"""Step 8 (optional): BM25 keyword retrieval vs dense baseline for ONE question."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from rank_bm25 import BM25Okapi

from backend.app.services.llm_client import LLMClient
from backend.app.services.vector_store import VectorStore
from eval.common import OUTPUT_DIR, default_baseline_store, format_section, load_questions, snippet


def tokenize(text: str) -> list[str]:
    return [t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if t]


def main() -> int:
    parser = argparse.ArgumentParser(description="Isolated BM25 vs dense comparison")
    parser.add_argument("--question-id", type=str, default="Q07")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--out", type=str, default=str(OUTPUT_DIR / "alternative_bm25_Q07.csv"))
    args = parser.parse_args()

    questions = {q["question_id"]: q["question"] for q in load_questions()}
    if args.question_id not in questions:
        raise SystemExit(f"Unknown question_id {args.question_id}")
    query = questions[args.question_id]

    store = default_baseline_store()
    if store.size == 0:
        raise SystemExit("Empty index")

    corpus_tokens = [tokenize(c.text) for c in store._chunks]
    bm25 = BM25Okapi(corpus_tokens)
    scores = bm25.get_scores(tokenize(query))
    top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[: args.top_k]

    bm25_rows = []
    for rank, idx in enumerate(top_idx, start=1):
        ch = store._chunks[idx]
        meta = ch.metadata or {}
        bm25_rows.append(
            {
                "question_id": args.question_id,
                "method": "bm25",
                "rank": rank,
                "chunk_id": ch.id,
                "score": float(scores[idx]),
                "document": ch.source,
                "page": meta.get("page", ""),
                "section_number": meta.get("section_number", ""),
                "section_title": meta.get("section_title", ""),
                "section": format_section(meta.get("section_number"), meta.get("section_title")),
                "chunk_text_snippet": snippet(ch.text),
            }
        )

    client = LLMClient()
    emb = client.embed([query])[0]
    dense_hits = store.similarity_search(emb, top_k=args.top_k)
    dense_rows = []
    for rank, hit in enumerate(dense_hits, start=1):
        meta = hit.get("metadata") or {}
        sec_n = hit.get("section_number", meta.get("section_number")) or ""
        sec_t = hit.get("section_title", meta.get("section_title")) or ""
        dense_rows.append(
            {
                "question_id": args.question_id,
                "method": "dense",
                "rank": rank,
                "chunk_id": hit.get("id"),
                "score": float(hit["score"]),
                "document": hit.get("source"),
                "page": hit.get("page", meta.get("page", "")),
                "section_number": sec_n,
                "section_title": sec_t,
                "section": format_section(sec_n, sec_t),
                "chunk_text_snippet": snippet(str(hit.get("text", ""))),
            }
        )

    out_df = pd.DataFrame(bm25_rows + dense_rows)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out, index=False)
    print(out_df.to_string(index=False))
    print(f"\nWrote {out}")

    bm25_ids = set(out_df[out_df["method"] == "bm25"]["chunk_id"])
    dense_ids = set(out_df[out_df["method"] == "dense"]["chunk_id"])
    print(f"Overlap in top-{args.top_k}: {len(bm25_ids & dense_ids)} / {args.top_k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
