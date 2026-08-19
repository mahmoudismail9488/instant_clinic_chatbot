"""Dispatch loaders by file type (pdf / txt), preserving page boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PageUnit:
    """One loadable unit of source text (a PDF page, or the whole .txt file)."""

    text: str
    page: int | None  # 1-based PDF page; None for plain text


def load_source_text(path: Path) -> str:
    """Backward-compatible flat text (page markers included for PDFs)."""
    units = load_source_units(path)
    parts: list[str] = []
    for unit in units:
        if unit.page is not None:
            parts.append(f"[page {unit.page}]\n{unit.text}")
        else:
            parts.append(unit.text)
    return "\n\n".join(parts)


def load_source_units(path: Path) -> list[PageUnit]:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return _load_txt_units(path)
    if suffix == ".pdf":
        return _load_pdf_units(path)
    raise ValueError(f"Unsupported source type: {suffix}")


def _load_txt_units(path: Path) -> list[PageUnit]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [PageUnit(text=text, page=None)] if text.strip() else []


def _load_pdf_units(path: Path) -> list[PageUnit]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    units: list[PageUnit] = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        # Soften common PDF extraction glue so section detectors can fire.
        text = text.replace("\xa0", " ")
        text = text.replace("UPDATED FOR 2025How", "UPDATED FOR 2025\nHow")
        if text.strip():
            units.append(PageUnit(text=text, page=page_num))
    return units
