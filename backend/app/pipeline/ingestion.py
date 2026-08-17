"""Stage 1 — load guideline files (PDF and .txt) into page-aware units."""

from dataclasses import dataclass
from pathlib import Path

from backend.app.pipeline.source_loader import PageUnit, load_source_units

SUPPORTED_SUFFIXES = {".pdf", ".txt"}


@dataclass(frozen=True)
class IngestedDocument:
    source: str
    source_path: Path
    units: list[PageUnit]


def list_guideline_files(directory: Path, *, txt_only: bool = False) -> list[Path]:
    if not directory.exists():
        raise FileNotFoundError(f"Guidelines directory not found: {directory}")
    files = sorted(
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES and not p.name.startswith(".")
    )
    if txt_only:
        files = [p for p in files if p.suffix.lower() == ".txt"]
    return files


def ingest_file(path: Path) -> IngestedDocument:
    units = load_source_units(path)
    if not units:
        raise ValueError(f"No extractable text in {path.name}")
    return IngestedDocument(source=path.name, source_path=path, units=units)


def ingest_directory(directory: Path, *, txt_only: bool = False) -> list[IngestedDocument]:
    docs: list[IngestedDocument] = []
    for path in list_guideline_files(directory, txt_only=txt_only):
        try:
            docs.append(ingest_file(path))
        except Exception as exc:  # noqa: BLE001 - keep ingesting remaining files
            print(f"  ! skip {path.name}: {exc}")
    return docs
