"""Map pipeline QueryResult → API / frontend-friendly response."""

from __future__ import annotations

import uuid

from backend.app.models.schemas import (
    ChunkOut,
    CitationOut,
    ConflictOut,
    GuardrailOut,
    QueryResponse,
)
from backend.app.pipeline.evidence import format_location
from backend.app.pipeline.run import QueryResult


def _section(number: str | None, title: str | None) -> str:
    return format_location(None, number, title) or (title or number or "")

# Owner of search must change this
def _confidence(scores: list[float], *, blocked: bool, empty: bool) -> str:
    if blocked or empty:
        return "insufficient"
    if not scores:
        return "insufficient"
    top = max(scores)
    # Cosine scores vary by embedding stack; keep a soft ladder and avoid
    # marking successful retrievals as "insufficient" solely due to scale.
    if top >= 0.7:
        return "high"
    if top >= 0.45:
        return "medium"
    if top >= 0.2:
        return "low"
    return "low"


def _refusal_reason(guard_reason: str | None) -> str:
    text = (guard_reason or "").lower()
    if "emergency" in text or "chest pain" in text or "overdose" in text:
        return "Emergency — seek immediate care"
    if "empty" in text or "blocked" in text:
        return "Out of scope"
    return "Out of scope"


def query_result_to_response(result: QueryResult) -> QueryResponse:
    turn_id = f"t-{uuid.uuid4().hex[:10]}"
    cited_ids = {
        f"{c.source}::{c.chunk_index}" for c in result.citations
    }

    chunks_out: list[ChunkOut] = []
    for ch in result.chunks:
        cid = f"{ch.source}::{ch.chunk_index}"
        section = _section(ch.section_number, ch.section_title)
        chunks_out.append(
            ChunkOut(
                id=cid,
                doc=ch.source,
                page=ch.page,
                section=section,
                section_number=ch.section_number,
                section_title=ch.section_title,
                score=round(ch.score, 4),
                excerpt=(ch.text[:280] + "…") if len(ch.text) > 280 else ch.text,
                text=ch.text,
                used=cid in cited_ids if cited_ids else True,
            )
        )

    citations_out = [
        CitationOut(
            doc=c.source,
            page=c.page,
            section=_section(c.section_number, c.section_title),
            chunk_id=f"{c.source}::{c.chunk_index}",
            excerpt=c.excerpt,
            score=round(c.score, 4),
        )
        for c in result.citations
    ]

    evidence = [
        {
            "text": c.excerpt,
            "citation": {
                "doc": c.doc,
                "page": c.page or 0,
                "section": c.section or "—",
                "chunkId": c.chunk_id,
            },
        }
        for c in citations_out
    ]

    scores = [c.score for c in result.chunks]
    confidence = _confidence(scores, blocked=result.blocked, empty=not result.chunks)
    guard = (
        GuardrailOut(allowed=result.guardrail.allowed, reason=result.guardrail.reason)
        if result.guardrail
        else None
    )
    conflict = (
        ConflictOut(
            has_conflict=result.conflict.has_conflict,
            summary=result.conflict.summary,
            sources=list(result.conflict.sources),
        )
        if result.conflict
        else None
    )

    if result.blocked:
        reason = _refusal_reason(result.guardrail.reason if result.guardrail else None)
        return QueryResponse(
            kind="refusal",
            id=turn_id,
            question=result.original_query,
            rewritten_query=result.rewritten_query,
            detail=result.answer,
            reason=reason,
            confidence="insufficient",
            chunks=chunks_out,
            citations=citations_out,
            evidence=evidence,
            conflict=conflict,
            guardrail=guard,
            blocked=True,
        )

    if not result.chunks:
        return QueryResponse(
            kind="refusal",
            id=turn_id,
            question=result.original_query,
            rewritten_query=result.rewritten_query,
            detail="No guideline chunks were retrieved for this question.",
            reason="Insufficient retrieval confidence",
            confidence="insufficient",
            chunks=[],
            citations=[],
            evidence=[],
            conflict=conflict,
            guardrail=guard,
            blocked=True,
        )

    caution = None
    if conflict and conflict.has_conflict:
        caution = conflict.summary or "Guideline sources may conflict — review evidence carefully."

    return QueryResponse(
        kind="answer",
        id=turn_id,
        question=result.original_query,
        rewritten_query=result.rewritten_query,
        recommendation=result.answer,
        caution=caution,
        confidence=confidence,
        evidence=evidence,
        chunks=chunks_out,
        citations=citations_out,
        conflict=conflict,
        guardrail=guard,
        blocked=False,
    )
