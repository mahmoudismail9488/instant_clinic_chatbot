"""Stage 2 — split text into overlapping chunks with page/section metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass

from backend.app.pipeline.source_loader import PageUnit

# Markdown: "# …", "## Prediabetes and Type 2 Diabetes"
_MD_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# Dotted section numbers: "2.1 Screening…", "4.2.3 Title"
_DOTTED_SECTION = re.compile(r"^((?:\d+\.)+\d+)\s+([A-Z].{2,140})$")
# Explicit labels: "Chapter 4 Screening…", "Section 3.2: Title"
_SECTION_LABEL = re.compile(
    r"^(?:Section|CHAPTER|Chapter|Part)\s+(\d+[A-Za-z0-9.]*)(?:\s*[:.\-–—]\s*|\s+)(.+)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Chunk:
    text: str
    index: int
    source: str
    source_path: str
    page: int | None = None
    section_number: str | None = None
    section_title: str | None = None


@dataclass(frozen=True)
class _Section:
    number: str | None = None
    title: str | None = None


def _parse_heading(line: str) -> _Section | None:
    raw = line.strip()
    if not raw or len(raw) > 180:
        return None

    md = _MD_HEADING.match(raw)
    if md:
        title = md.group(2).strip()
        # "# 2. Diagnosis and Classification…"
        dotted = re.match(r"^((?:\d+\.)+\d*|\d+)\.?\s+(.+)$", title)
        if dotted:
            return _Section(number=dotted.group(1), title=dotted.group(2).strip())
        return _Section(title=title)

    labeled = _SECTION_LABEL.match(raw)
    if labeled:
        return _Section(number=labeled.group(1), title=labeled.group(2).strip())

    dotted = _DOTTED_SECTION.match(raw)
    if dotted and not raw.endswith(","):
        return _Section(number=dotted.group(1), title=dotted.group(2).strip())

    return None


def chunk_units(
    units: list[PageUnit],
    *,
    source: str,
    source_path: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[Chunk]:
    """Chunk page-aware units, attaching the nearest section heading to each chunk."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be in [0, chunk_size)")

    chunks: list[Chunk] = []
    index = 0
    section = _Section()
    buffer: list[str] = []
    buffer_len = 0
    buffer_page: int | None = None
    buffer_section = _Section()

    def current_len() -> int:
        return buffer_len + max(0, len(buffer) - 1)

    def emit(text: str, page: int | None, sec: _Section) -> None:
        nonlocal index
        cleaned = " ".join(text.split()).strip()
        if not cleaned:
            return
        chunks.append(
            Chunk(
                text=cleaned,
                index=index,
                source=source,
                source_path=source_path,
                page=page,
                section_number=sec.number,
                section_title=sec.title,
            )
        )
        index += 1

    def flush(*, keep_overlap: bool) -> None:
        nonlocal buffer, buffer_len, buffer_page, buffer_section
        if not buffer:
            return
        text = " ".join(buffer)
        emit(text, buffer_page, buffer_section)
        if keep_overlap and overlap and len(text) > overlap:
            tail = text[-overlap:]
            buffer = [tail]
            buffer_len = len(tail)
        else:
            buffer = []
            buffer_len = 0
            buffer_page = None

    for unit in units:
        for line in unit.text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            heading = _parse_heading(stripped)
            if heading is not None:
                if buffer and current_len() >= 120:
                    flush(keep_overlap=False)
                section = heading

            if not buffer:
                buffer_page = unit.page
                buffer_section = section
            elif buffer_page is None and unit.page is not None:
                buffer_page = unit.page

            if heading is not None:
                buffer_section = section

            buffer.append(stripped)
            buffer_len += len(stripped)

            if current_len() >= chunk_size:
                flush(keep_overlap=True)
                buffer_section = section
                if buffer_page is None:
                    buffer_page = unit.page

    flush(keep_overlap=False)
    return chunks


def chunk_text(
    text: str,
    *,
    source: str,
    source_path: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[Chunk]:
    """Chunk flat text, honoring optional `[page N]` markers."""
    units: list[PageUnit] = []
    page_splits = re.split(r"\[page\s+(\d+)\]\s*", text)
    if len(page_splits) == 1:
        units = [PageUnit(text=text, page=None)]
    else:
        preamble = page_splits[0].strip()
        if preamble:
            units.append(PageUnit(text=preamble, page=None))
        for i in range(1, len(page_splits), 2):
            page_num = int(page_splits[i])
            body = page_splits[i + 1] if i + 1 < len(page_splits) else ""
            if body.strip():
                units.append(PageUnit(text=body, page=page_num))
    return chunk_units(
        units,
        source=source,
        source_path=source_path,
        chunk_size=chunk_size,
        overlap=overlap,
    )
