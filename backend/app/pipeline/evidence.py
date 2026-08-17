"""Stage 7 — attach evidence / citations to the final answer."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.pipeline.chunking import infer_section_title
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
        title = infer_section_title(chunk.text, chunk.section_title)
        citations.append(
            Citation(
                source=chunk.source,
                excerpt=chunk.text[:excerpt_chars].strip(),
                score=chunk.score,
                chunk_index=chunk.chunk_index,
                page=chunk.page,
                section_number=chunk.section_number,
                section_title=title,
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


def format_evidence_header(
    *,
    score: float,
    source: str,
    chunk_index: int,
    page: int | None,
    section_number: str | None,
    section_title: str | None,
) -> str:
    """Single-line evidence header with explicit section_title (always shown)."""
    page_bit = f"p.{page}" if page is not None else "p=—"
    sec_n = section_number or "—"
    sec_t = section_title or "—"
    return (
        f"score={score:.3f}  source={source}  chunk={chunk_index}  "
        f"{page_bit}  section_number={sec_n}  section_title={sec_t}"
    )


def format_evidence_block(citations: list[Citation]) -> str:
    if not citations:
        return "(no evidence)"
    lines: list[str] = []
    for i, cite in enumerate(citations, start=1):
        header = format_evidence_header(
            score=cite.score,
            source=cite.source,
            chunk_index=cite.chunk_index,
            page=cite.page,
            section_number=cite.section_number,
            section_title=cite.section_title,
        )
        lines.append(f"[{i}] {header}\n    {cite.excerpt}")
    return "\n".join(lines)
