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


def _refusal_reason(result: GroundedResult) -> str:
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
    )


def grounded_result_to_response(result: GroundedResult) -> QueryResponse:
    turn_id = f"t-{uuid.uuid4().hex[:10]}"
    answer = result.answer

    used_ids = {store_id(c) for c in result.used}
    # Prefer used chunks for the evidence panel; fall back to retrieved.
    source_chunks = result.used or result.retrieved
    chunks_out = [_chunk_out(c, used=(store_id(c) in used_ids or not used_ids)) for c in source_chunks]

    by_ref = {chunk_ref(c).upper(): c for c in source_chunks}
    citations_out: list[CitationOut] = []
    evidence: list[dict] = []

    for item in answer.supporting_evidence:
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

    guard = None
    if result.safety and result.safety.patient_specific:
        guard = GuardrailOut(allowed=False, reason=result.safety.reason)
    elif answer.status is not AnswerStatus.ANSWERED:
        guard = GuardrailOut(allowed=False, reason=answer.status.value)

    if answer.status is not AnswerStatus.ANSWERED:
        return QueryResponse(
            kind="refusal",
            id=turn_id,
            question=result.question,
            recommendation=answer.recommendation,
            detail=answer.recommendation,
            reason=_refusal_reason(result),
            confidence=_ui_confidence(answer.confidence),
            evidence=evidence,
            chunks=chunks_out,
            citations=citations_out,
            guardrail=guard,
            blocked=True,
            status=answer.status.value,
            safety_note=answer.safety_note,
            missing_information=list(answer.missing_information),
            decision_path=list(result.decision_path),
        )

    return QueryResponse(
        kind="answer",
        id=turn_id,
        question=result.question,
        recommendation=answer.recommendation,
        caution=None,
        confidence=_ui_confidence(answer.confidence),
        evidence=evidence,
        chunks=chunks_out,
        citations=citations_out,
        guardrail=GuardrailOut(allowed=True, reason=None),
        blocked=False,
        status=answer.status.value,
        safety_note=answer.safety_note,
        missing_information=list(answer.missing_information),
        decision_path=list(result.decision_path),
    )
