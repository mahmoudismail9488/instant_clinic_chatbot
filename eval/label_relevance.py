"""Step 4: manual relevance labeling CLI (resume-safe).

Keys labels by (question_id, config, chunk_id).
Does NOT auto-generate labels — human judgment only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from eval.common import OUTPUT_DIR

LABELS_PATH = OUTPUT_DIR / "relevance_labels.csv"


def _load_retrieval(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"question_id", "config", "chunk_id", "rank", "score", "document", "chunk_text"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Retrieval CSV missing columns: {missing}")
    return df


def _load_labels(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["question_id", "config", "chunk_id", "relevant", "notes"])
    return pd.read_csv(path)


def _save_labels(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual relevance labeling for CliniRAG eval")
    parser.add_argument(
        "--retrieval",
        action="append",
        required=True,
        help="Retrieval CSV path (repeatable). Example: --retrieval eval/outputs/retrieval_results.csv",
    )
    parser.add_argument("--labels", type=str, default=str(LABELS_PATH))
    parser.add_argument("--config", type=str, default=None, help="Optional filter by config label")
    parser.add_argument("--question-id", type=str, default=None, help="Optional filter by question_id")
    parser.add_argument("--max-rank", type=int, default=10, help="Only label ranks <= this")
    args = parser.parse_args()

    frames = [_load_retrieval(Path(p)) for p in args.retrieval]
    pool = pd.concat(frames, ignore_index=True)
    if args.config:
        pool = pool[pool["config"] == args.config]
    if args.question_id:
        pool = pool[pool["question_id"] == args.question_id]
    pool = pool[pool["rank"] <= args.max_rank].copy()
    pool = pool.sort_values(["config", "question_id", "rank"]).reset_index(drop=True)

    labels_path = Path(args.labels)
    labels = _load_labels(labels_path)
    labeled_keys = set(
        zip(labels["question_id"], labels["config"], labels["chunk_id"])
    ) if len(labels) else set()

    pending = []
    for _, row in pool.iterrows():
        key = (row["question_id"], row["config"], row["chunk_id"])
        if key not in labeled_keys:
            pending.append(row)

    print(f"Total candidates: {len(pool)} | already labeled: {len(labeled_keys)} | pending: {len(pending)}")
    print("Enter 1=relevant, 0=not relevant, s=skip, q=quit & save\n")

    new_rows = []
    for i, row in enumerate(pending, start=1):
        print("=" * 80)
        print(f"[{i}/{len(pending)}] {row['question_id']} | config={row['config']} | rank={row['rank']}")
        print(f"Q: {row.get('question', '')}")
        print(f"chunk_id: {row['chunk_id']}")
        print(f"score: {row['score']} | document: {row['document']} | page: {row.get('page','')} | section: {row.get('section','')}")
        print("-" * 80)
        text = str(row.get("chunk_text") or row.get("chunk_text_snippet") or "")
        print(text[:1200])
        print("-" * 80)
        while True:
            ans = input("relevant? [1/0/s/q]: ").strip().lower()
            if ans in {"1", "0", "s", "q"}:
                break
            print("Please enter 1, 0, s, or q")
        if ans == "q":
            break
        if ans == "s":
            continue
        new_rows.append(
            {
                "question_id": row["question_id"],
                "config": row["config"],
                "chunk_id": row["chunk_id"],
                "relevant": int(ans),
                "notes": "",
            }
        )
        # incremental save
        labels = pd.concat([labels, pd.DataFrame(new_rows[-1:])], ignore_index=True)
        labels = labels.drop_duplicates(subset=["question_id", "config", "chunk_id"], keep="last")
        _save_labels(labels, labels_path)
        print(f"Saved → {labels_path} ({len(labels)} labels)")

    if new_rows:
        print(f"Session complete. Total labels on disk: {len(_load_labels(labels_path))}")
    else:
        print("No new labels entered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
