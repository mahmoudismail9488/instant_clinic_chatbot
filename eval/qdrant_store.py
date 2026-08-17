"""Qdrant helpers for isolated eval collections (local embedded path)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from eval.common import QDRANT_PATH, format_section, snippet


def get_client(path: Path | None = None) -> QdrantClient:
    root = Path(path or QDRANT_PATH)
    root.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(root))


def list_collections(client: QdrantClient | None = None) -> list[str]:
    c = client or get_client()
    return [col.name for col in c.get_collections().collections]


def ensure_collection(
    client: QdrantClient,
    name: str,
    *,
    vector_size: int,
    recreate: bool = False,
) -> None:
    existing = list_collections(client)
    if name in existing:
        if not recreate:
            raise FileExistsError(
                f"Qdrant collection '{name}' already exists. "
                "Re-run with --recreate only after confirming overwrite is OK."
            )
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config=qm.VectorParams(size=vector_size, distance=qm.Distance.COSINE),
    )


def upsert_chunks(
    client: QdrantClient,
    collection: str,
    *,
    ids: list[str],
    vectors: list[list[float]],
    payloads: list[dict[str, Any]],
    id_offset: int = 0,
) -> None:
    points = [
        qm.PointStruct(
            id=id_offset + i,
            vector=vec,
            payload={**payload, "chunk_id": chunk_id},
        )
        for i, (chunk_id, vec, payload) in enumerate(zip(ids, vectors, payloads, strict=True))
    ]
    client.upsert(collection_name=collection, points=points)


def search(
    client: QdrantClient,
    collection: str,
    query_vector: list[float],
    *,
    top_k: int = 10,
) -> list[dict[str, Any]]:
    # qdrant-client >=1.10 prefers query_points; fall back to search.
    try:
        response = client.query_points(
            collection_name=collection,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )
        hits = response.points
    except Exception:
        hits = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
        )

    rows: list[dict[str, Any]] = []
    for hit in hits:
        payload = hit.payload or {}
        rows.append(
            {
                "chunk_id": payload.get("chunk_id") or str(hit.id),
                "score": float(hit.score),
                "text": payload.get("text", ""),
                "document": payload.get("document") or payload.get("source", ""),
                "page": payload.get("page", ""),
                "section_number": payload.get("section_number", ""),
                "section_title": payload.get("section_title", ""),
                "section": payload.get("section")
                or format_section(payload.get("section_number"), payload.get("section_title")),
                "chunk_text_snippet": snippet(str(payload.get("text", ""))),
            }
        )
    return rows
