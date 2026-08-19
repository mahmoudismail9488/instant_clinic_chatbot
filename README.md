# GlucoRAG

Guideline-grounded diabetes screening assistant: **CLI**, **HTTP API**, and **Vite frontend**, with Day 4 safety evaluation and deploy packaging.

| | |
|---|---|
| **Chat** | Groq (`GROQ_AI_MODEL`) |
| **Embeddings** | local `fastembed` (`BAAI/bge-small-en-v1.5`) |
| **Chunking** | **Config B** — `chunk_size=1024`, `overlap=100` |
| **Index** | numpy cosine store under `data/index/` |
| **Answer path** | Grounded pipeline + Day 4 risk / claim-support nets |
| **API** | FastAPI `POST /query` · `GET /health` |
| **Docs (all)** | [`docs/`](docs/README.md) · final: [`docs/FINAL.md`](docs/FINAL.md) |

## Setup

```bash
cp backend/app/.env.example backend/app/.env   # set GROQ_API_KEY
uv sync
uv run clinic ingest                           # if index missing / corpus changed
```

## Run (full stack)

```bash
uv run clinic-api          # http://localhost:8000
cd frontend && npm run dev # http://localhost:8080
```

## Day 4 evaluation

```bash
uv run --extra dev pytest backend/tests/ -q
uv run clinic day4-eval --out docs/day4/EVALUATION_RESULTS.md
```

## Deploy

| Piece | Guide |
|---|---|
| Frontend → **Vercel** | [`docs/deploy/VERCEL.md`](docs/deploy/VERCEL.md) |
| API → **AWS** | [`docs/deploy/AWS.md`](docs/deploy/AWS.md) |
| Local containers | `docker compose up --build` |

## Layout

```
backend/app/     CLI + FastAPI + grounded RAG + Day 4 safety
frontend/        Vite / TanStack UI (Vercel-ready)
data/            guidelines + numpy index
eval/            Day 2 retrieval + Day 4 benchmark CSV
docs/            All documentation (day2–day4, deploy, FINAL)
deploy/aws/      ECS task definition sketch
Dockerfile       AWS/App Runner image
```
