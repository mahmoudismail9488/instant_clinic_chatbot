"""Map grounded Day-3 pipeline results → API / frontend response."""

from __future__ import annotations

import uuid

from backend.app.models.schemas import (
    ChunkOut,
    CitationOut,
    GuardrailOut,
    QueryResponse,
)
from backend.app.pipeline.answer_schema import (
    AnswerStatus,
    ConfidenceLevel,
    chunk_ref,
    store_id,
)
from backend.app.pipeline.evidence import format_location
from backend.app.pipeline.grounded_run import GroundedResult
from backend.app.pipeline.retrieval import RetrievedChunk


def _section(number: str | None, title: str | None) -> str:
    return format_location(None, number, title) or (title or number or "")


def _ui_confidence(level: ConfidenceLevel) -> str:
    mapping = {
        ConfidenceLevel.HIGH: "high",
        ConfidenceLevel.MEDIUM: "medium",
        ConfidenceLevel.LOW: "low",
        ConfidenceLevel.INSUFFICIENT: "insufficient",
    }
    return mapping.get(level, "medium")


def _confidence_score(
    level: ConfidenceLevel,
    chunks: list[RetrievedChunk],
    *,
    coverage: float | None = None,
) -> float:
    """Transparent 0–1 evidence score paired with the Low/Med/High label.

    Combines the closed-set confidence band with retrieval strength and citation
    coverage. Not a clinically validated probability — an evidence-quality index.
    """
    band = {
        ConfidenceLevel.HIGH: 0.88,
        ConfidenceLevel.MEDIUM: 0.68,
        ConfidenceLevel.LOW: 0.42,
        ConfidenceLevel.INSUFFICIENT: 0.0,
    }.get(level, 0.5)
    if level is ConfidenceLevel.INSUFFICIENT or not chunks:
        return 0.0

    scores = [float(c.score) for c in chunks]
    top = max(scores)
    mean = sum(scores) / len(scores)
    # Fused RRF scores are often << 1; dense cosine may already be in [0, 1].
    if top <= 0.35:
        retrieval = min(1.0, (0.65 * top + 0.35 * mean) / 0.12)
    else:
        retrieval = min(1.0, 0.6 * top + 0.4 * mean)
    cov = 1.0 if coverage is None else max(0.0, min(1.0, coverage))
    score = 0.55 * band + 0.35 * retrieval + 0.10 * cov
    return round(max(0.0, min(1.0, score)), 2)

def _refusal_reason(result: GroundedResult) -> str:
    if result.risk and result.risk.action.value == "emergency_redirect":
        return "Emergency — seek immediate care"
    if result.risk and result.risk.category.value == "adversarial":
        return "Out of scope"
    if result.risk and result.risk.action.value == "clarify":
        return "Out of scope"
    if result.guardrail and not result.guardrail.allowed:
        text = (result.guardrail.reason or "").lower()
        if "emergency" in text or "overdose" in text:
            return "Emergency — seek immediate care"
        if "medication" in text or "prescription" in text or "prescrib" in text or "dosage" in text:
            return "Medication request — consult a clinician"
        if "empty" in text:
            return "Out of scope"
        return "Out of scope"
    if result.risk and result.risk.category.value in {
        "medication_dosage",
        "diagnosis_request",
        "patient_specific",
    }:
        if result.risk.category.value == "medication_dosage":
            return "Medication request — consult a clinician"
        return "Patient-specific — seek clinical care"
    if result.answer.status is AnswerStatus.SAFETY_REFUSAL:
        return "Patient-specific — seek clinical care"
    if result.safety and result.safety.patient_specific:
        return "Patient-specific — seek clinical care"
    return "Insufficient retrieval confidence"


def _chunk_out(ch: RetrievedChunk, *, used: bool) -> ChunkOut:
    section = _section(ch.section_number, ch.section_title)
    return ChunkOut(
        id=store_id(ch),
        doc=ch.source,
        page=ch.page,
        section=section,
        section_number=ch.section_number,
        section_title=ch.section_title,
        score=round(ch.score, 4),
        excerpt=(ch.text[:280] + "…") if len(ch.text) > 280 else ch.text,
        text=ch.text,
        used=used,
        source=ch.source,
        source_path=ch.source_path,
        chunk_id=store_id(ch),
        chunk_index=ch.chunk_index,
    )


