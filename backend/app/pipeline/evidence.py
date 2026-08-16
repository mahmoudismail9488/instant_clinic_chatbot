"""Stage 7 — attach evidence / citations to the final answer."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.pipeline.retrieval import RetrievedChunk


@dataclass(frozen=True)
class Citation:
    source: str
    excerpt: str
    score: float
    chunk_index: int


def build_citations(
    chunks: list[RetrievedChunk],
    *,
    max_citations: int = 5,
    excerpt_chars: int = 280,
) -> list[Citation]:
    citations: list[Citation] = []
    for chunk in chunks[:max_citations]:
        citations.append(
            Citation(
                source=chunk.source,
                excerpt=chunk.text[:excerpt_chars].strip(),
                score=chunk.score,
                chunk_index=chunk.chunk_index,
            )
        )
    return citations


def format_evidence_block(citations: list[Citation]) -> str:
    if not citations:
        return "(no evidence)"
    lines: list[str] = []
    for i, cite in enumerate(citations, start=1):
        lines.append(
            f"[{i}] {cite.source}  chunk={cite.chunk_index}  score={cite.score:.3f}\n"
            f"    {cite.excerpt}"
        )
    return "\n".join(lines)
