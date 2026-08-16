"""Persistent local vector store (numpy cosine similarity)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from backend.app.config import get_settings


@dataclass
class StoredChunk:
    id: str
    text: str
    source: str
    source_path: str
    chunk_index: int
    metadata: dict[str, Any]


class VectorStore:
    def __init__(self, index_dir: Path | None = None) -> None:
        settings = get_settings()
        self.index_dir = Path(index_dir or settings.vector_index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._meta_path = self.index_dir / "chunks.json"
        self._emb_path = self.index_dir / "embeddings.npy"
        self._chunks: list[StoredChunk] = []
        self._embeddings: np.ndarray | None = None
        self.load()

    @property
    def size(self) -> int:
        return len(self._chunks)

    def clear(self) -> None:
        self._chunks = []
        self._embeddings = None
        if self._meta_path.exists():
            self._meta_path.unlink()
        if self._emb_path.exists():
            self._emb_path.unlink()

    def load(self) -> None:
        if not self._meta_path.exists() or not self._emb_path.exists():
            self._chunks = []
            self._embeddings = None
            return
        raw = json.loads(self._meta_path.read_text(encoding="utf-8"))
        self._chunks = [StoredChunk(**item) for item in raw]
        self._embeddings = np.load(self._emb_path)

    def save(self) -> None:
        payload = [asdict(chunk) for chunk in self._chunks]
        self._meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if self._embeddings is not None:
            np.save(self._emb_path, self._embeddings)

    def upsert(
        self,
        *,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        if not (len(ids) == len(embeddings) == len(documents) == len(metadatas)):
            raise ValueError("upsert inputs must have equal lengths")

        matrix = np.asarray(embeddings, dtype=np.float32)
        if matrix.ndim != 2:
            raise ValueError("embeddings must be a 2D matrix")

        new_chunks = [
            StoredChunk(
                id=doc_id,
                text=document,
                source=str(meta.get("source", "unknown")),
                source_path=str(meta.get("source_path", "")),
                chunk_index=int(meta.get("chunk_index", 0)),
                metadata=meta,
            )
            for doc_id, document, meta in zip(ids, documents, metadatas, strict=True)
        ]

        if self._embeddings is None or len(self._chunks) == 0:
            self._chunks = new_chunks
            self._embeddings = matrix
        else:
            self._chunks.extend(new_chunks)
            self._embeddings = np.vstack([self._embeddings, matrix])
        self.save()

    def similarity_search(
        self, query_embedding: list[float], *, top_k: int = 5
    ) -> list[dict[str, Any]]:
        if self._embeddings is None or len(self._chunks) == 0:
            return []

        query = np.asarray(query_embedding, dtype=np.float32)
        docs = self._embeddings
        # Cosine similarity
        query_norm = np.linalg.norm(query) + 1e-12
        doc_norms = np.linalg.norm(docs, axis=1) + 1e-12
        scores = (docs @ query) / (doc_norms * query_norm)
        k = min(top_k, len(self._chunks))
        top_idx = np.argsort(scores)[::-1][:k]

        results: list[dict[str, Any]] = []
        for idx in top_idx:
            chunk = self._chunks[int(idx)]
            results.append(
                {
                    "id": chunk.id,
                    "text": chunk.text,
                    "score": float(scores[int(idx)]),
                    "source": chunk.source,
                    "source_path": chunk.source_path,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata,
                }
            )
        return results
