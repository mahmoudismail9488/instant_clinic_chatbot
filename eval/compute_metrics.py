"""Step 5 (+ helpers for 6): compute Precision@3 / Precision@5 from manual labels."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from eval.common import OUTPUT_DIR

LABELS_PATH = OUTPUT_DIR / "relevance_labels.csv"


def precision_at_k(ranked: pd.DataFrame, labels: pd.DataFrame, k: int) -> float:
    top = ranked.nsmallest(k, "rank") if "rank" in ranked.columns else ranked.head(k)
    if top.empty:
        return float("nan")
    merged = top.merge(labels, on=["question_id", "config", "chunk_id"], how="left")
    if merged["relevant"].isna().all():
        return float("nan")
    # unlabeled in top-k treated as 0 for strict precision
    vals = merged["relevant"].fillna(0).astype(int)
    return float(vals.sum() / k)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute Precision@3/@5 from manual labels")
    parser.add_argument(
        "--retrieval",
        action="append",
        required=True,
        help="Retrieval CSV(s) to score",
    )
    parser.add_argument("--labels", type=str, default=str(LABELS_PATH))
    parser.add_argument("--out", type=str, default=str(OUTPUT_DIR / "metrics_summary.csv"))
    args = parser.parse_args()

    labels_path = Path(args.labels)
    if not labels_path.exists():
        raise SystemExit(
            f"No labels file at {labels_path}. Run: "
            "uv run python -m eval.label_relevance --retrieval eval/outputs/retrieval_results.csv"
        )

    labels = pd.read_csv(labels_path)
    if labels.empty or "relevant" not in labels.columns:
        raise SystemExit("Labels file is empty or missing `relevant` column.")

    frames = [pd.read_csv(p) for p in args.retrieval]
    retrieval = pd.concat(frames, ignore_index=True)

    rows = []
    for (qid, config), group in retrieval.groupby(["question_id", "config"]):
        group = group.sort_values("rank")
        lab = labels[(labels["question_id"] == qid) & (labels["config"] == config)]
        p3 = precision_at_k(group, lab, 3)
        p5 = precision_at_k(group, lab, 5)
        labeled_n = len(lab)
        rows.append(
            {
                "question_id": qid,
                "config": config,
                "precision_at_3": p3,
                "precision_at_5": p5,
                "n_labels": labeled_n,
            }
        )

    per_q = pd.DataFrame(rows)
    averages = (
        per_q.groupby("config")[["precision_at_3", "precision_at_5"]]
        .mean()
        .reset_index()
        .assign(question_id="AVERAGE", n_labels="")
    )
    out_df = pd.concat([per_q, averages], ignore_index=True)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(out_df.to_string(index=False))
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