def grounded_result_to_response(result: GroundedResult) -> QueryResponse:
    turn_id = f"t-{uuid.uuid4().hex[:10]}"
    answer = result.answer

    used_ids = {store_id(c) for c in result.used}
    # Prefer used chunks for the evidence panel; fall back to retrieved.
    source_chunks = result.used or result.retrieved
    chunks_out = [
        _chunk_out(c, used=(store_id(c) in used_ids or not used_ids))
        for c in source_chunks
    ]

    by_ref = {chunk_ref(c).upper(): c for c in source_chunks}
    citations_out: list[CitationOut] = []
    evidence: list[dict] = []
    supporting: list[dict] = []

    for item in answer.supporting_evidence:
        supporting.append(
            {
                "claim": item.claim,
                "citations": [c.model_dump() for c in item.citations],
            }
        )
        for citation in item.citations:
            ref = citation.chunk.strip().upper()
            chunk = by_ref.get(ref)
            page = citation.page if citation.page is not None else (chunk.page if chunk else None)
            section = citation.section or (
                _section(chunk.section_number, chunk.section_title) if chunk else "—"
            )
            chunk_id = store_id(chunk) if chunk else f"{citation.document}::{citation.chunk}"
            citations_out.append(
                CitationOut(
                    doc=citation.document,
                    page=page,
                    section=section or "—",
                    chunk_id=chunk_id,
                    excerpt=item.claim,
                    score=round(chunk.score, 4) if chunk else 0.0,
                    claim=item.claim,
                )
            )
            evidence.append(
                {
                    "text": item.claim,
                    "citation": {
                        "doc": citation.document,
                        "page": page or 0,
                        "section": section or "—",
                        "chunkId": chunk_id,
                    },
                }
            )

    # Mark cited chunks as used in the panel.
    cited = {c.chunk_id for c in citations_out}
    for ch in chunks_out:
        if cited:
            ch.used = ch.id in cited

    if result.guardrail is not None and not result.guardrail.allowed:
        guard = GuardrailOut(
            allowed=result.guardrail.allowed,
            reason=result.guardrail.reason,
        )
    elif result.risk is not None and result.risk.action.value != "continue":
        guard = GuardrailOut(allowed=False, reason=result.risk.reason)
    elif result.safety and result.safety.patient_specific:
        guard = GuardrailOut(allowed=False, reason=result.safety.reason)
    elif answer.status is not AnswerStatus.ANSWERED:
        guard = GuardrailOut(allowed=False, reason=answer.status.value)
    else:
        guard = GuardrailOut(allowed=True, reason=None)

    next_action = "Consult a clinician to apply this to an individual patient."
    if result.risk and result.risk.action.value == "emergency_redirect":
        next_action = "Call emergency services immediately (112 / 911 / local equivalent)."
    elif result.risk and result.risk.action.value == "clarify":
        next_action = "Rephrase as a specific guideline question (population, test, or recommendation)."
    elif result.risk and result.risk.category.value == "adversarial":
        next_action = "Ask a guideline question without requesting that evidence be ignored."
    elif answer.status is AnswerStatus.SAFETY_REFUSAL:
        next_action = "Speak with a qualified clinician; do not use this tool for personal treatment decisions."
    elif answer.status is AnswerStatus.INSUFFICIENT_EVIDENCE:
        next_action = "Try a more specific guideline question, or consult a clinician."
    risk_payload = None
    if result.risk is not None:
        risk_payload = {
            "category": result.risk.category.value,
            "level": result.risk.level.value,
            "action": result.risk.action.value,
            "reason": result.risk.reason,
        }

    claim_payload = None
    if result.claim_support is not None:
        claim_payload = {
            "total_claims": result.claim_support.total_claims,
            "unsupported": list(result.claim_support.unsupported),
            "faithfulness": round(result.claim_support.faithfulness, 3),
            "unsupported_claim_rate": round(
                result.claim_support.unsupported_claim_rate, 3
            ),
        }

    if answer.status is not AnswerStatus.ANSWERED:
        score = _confidence_score(
            answer.confidence,
            source_chunks,
            coverage=result.report.coverage if result.report else 0.0,
        )
        return QueryResponse(
            kind="refusal",
            id=turn_id,
            question=result.question,
            recommendation=answer.recommendation,
            detail=answer.recommendation,
            reason=_refusal_reason(result),
            confidence=_ui_confidence(answer.confidence),
            confidence_score=score,
            evidence=evidence,
            supporting_evidence=supporting,
            chunks=chunks_out,
            citations=citations_out,
            guardrail=guard,
            blocked=True,
            status=answer.status.value,
            safety_note=answer.safety_note,
            missing_information=list(answer.missing_information),
            decision_path=list(result.decision_path),
            risk=risk_payload,
            claim_support=claim_payload,
            next_action=next_action,
        )

    score = _confidence_score(
        answer.confidence,
        source_chunks,
        coverage=result.report.coverage if result.report else 1.0,
    )
    return QueryResponse(
        kind="answer",
        id=turn_id,
        question=result.question,
        recommendation=answer.recommendation,
        caution=None,
        confidence=_ui_confidence(answer.confidence),
        confidence_score=score,
        evidence=evidence,
        supporting_evidence=supporting,
        chunks=chunks_out,
        citations=citations_out,
        guardrail=guard,
        blocked=False,
        status=answer.status.value,
        safety_note=answer.safety_note,
        missing_information=list(answer.missing_information),
        decision_path=list(result.decision_path),
        risk=risk_payload,
        claim_support=claim_payload,
        next_action=next_action,
    )
