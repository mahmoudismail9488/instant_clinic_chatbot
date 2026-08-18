# Instant Clinic — CLI + web RAG

Guideline-grounded diabetes screening assistant: **CLI**, **HTTP API**, and **Vite frontend**.

| | |
|---|---|
| **Chat** | Groq (`GROQ_AI_MODEL`) |
| **Embeddings** | local `fastembed` (`BAAI/bge-small-en-v1.5`) |
| **Chunking** | **Config B** — `chunk_size=1024`, `overlap=100` |
| **Index** | numpy cosine store under `data/index/` |
| **API** | FastAPI `POST /query` · `GET /health` |
| **Eval report** | [`eval/outputs/LAB_REPORT.md`](eval/outputs/LAB_REPORT.md) |

## Setup

```bash
cp backend/app/.env.example backend/app/.env   # set GROQ_API_KEY
uv sync
uv run clinic ingest
```

## Run (full stack)

Terminal 1 — API:

```bash
uv run clinic-api
# → http://127.0.0.1:8000  (docs at /docs)
```

Terminal 2 — frontend:

```bash
cd frontend
cp .env.example .env   # set Supabase + VITE_API_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Open the app, sign in, start a **Diabetes Screening** session, and ask a question. The workspace calls `POST /query` and shows answer + evidence chunks.

### API smoke test

```bash
curl -s http://127.0.0.1:8000/health | jq
curl -s -X POST http://127.0.0.1:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"Who should be screened for type 2 diabetes?"}' | jq '.kind,.confidence,.chunks[0].section_title'
```

## CLI query

```bash
uv run clinic query "Who should be screened for type 2 diabetes?"
```

## Corpus

Active files in `data/raw_guidelines/`:

- `Diabetes-Canada-2024-CPG-Quick-Reference-Guide.pdf`
- `NICE-NG28-Type2-Diabetes-Adults-Recommendations.pdf`

See [`data/raw_guidelines/SOURCES.md`](data/raw_guidelines/SOURCES.md).

## Retrieval evaluation

See [`eval/README.md`](eval/README.md) · report: [`eval/outputs/LAB_REPORT.md`](eval/outputs/LAB_REPORT.md)

| config | size | overlap | avg P@3 | avg P@5 |
|---|---:|---:|---:|---:|
| old | 1200 | 200 | 0.315 | 0.333 |
| cfgA | 512 | 50 | 0.370 | 0.356 |
| **cfgB** | **1024** | **100** | **0.407** | **0.433** |

## Layout

```
backend/app/          CLI + FastAPI + RAG pipeline
frontend/             Vite / TanStack UI
data/raw_guidelines/  source PDFs
data/index/           production numpy index
eval/                 retrieval lab
```
