"""Dense + BM25 hybrid merge via Reciprocal Rank Fusion (RRF)."""

from __future__ import annotations

import re
from typing import Any

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def doc_key(hit: dict[str, Any]) -> str:
    """Stable fusion key — prefer chunk id over raw text."""
    if hit.get("id"):
        return str(hit["id"])
    source = hit.get("source") or (hit.get("metadata") or {}).get("source") or ""
    idx = hit.get("chunk_index")
    if idx is None:
        idx = (hit.get("metadata") or {}).get("chunk_index", 0)
    return f"{source}:{idx}:{hash(str(hit.get('text', ''))[:120])}"


def build_bm25(documents: list[dict[str, Any]]) -> BM25Okapi | None:
    if not documents:
        return None
    corpus = [tokenize(str(doc.get("text", ""))) for doc in documents]
    return BM25Okapi(corpus)


def rrf_hybrid_merge(
    dense_hits: list[dict[str, Any]],
    all_store_documents: list[dict[str, Any]],
    query: str,
    *,
    top_k: int = 5,
    n_candidates: int = 20,
    k_rrf: int = 60,
    bm25: BM25Okapi | None = None,
) -> list[dict[str, Any]]:
    """Combine dense vector hits with BM25 lexical hits using Reciprocal Rank Fusion."""
    if not all_store_documents:
        return dense_hits[:top_k]

    engine = bm25 or build_bm25(all_store_documents)
    if engine is None:
        return dense_hits[:top_k]

    query_tokens = tokenize(query)
    if not query_tokens:
        return dense_hits[:top_k]

    bm25_scores = engine.get_scores(query_tokens)
    top_bm25_indices = sorted(
        range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
    )[:n_candidates]
    bm25_hits = [all_store_documents[i] for i in top_bm25_indices]

    doc_lookup: dict[str, dict[str, Any]] = {}
    fused_scores: dict[str, float] = {}

    for rank, hit in enumerate(dense_hits[:n_candidates]):
        key = doc_key(hit)
        doc_lookup[key] = hit
        fused_scores[key] = fused_scores.get(key, 0.0) + (1.0 / (rank + k_rrf))

    for rank, hit in enumerate(bm25_hits):
        key = doc_key(hit)
        # Prefer dense metadata when both lists contain the same chunk.
        doc_lookup.setdefault(key, hit)
        fused_scores[key] = fused_scores.get(key, 0.0) + (1.0 / (rank + k_rrf))

    sorted_items = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    merged_hits: list[dict[str, Any]] = []
    for key, score in sorted_items:
        hit = dict(doc_lookup[key])
        hit["score"] = score
        merged_hits.append(hit)

    return merged_hits
