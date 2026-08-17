# CliniRAG retrieval evaluation lab

Scripts in `eval/` · artifacts in `eval/outputs/`.

**Deliverable:** [`outputs/LAB_REPORT.md`](outputs/LAB_REPORT.md) — fair comparison of **old / cfgA / cfgB** on the current 2-PDF corpus, with Precision@3/@5, top-k tables, failure modes, labels, and the final config decision.

## Chunk configs

All three are indexed into isolated Qdrant collections under `data/qdrant_lab/` from the same `data/raw_guidelines/` corpus.

| key | size | overlap | collection | role |
|---|---:|---:|---|---|
| `old` | 1200 | 200 | `guidelines_old` | pre-lab production defaults |
| `cfgA` | 512 | 50 | `guidelines_cfgA` | smaller-chunk candidate |
| `cfgB` | 1024 | 100 | `guidelines_cfgB` | **selected** → production |

Retrieval CSVs include `chunk_text`, `score`, `document`, `page`, `section_number`, `section_title`, `section`, and `chunk_id`.

## Workflow

```bash
# 1) Index + retrieve top-10 for all configs (confirms before overwrite unless --yes)
uv run python -m eval.reindex_and_retrieve --config all --recreate --yes

# Single config:
# uv run python -m eval.reindex_and_retrieve --config cfgB --recreate --yes

# 2) Manual labels (resume-safe CLI)
uv run python -m eval.label_relevance \
  --retrieval eval/outputs/retrieval_results_old.csv \
  --retrieval eval/outputs/retrieval_results_cfgA.csv \
  --retrieval eval/outputs/retrieval_results_cfgB.csv

# 3) Precision@3 / Precision@5
uv run python -m eval.compute_metrics \
  --retrieval eval/outputs/retrieval_results_old.csv \
  --retrieval eval/outputs/retrieval_results_cfgA.csv \
  --retrieval eval/outputs/retrieval_results_cfgB.csv

# 4) Top-3 vs Top-5 vs Top-10 relevant counts
uv run python -m eval.compare_topk \
  --retrieval eval/outputs/retrieval_results_cfgB.csv \
  --config cfgB \
  --question-id Q01 --question-id Q02 --question-id Q07

# 5) Optional: BM25 keyword vs dense on one question
uv run python -m eval.alternative_bm25 --question-id Q07
```

Optional baseline against the production numpy index (`data/index/`):

```bash
uv run python -m eval.run_baseline_retrieval
```

## Key outputs

| path | purpose |
|---|---|
| `outputs/LAB_REPORT.md` | full lab write-up |
| `outputs/retrieval_results_{old,cfgA,cfgB}.csv` | top-10 hits per question |
| `outputs/relevance_labels.csv` | manual relevant / not relevant |
| `outputs/labeled_retrieval_top5.csv` | top-5 joined with labels |
| `outputs/metrics_summary.csv` | P@3 / P@5 per question + averages |
| `outputs/alternative_bm25_Q07.csv` | optional keyword vs dense |
| `questions.json` | 18 evaluation questions |

## Latest fair-eval averages (same corpus)

| config | P@3 | P@5 |
|---|---:|---:|
| old | 0.315 | 0.333 |
| cfgA | 0.370 | 0.356 |
| **cfgB** | **0.407** | **0.433** |

Do not overwrite Qdrant collections without `--recreate` (and confirmation, or `--yes`).
