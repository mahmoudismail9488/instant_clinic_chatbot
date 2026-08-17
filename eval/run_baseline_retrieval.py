"""Step 1–2: run dense retrieval on all eval questions against the current index."""

from __future__ import annotations

import argparse

from backend.app.services.llm_client import LLMClient
from eval.common import (
    OUTPUT_DIR,
    default_baseline_store,
    load_questions,
    retrieve_rows_from_numpy_store,
    save_retrieval_csv,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Baseline retrieval for CliniRAG eval lab")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument(
        "--out",
        type=str,
        default=str(OUTPUT_DIR / "retrieval_results.csv"),
    )
    args = parser.parse_args()

    questions = load_questions()
    store = default_baseline_store()
    if store.size == 0:
        raise SystemExit("Current index is empty. Run: uv run clinic ingest")

    print(f"Index size: {store.size} | questions: {len(questions)} | top_k={args.top_k}")
    client = LLMClient()
    rows = retrieve_rows_from_numpy_store(
        questions=questions,
        store=store,
        client=client,
        top_k=args.top_k,
        config="baseline",
    )
    df = save_retrieval_csv(rows, path=__import__("pathlib").Path(args.out))
    print(f"Wrote {len(df)} rows → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
