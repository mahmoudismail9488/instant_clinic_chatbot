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
from backend.app.pipeline.grounding import (
    DAY3_SYSTEM_PROMPT,
    build_grounded_context,
    build_user_message,
)
from backend.app.pipeline.retrieval import RetrievedChunk, retrieve
from backend.app.pipeline.safety import (
    SAFETY_REFUSAL_TEXT,
    SafetyVerdict,
    check_patient_specific,
)
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
    safety: SafetyVerdict | None = None
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

    # --- flow step 2: patient-specific check, BEFORE retrieval -----------------------
    verdict = check_patient_specific(asked)
    path.append("2. patient-specific check")
    if verdict.patient_specific:
        return GroundedResult(
            question=asked,
            answer=refusal(
                AnswerStatus.SAFETY_REFUSAL,
                SAFETY_REFUSAL_TEXT,
                missing_information=[
                    "A qualified clinician must assess the individual case."
                ],
            ),
            threshold=cutoff,
            safety=verdict,
            decision_path=tuple(path + [f"-> safety refusal ({verdict.reason})"]),
        )

    # --- flow step 4: retrieve --------------------------------------------------------
    # The raw question is used, not a rewrite: slide 14 specifies {question} untouched.
    llm = client or LLMClient(cfg)
    retrieved = retrieve(asked, top_k=k, store=store, client=llm)
    path.append(f"4. retrieved {len(retrieved)} chunks")

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
            safety=verdict,
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
            safety=verdict,
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
            safety=verdict,
            structured=structured,
            decision_path=tuple(path + [f"-> model returned {answer.status.value}"]),
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
            safety=verdict,
            structured=structured,
            rejected_answer=answer,
            decision_path=tuple(path + ["-> citation validation failed, refused"]),
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
        safety=verdict,
        structured=structured,
        decision_path=tuple(path),
    )
