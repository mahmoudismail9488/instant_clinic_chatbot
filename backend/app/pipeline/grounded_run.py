"""Day 3 — the grounded answer flow (slide 28).

Runs alongside `run.run_query` rather than replacing it: the Day 2 path (`clinic query`)
is untouched and still behaves exactly as before. This module reads from the existing
pipeline via `retrieve()` and adds the answer layer on top.

Decision flow, in slide 28's order — a NO exits early and later checks are skipped:

     1. clinical question received
     2. patient-specific?                      -> yes -> safety refusal (before retrieval)
     4. retrieve top-k chunks
    5-6. evidence relevant & score ok?         -> no  -> insufficient evidence
    7-8. build context, generate structured answer
    9-10. citation coverage & correctness ok?  -> no  -> refuse
    12. grounded answer returned
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from backend.app.config import Settings, get_settings
from backend.app.pipeline.answer_schema import (
    AnswerStatus,
    CitationReport,
    ConfidenceLevel,
    GroundedAnswer,
    final_confidence,
    refusal,
    validate_citations,
)
from backend.app.pipeline.claim_support import (
    ClaimSupportReport,
    check_unsupported_claims,
    is_claim_supported,
)
from backend.app.pipeline.grounding import (
    DAY3_SYSTEM_PROMPT,
    build_grounded_context,
    build_user_message,
)
from backend.app.pipeline.guardrails import GuardrailResult, check_answer, check_query
from backend.app.pipeline.retrieval import RetrievedChunk, retrieve
from backend.app.pipeline.risk_classification import (
    RiskAction,
    RiskVerdict,
    classify_input_risk,
    refusal_text_for,
)
from backend.app.pipeline.safety import SafetyVerdict, check_patient_specific
from backend.app.services.llm_client import LLMClient, StructuredResult
from backend.app.services.vector_store import VectorStore

# Slide 26: the threshold is not universal and must be chosen by testing, not guessed.
# It applies to the existing retriever's fused rank score, NOT a cosine similarity, so
# slide 26's example numbers (0.84 / 0.52 / 0.18) do not transfer.
#
# Calibrated 2026-08-18 via `clinic calibrate`. Finding: supported and out-of-scope
# questions OVERLAP on this score — off-topic "treatment for melanoma" scored 0.105,
# above on-topic "HbA1c threshold" at 0.103 — so no cutoff separates them. The threshold
# therefore cannot do topic filtering; grounding rule 5 does that. Its only job is to trim
# the weakest tail, so it is set low: at 0.02 it admitted 1 of 5 chunks and starved
# answers of corroborating evidence.
DEFAULT_EVIDENCE_THRESHOLD = 0.015
MIN_CHUNKS_ABOVE_THRESHOLD = 1

INSUFFICIENT_EVIDENCE_TEXT = (
    "The retrieved guideline text does not provide sufficient evidence to answer this "
    "question reliably."
)


def evidence_threshold() -> float:
    """Threshold, overridable by env without editing config.py."""
    raw = os.environ.get("DAY3_EVIDENCE_THRESHOLD")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return DEFAULT_EVIDENCE_THRESHOLD


@dataclass(frozen=True)
class GroundedResult:
    """Everything lab step 12 asks you to document for a single question."""

    question: str
    answer: GroundedAnswer
    threshold: float
    retrieved: list[RetrievedChunk] = field(default_factory=list)
    used: list[RetrievedChunk] = field(default_factory=list)
    report: CitationReport | None = None
    claim_support: ClaimSupportReport | None = None
    safety: SafetyVerdict | None = None
    risk: RiskVerdict | None = None
    guardrail: GuardrailResult | None = None
    structured: StructuredResult | None = None
    decision_path: tuple[str, ...] = ()
    # The model's original answer when rejected at flow steps 9-10. Kept so the failure
    # can be inspected — lab step 13 wants a recorded generation failure, and discarding
    # the rejected output would destroy the only evidence of it.
    rejected_answer: GroundedAnswer | None = None

    @property
    def status(self) -> AnswerStatus:
        return self.answer.status

    @property
    def confidence(self) -> ConfidenceLevel:
        return self.answer.confidence

    @property
    def accepted(self) -> bool:
        return self.answer.status is AnswerStatus.ANSWERED


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def dedupe_chunks(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    """Drop repeated text, keeping the highest-ranked copy.

    The index stores some passages many times over: the Diabetes Canada quick-reference is
    a foldout whose panels repeat the same text, so 471 stored chunks hold only 349
    distinct passages. Retrieval is not changed here; duplicates are dropped at the point
    of use. This matters beyond tidiness — slide 27 counts *agreement between retrieved
    chunks* toward confidence, and seven copies of one passage must not read as seven
    independent sources agreeing.
    """
    seen: set[str] = set()
    unique: list[RetrievedChunk] = []
    for chunk in chunks:
        key = _normalize(chunk.text)
        if key and key not in seen:
            seen.add(key)
            unique.append(chunk)
    return unique


def answer_question(
    question: str,
    *,
    top_k: int | None = None,
    threshold: float | None = None,
    settings: Settings | None = None,
    store: VectorStore | None = None,
    client: LLMClient | None = None,
    section_focus: str | None = None,
) -> GroundedResult:
    """Run one clinical question through the full Day 3 decision flow."""
    cfg = settings or get_settings()
    cutoff = evidence_threshold() if threshold is None else threshold
    k = top_k or cfg.default_top_k
    asked = (question or "").strip()
    path: list[str] = ["1. question received"]

    if not asked:
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                "No question was provided.",
                missing_information=["A clinical question is required."],
            ),
            threshold=cutoff,
            decision_path=tuple(path + ["empty question"]),
        )

    # --- Day 4 input risk classification (before retrieval) -------------------------
    risk = classify_input_risk(asked)
    path.append(f"1a. risk={risk.category.value}/{risk.level.value}")
    if risk.action is not RiskAction.CONTINUE:
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.SAFETY_REFUSAL,
                refusal_text_for(risk),
                missing_information=[risk.reason],
            ),
            threshold=cutoff,
            risk=risk,
            decision_path=tuple(
                path + [f"-> risk {risk.action.value} ({risk.category.value})"]
            ),
        )

    # Defense in depth: legacy Stage 5 phrase lists + patient-specific regexes.
    query_guard = check_query(asked)
    path.append("1b. query guardrails")
    if not query_guard.allowed:
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.SAFETY_REFUSAL,
                query_guard.reason or "Request blocked by guardrails.",
                missing_information=[
                    "This assistant does not provide prescriptions, dosages, or "
                    "personalized medication advice."
                ],
            ),
            threshold=cutoff,
            risk=risk,
            guardrail=query_guard,
            decision_path=tuple(path + [f"-> guardrail refusal ({query_guard.reason})"]),
        )

    verdict = check_patient_specific(asked)
    path.append("2. patient-specific check")
    if verdict.patient_specific:
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.SAFETY_REFUSAL,
                refusal_text_for(risk)
                if risk.action is not RiskAction.CONTINUE
                else (
                    "I cannot provide a patient-specific diagnosis, prescription, dosage, "
                    "or treatment selection. Please consult a qualified clinician."
                ),
                missing_information=[
                    "A qualified clinician must assess the individual case."
                ],
            ),
            threshold=cutoff,
            risk=risk,
            safety=verdict,
            guardrail=query_guard,
            decision_path=tuple(path + [f"-> safety refusal ({verdict.reason})"]),
        )

    # --- flow step 4: retrieve --------------------------------------------------------
    # The raw question is used, not a rewrite: slide 14 specifies {question} untouched.
    # Hybrid dense+BM25 RRF, optionally re-ranked by section_focus chips.
    llm = client or LLMClient(cfg)
    retrieved = retrieve(
        asked,
        top_k=k,
        store=store,
        client=llm,
        section_focus=section_focus,
    )
    focus_note = f", focus={section_focus}" if section_focus else ""
    path.append(f"4. retrieved {len(retrieved)} chunks (hybrid{focus_note})")

    unique = dedupe_chunks(retrieved)
    if len(unique) != len(retrieved):
        path.append(f"   deduplicated to {len(unique)} distinct chunks")

    # --- flow steps 5-6: is the evidence strong enough to use? ------------------------
    usable = [c for c in unique if c.score >= cutoff]
    path.append(f"5-6. {len(usable)} chunk(s) at or above threshold {cutoff:g}")
    if len(usable) < MIN_CHUNKS_ABOVE_THRESHOLD:
        best = max((c.score for c in unique), default=0.0)
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                INSUFFICIENT_EVIDENCE_TEXT,
                missing_information=[
                    f"No retrieved passage reached the minimum evidence score "
                    f"(best was {best:.3f}, threshold {cutoff:g}).",
                    "A guideline section addressing this question directly is required.",
                ],
            ),
            threshold=cutoff,
            retrieved=retrieved,
            risk=risk,
            safety=verdict,
            guardrail=query_guard,
            decision_path=tuple(path + ["-> insufficient evidence"]),
        )

    # --- flow steps 7-8: build context and generate ----------------------------------
    structured = llm.generate_structured(
        system=DAY3_SYSTEM_PROMPT,
        user=build_user_message(asked, build_grounded_context(usable)),
    )
    path.append(f"7-8. generation ({structured.attempts} attempt(s))")

    if not structured.ok or structured.answer is None:
        # Fail closed: an unparseable model response is never shown as an answer.
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                INSUFFICIENT_EVIDENCE_TEXT,
                missing_information=[
                    "The answer could not be produced in a verifiable structured form."
                ],
            ),
            threshold=cutoff,
            retrieved=retrieved,
            used=usable,
            risk=risk,
            safety=verdict,
            guardrail=query_guard,
            structured=structured,
            decision_path=tuple(path + ["-> generation failed, refused"]),
        )

    answer = structured.answer

    # The model may refuse on its own (rules 5 and 6). Respect it and stop.
    if answer.status is not AnswerStatus.ANSWERED:
        return GroundedResult(
            question=asked,
            answer=answer,
            threshold=cutoff,
            retrieved=retrieved,
            used=usable,
            risk=risk,
            safety=verdict,
            guardrail=query_guard,
            structured=structured,
            decision_path=tuple(path + [f"-> model returned {answer.status.value}"]),
        )

    # --- stage 5 answer guardrails (block prescribing language in drafts) ------------
    answer_guard = check_answer(answer.recommendation)
    path.append("8b. answer guardrails")
    if not answer_guard.allowed:
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.SAFETY_REFUSAL,
                answer_guard.reason or "Answer blocked by guardrails.",
                missing_information=[
                    "Generated text looked like a prescription or dosing instruction."
                ],
            ),
            threshold=cutoff,
            retrieved=retrieved,
            used=usable,
            risk=risk,
            safety=verdict,
            guardrail=answer_guard,
            structured=structured,
            rejected_answer=answer,
            decision_path=tuple(path + ["-> answer guardrail refusal"]),
        )

    # --- flow steps 9-10: citation coverage and correctness --------------------------
    report = validate_citations(answer, usable)
    path.append(
        f"9-10. coverage {report.coverage:.0%}, "
        f"{len(report.invented_citations)} invented"
    )

    if not report.passed:
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                INSUFFICIENT_EVIDENCE_TEXT,
                missing_information=[
                    f"The generated answer failed citation validation: "
                    f"{report.failure_summary()}."
                ],
            ),
            threshold=cutoff,
            retrieved=retrieved,
            used=usable,
            report=report,
            risk=risk,
            safety=verdict,
            guardrail=query_guard,
            structured=structured,
            rejected_answer=answer,
            decision_path=tuple(path + ["-> citation validation failed, refused"]),
        )

    # --- Day 4 unsupported-claim heuristic (second safety net) ------------------------
    evidence_blob = "\n".join(c.text for c in usable)
    claim_texts = [item.claim for item in answer.supporting_evidence]
    if claim_texts:
        unsupported = tuple(
            c for c in claim_texts if not is_claim_supported(c, evidence_blob)
        )
        claim_report = ClaimSupportReport(
            claims=tuple(claim_texts), unsupported=unsupported
        )
    else:
        claim_report = check_unsupported_claims(answer.recommendation, evidence_blob)
    path.append(
        f"11. claim support faithfulness={claim_report.faithfulness:.0%}, "
        f"unsupported={len(claim_report.unsupported)}"
    )
    if not claim_report.passed:
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.INSUFFICIENT_EVIDENCE,
                INSUFFICIENT_EVIDENCE_TEXT,
                missing_information=[
                    "Post-generation claim support check flagged unsupported claim(s):",
                    *[f"- {c}" for c in claim_report.unsupported[:3]],
                ],
            ),
            threshold=cutoff,
            retrieved=retrieved,
            used=usable,
            report=report,
            claim_support=claim_report,
            risk=risk,
            safety=verdict,
            guardrail=query_guard,
            structured=structured,
            rejected_answer=answer,
            decision_path=tuple(path + ["-> unsupported claims, refused"]),
        )

    # --- flow step 12: grounded answer, confidence derived from evidence -------------
    answer.confidence = final_confidence(
        answer.confidence, usable, report, threshold=cutoff
    )
    path.append(f"12. answered, confidence {answer.confidence.value}")

    return GroundedResult(
        question=asked,
        answer=answer,
        threshold=cutoff,
        retrieved=retrieved,
        used=usable,
        report=report,
        claim_support=claim_report,
        risk=risk,
        safety=verdict,
        guardrail=query_guard,
        structured=structured,
        decision_path=tuple(path),
    )
