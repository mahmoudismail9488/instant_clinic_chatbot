"""Stage 2 — split raw text into overlapping chunks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    text: str
    index: int
    source: str
    source_path: str


def chunk_text(
    text: str,
    *,
    source: str,
    source_path: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be in [0, chunk_size)")

    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: list[Chunk] = []
    start = 0
    index = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(
                Chunk(text=piece, index=index, source=source, source_path=source_path)
            )
            index += 1
        if end == len(cleaned):
            break
        start = end - overlap
    return chunks
