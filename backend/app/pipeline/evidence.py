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
    page: int | None = None
    section_number: str | None = None
    section_title: str | None = None


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
                page=chunk.page,
                section_number=chunk.section_number,
                section_title=chunk.section_title,
            )
        )
    return citations


def format_location(page: int | None, section_number: str | None, section_title: str | None) -> str:
    parts: list[str] = []
    if page is not None:
        parts.append(f"p.{page}")
    if section_number:
        parts.append(f"§{section_number}")
    if section_title:
        parts.append(section_title)
    return " | ".join(parts) if parts else ""


def format_evidence_block(citations: list[Citation]) -> str:
    if not citations:
        return "(no evidence)"
    lines: list[str] = []
    for i, cite in enumerate(citations, start=1):
        loc = format_location(cite.page, cite.section_number, cite.section_title)
        loc_bit = f"  {loc}" if loc else ""
        lines.append(
            f"[{i}] {cite.source}  chunk={cite.chunk_index}  score={cite.score:.3f}{loc_bit}\n"
            f"    {cite.excerpt}"
        )
    return "\n".join(lines)
