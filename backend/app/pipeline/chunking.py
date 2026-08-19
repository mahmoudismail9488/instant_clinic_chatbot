"""Stage 2 — split text into overlapping chunks with page/section metadata.

Section titles are recovered from:
  - Markdown / dotted NICE headings (1.5 …, 1.2.4 …)
  - Explicit Section/Chapter labels
  - Known diabetes guideline panel titles (including PDF line-breaks)
  - Short Title-Case / ALL-CAPS stand-alone heading lines
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from backend.app.pipeline.source_loader import PageUnit

# Markdown: "# …", "## Prediabetes and Type 2 Diabetes"
_MD_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# Dotted / NICE-style section: "1.5 HbA1c measurement…", "1.2 Structured education…"
_DOTTED_SECTION = re.compile(
    r"^((?:\d+\.)+\d+|\d+)\s+([A-Za-z][\w\s,/'()\-]{2,160})$"
)
# Recommendation bullets that still carry a section number: "1.2.4 Offer adults…"
_REC_NUMBER = re.compile(r"^((?:\d+\.){1,3}\d+)\s+([A-Za-z].{8,200})$")
# Explicit labels: "Chapter 4 Screening…", "Section 3.2: Title"
_SECTION_LABEL = re.compile(
    r"^(?:Section|CHAPTER|Chapter|Part)\s+(\d+[A-Za-z0-9.]*)(?:\s*[:.\-–—]\s*|\s+)(.+)$",
    re.IGNORECASE,
)
# ALL-CAPS heading line (guideline panel titles)
_ALL_CAPS = re.compile(r"^[A-Z0-9][A-Z0-9\s/&,\-]{3,80}$")
# Title Case short heading (no trailing period)
_TITLE_CASE = re.compile(
    r"^(?:[A-Z][a-z0-9]+(?:[\s/\-](?:[A-Z][a-z0-9]+|[a-z]{2,8})){0,8})$"
)

# Known section titles from Diabetes Canada QRG + common NICE panels
_KNOWN_SECTION_TITLES = (
    "Who to screen",
    "How to screen",
    "Screening of Type 2 Diabetes",
    "Diagnosis of Diabetes",
    "Diagnostic Tests for Diabetes",
    "Prediabetes and Type 2 Diabetes",
    "Classification",
    "Key Messages",
    "Recommendations",
    "Full Text",
    "ABCDESSS of diabetes care",
    "Individualised care",
    "Education",
    "Dietary advice and interventions",
    "Blood glucose management",
    "Person-centred medicine",
    "Initial medicines",
    "Using this guideline",
    "Contents",
)

_KNOWN_JOINED = {re.sub(r"\s+", " ", t).lower(): t for t in _KNOWN_SECTION_TITLES}

_SECTION_TITLE_ONLY = re.compile(
    r"^(" + "|".join(re.escape(t) for t in _KNOWN_SECTION_TITLES) + r")\s*$",
    re.IGNORECASE,
)
_INLINE_SECTION_TITLE = re.compile(
    r"(" + "|".join(re.escape(t) for t in _KNOWN_SECTION_TITLES) + r")",
    re.IGNORECASE,
)

# PDF artifacts: "UPDATED FOR 2025How to" → insert space before capital run
_GLUED_YEAR = re.compile(r"(20\d{2})([A-Z][a-z])")
_GLUED_WORD = re.compile(r"([a-z])([A-Z][a-z])")


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


def _normalize_line(line: str) -> str:
    text = (line or "").replace("\xa0", " ").replace("\uf094", " ")
    text = _GLUED_YEAR.sub(r"\1 \2", text)
    text = _GLUED_WORD.sub(r"\1 \2", text)
    return re.sub(r"\s+", " ", text).strip()


def _canonical_known(title: str) -> str | None:
    key = re.sub(r"\s+", " ", title).strip().lower()
    return _KNOWN_JOINED.get(key)


def _extract_embedded_known(line: str) -> str | None:
    """Recover a known title glued inside noisy PDF lines."""
    lower = re.sub(r"\s+", " ", line).strip().lower()
    for key, canon in sorted(_KNOWN_JOINED.items(), key=lambda kv: -len(kv[0])):
        if key in lower:
            return canon
    return None


def _looks_like_body(line: str) -> bool:
    if len(line) > 120:
        return True
    if line.endswith((".", ";", ":")) and len(line) > 60:
        return True
    if line.startswith(("•", "-", "*", "–", "—")):
        return True
    lower = line.lower()
    if lower.startswith(("the ", "this ", "offer ", "ensure ", "consider ", "if ")):
        return len(line) > 40
    return False


def _parse_heading(line: str) -> _Section | None:
    raw = _normalize_line(line)
    if not raw or len(raw) > 180 or _looks_like_body(raw):
        return None

    known = _canonical_known(raw) or _extract_embedded_known(raw)
    if known and (
        _canonical_known(raw)
        or len(raw) <= len(known) + 36
        or raw.lower().endswith(known.lower())
    ):
        return _Section(title=known)

    md = _MD_HEADING.match(raw)
    if md:
        title = md.group(2).strip()
        dotted = re.match(r"^((?:\d+\.)+\d*|\d+)\.?\s+(.+)$", title)
        if dotted:
            return _Section(number=dotted.group(1), title=dotted.group(2).strip())
        return _Section(title=_canonical_known(title) or title)

    labeled = _SECTION_LABEL.match(raw)
    if labeled:
        return _Section(
            number=labeled.group(1),
            title=_canonical_known(labeled.group(2)) or labeled.group(2).strip(),
        )

    # Prefer richer dotted titles (section headers) over bare recommendation numbers
    dotted = _DOTTED_SECTION.match(raw)
    if dotted and not raw.endswith(","):
        num, title = dotted.group(1), dotted.group(2).strip()
        # "1.2.4 Offer adults…" is a recommendation — keep number, trim to short title
        if re.match(r"^(Offer|Ensure|Consider|Do not|Advise|Provide|Refer)\b", title):
            short = title.split(".")[0][:80].strip()
            return _Section(number=num, title=short)
        return _Section(number=num, title=_canonical_known(title) or title)

    rec = _REC_NUMBER.match(raw)
    if rec and not raw.endswith(","):
        return _Section(number=rec.group(1), title=rec.group(2).strip()[:80])

    titled = _SECTION_TITLE_ONLY.match(raw)
    if titled:
        return _Section(title=_canonical_known(titled.group(1)) or titled.group(1).strip())

    if _ALL_CAPS.match(raw) and 3 <= len(raw.split()) <= 10:
        pretty = raw.title() if raw.isupper() else raw
        return _Section(title=_canonical_known(pretty) or pretty)

    if (
        _TITLE_CASE.match(raw)
        and 2 <= len(raw.split()) <= 8
        and not raw.endswith(".")
        and len(raw) <= 70
    ):
        return _Section(title=_canonical_known(raw) or raw)

    return None


def _merge_broken_headings(lines: list[str]) -> list[str]:
    """Join PDF-broken titles like 'Who' + 'to screen' → 'Who to screen'."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        cur = _normalize_line(lines[i])
        if not cur:
            i += 1
            continue
        if i + 1 < len(lines):
            nxt = _normalize_line(lines[i + 1])
            joined = f"{cur} {nxt}".strip()
            if (
                nxt
                and len(cur.split()) <= 4
                and len(nxt.split()) <= 5
                and len(joined) <= 80
                and not _looks_like_body(cur)
                and not _looks_like_body(nxt)
                and (
                    _canonical_known(joined)
                    or _parse_heading(joined) is not None
                    and _parse_heading(cur) is None
                )
            ):
                out.append(joined)
                i += 2
                continue
        out.append(cur)
        i += 1
    return out


