# Instant Clinic — CLI RAG demo

Query diabetes screening guidelines from `data/raw_guidelines` via the terminal.

| | |
|---|---|
| **Chat** | Groq (`GROQ_AI_MODEL`) |
| **Embeddings** | local `fastembed` (`BAAI/bge-small-en-v1.5`) |
| **Chunking** | **Config B** — `chunk_size=1024`, `overlap=100` |
| **Index** | numpy cosine store under `data/index/` |
| **Eval report** | [`eval/outputs/LAB_REPORT.md`](eval/outputs/LAB_REPORT.md) |

Old production defaults were `1200` / `200`. Fair bake-off on the current corpus chose Config B (best Precision@3 and Precision@5 vs old and cfgA).

## Setup

1. Copy env and set your key:

```bash
cp backend/app/.env.example backend/app/.env
# edit GROQ_API_KEY
```

2. Install:

```bash
uv sync
```

## Corpus

Active ingest files in `data/raw_guidelines/`:

- `Diabetes-Canada-2024-CPG-Quick-Reference-Guide.pdf`
- `NICE-NG28-Type2-Diabetes-Adults-Recommendations.pdf`

See [`data/raw_guidelines/SOURCES.md`](data/raw_guidelines/SOURCES.md) and [`CITATIONS.md`](data/raw_guidelines/CITATIONS.md).

## Ingest

Rebuild the vector index after changing chunk settings or corpus files:

```bash
uv run clinic ingest
```

Uses `CHUNK_SIZE` / `CHUNK_OVERLAP` from `.env` (Config B by default). Each chunk stores `page`, `section_number`, and `section_title` when detected.

## Query

```bash
uv run clinic query "Who should be screened for type 2 diabetes?"
```

Prints a grounded **answer** plus **related chunks** (score, document, page, `section_number`, `section_title`).

## Frontend

UI lives in `frontend/` (from [cheerful-digital-garden](https://github.com/ahmed-nagah-r/cheerful-digital-garden)):

```bash
cd frontend
cp .env.example .env   # add Supabase keys if using auth
npm install
npm run dev
```

See [`frontend/README.md`](frontend/README.md).

## Retrieval evaluation

Lab scripts and checklist results live under `eval/`:

```bash
# Re-index + retrieve old / cfgA / cfgB on the current corpus
uv run python -m eval.reindex_and_retrieve --config all --recreate --yes

# Precision@3 / @5 (needs labels in eval/outputs/relevance_labels.csv)
uv run python -m eval.compute_metrics \
  --retrieval eval/outputs/retrieval_results_old.csv \
  --retrieval eval/outputs/retrieval_results_cfgA.csv \
  --retrieval eval/outputs/retrieval_results_cfgB.csv
```

Details: [`eval/README.md`](eval/README.md) · full report: [`eval/outputs/LAB_REPORT.md`](eval/outputs/LAB_REPORT.md)

### Selected config (from lab)

| config | size | overlap | avg P@3 | avg P@5 |
|---|---:|---:|---:|---:|
| old | 1200 | 200 | 0.315 | 0.333 |
| cfgA | 512 | 50 | 0.370 | 0.356 |
| **cfgB** | **1024** | **100** | **0.407** | **0.433** |

## Layout

```
backend/app/          CLI + RAG pipeline + config
frontend/             Vite / TanStack UI (cheerful-digital-garden)
data/raw_guidelines/  source PDFs
data/index/           production numpy index
data/qdrant_lab/      isolated eval collections
eval/                 retrieval lab scripts + outputs
```
