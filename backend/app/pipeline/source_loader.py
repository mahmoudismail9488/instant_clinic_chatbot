"""Dispatch loaders by file type (pdf / txt)."""

from pathlib import Path


def load_source_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return _load_txt(path)
    if suffix == ".pdf":
        return _load_pdf(path)
    raise ValueError(f"Unsupported source type: {suffix}")


def _load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _load_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[str] = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[page {page_num}]\n{text}")
    return "\n\n".join(pages)
