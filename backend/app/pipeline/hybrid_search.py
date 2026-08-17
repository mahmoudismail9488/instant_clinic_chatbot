from __future__ import annotations

import re
from typing import Any
from rank_bm25 import BM25Okapi


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def rrf_hybrid_merge(
    dense_hits: list[dict[str, Any]],
    all_store_documents: list[dict[str, Any]],
    query: str,
    top_k: int = 5,
    n_candidates: int = 20,
    k_rrf: int = 60,
) -> list[dict[str, Any]]:
    """Combines dense vector search hits with BM25 lexical search hits using Reciprocal Rank Fusion (RRF)."""
    if not all_store_documents:
        return dense_hits[:top_k]

    # 1. BM25 Lexical Search
    corpus = [tokenize(str(doc.get("text", ""))) for doc in all_store_documents]
    bm25 = BM25Okapi(corpus)
    query_tokens = tokenize(query)
    bm25_scores = bm25.get_scores(query_tokens)

    # Get top sparse candidates
    top_bm25_indices = sorted(
        range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
    )[:n_candidates]
    bm25_hits = [all_store_documents[i] for i in top_bm25_indices]

    # 2. Reciprocal Rank Fusion (RRF)
    doc_lookup: dict[str, dict[str, Any]] = {}
    fused_scores: dict[str, float] = {}

    for rank, hit in enumerate(dense_hits[:n_candidates]):
        text = hit["text"]
        doc_lookup[text] = hit
        fused_scores[text] = fused_scores.get(text, 0.0) + (1.0 / (rank + k_rrf))

    for rank, hit in enumerate(bm25_hits):
        text = hit["text"]
        doc_lookup[text] = hit
        fused_scores[text] = fused_scores.get(text, 0.0) + (1.0 / (rank + k_rrf))

    # 3. Sort by fused score
    sorted_items = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    merged_hits: list[dict[str, Any]] = []
    for text, score in sorted_items:
        hit = dict(doc_lookup[text])
        hit["score"] = score
        merged_hits.append(hit)

    return merged_hits