def infer_section_title(text: str, current: str | None = None) -> str | None:
    """Fill section_title from known inline headings when line-based parse missed them."""
    if current:
        return current
    matches = list(_INLINE_SECTION_TITLE.finditer(text or ""))
    if not matches:
        return None
    raw = matches[0].group(1).strip()
    return _canonical_known(raw) or raw


def chunk_units(
    units: list[PageUnit],
    *,
    source: str,
    source_path: str,
    chunk_size: int = 1024,
    overlap: int = 100,
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
                section_title=infer_section_title(cleaned, sec.title),
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
            # Keep section for the overlap tail; advance page to continuing page below.
        else:
            buffer = []
            buffer_len = 0
            buffer_page = None

    for unit in units:
        lines = _merge_broken_headings(unit.text.splitlines())
        for stripped in lines:
            if not stripped:
                continue

            heading = _parse_heading(stripped)
            if heading is not None:
                # Always flush before a new section so early headings keep their title.
                if buffer:
                    flush(keep_overlap=False)
                section = heading
                buffer_page = unit.page
                buffer_section = section
                buffer.append(stripped)
                buffer_len += len(stripped)
                continue

            if not buffer:
                buffer_page = unit.page
                buffer_section = section
            elif buffer_page is None and unit.page is not None:
                buffer_page = unit.page

            buffer.append(stripped)
            buffer_len += len(stripped)

            if current_len() >= chunk_size:
                flush(keep_overlap=True)
                # After overlap flush, continuing text belongs to the next page unit.
                buffer_section = section
                buffer_page = unit.page

    flush(keep_overlap=False)
    return chunks


def chunk_text(
    text: str,
    *,
    source: str,
    source_path: str,
    chunk_size: int = 1024,
    overlap: int = 100,
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
