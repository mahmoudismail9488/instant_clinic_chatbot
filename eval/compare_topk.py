"""Step 6: compare relevant-chunk counts at k=3,5,10 for selected questions."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from eval.common import OUTPUT_DIR


def main() -> int:
    parser = argparse.ArgumentParser(description="Top-3 vs Top-5 vs Top-10 relevant overlap table")
    parser.add_argument("--retrieval", action="append", required=True)
    parser.add_argument("--labels", type=str, default=str(OUTPUT_DIR / "relevance_labels.csv"))
    parser.add_argument(
        "--question-id",
        action="append",
        default=None,
        help="Question ids to compare (default: first 3 with labels)",
    )
    parser.add_argument("--config", type=str, default="baseline")
    parser.add_argument("--out", type=str, default=str(OUTPUT_DIR / "topk_comparison.md"))
    args = parser.parse_args()

    labels_path = Path(args.labels)
    if not labels_path.exists():
        raise SystemExit(f"Missing labels: {labels_path}")

    retrieval = pd.concat([pd.read_csv(p) for p in args.retrieval], ignore_index=True)
    retrieval = retrieval[retrieval["config"] == args.config]
    labels = pd.read_csv(labels_path)
    labels = labels[labels["config"] == args.config]

    qids = args.question_id
    if not qids:
        qids = list(labels["question_id"].drop_duplicates().head(3))
    if len(qids) < 1:
        raise SystemExit("No labeled questions available for comparison.")

    lines = ["# Top-3 vs Top-5 vs Top-10 relevant chunk comparison", ""]
    for qid in qids:
        rel_ids = set(
            labels[(labels["question_id"] == qid) & (labels["relevant"] == 1)]["chunk_id"].astype(str)
        )
        group = retrieval[retrieval["question_id"] == qid].sort_values("rank")
        lines.append(f"## {qid} (config={args.config})")
        lines.append("")
        lines.append("| k | #relevant_in_topk | relevant_chunk_ids |")
        lines.append("|---:|---:|---|")
        for k in (3, 5, 10):
            top = group.head(k)
            ids = [str(x) for x in top["chunk_id"].tolist()]
            hit = [cid for cid in ids if cid in rel_ids]
            lines.append(f"| {k} | {len(hit)} | {', '.join(hit) if hit else '(none)'} |")
        lines.append("")

    out = Path(args.out)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
