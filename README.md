# Instant Clinic — CLI + web RAG

Guideline-grounded diabetes screening assistant: **CLI**, **HTTP API**, and **Vite frontend**.

| | |
|---|---|
| **Chat** | Groq (`GROQ_AI_MODEL`) |
| **Embeddings** | local `fastembed` (`BAAI/bge-small-en-v1.5`) |
| **Chunking** | **Config B** — `chunk_size=1024`, `overlap=100` |
| **Index** | numpy cosine store under `data/index/` |
| **Answer path** | Day 3 **grounded** pipeline (safety → retrieve → structured cite) |
| **API** | FastAPI `POST /query` · `GET /health` |
| **Day 2 eval** | [`eval/outputs/LAB_REPORT.md`](eval/outputs/LAB_REPORT.md) |
| **Day 3 docs** | [`docs/day3/CHECKLIST.md`](docs/day3/CHECKLIST.md) |

## Setup

```bash
cp backend/app/.env.example backend/app/.env   # set GROQ_API_KEY
uv sync
uv run clinic ingest                           # rebuild index after chunk/corpus changes
```

## Run (full stack)

**Terminal 1 — API** (grounded pipeline):

```bash
uv run clinic-api
# → http://localhost:8000  · OpenAPI at /docs
```

**Terminal 2 — frontend** (Vite often binds **:8080**):

```bash
cd frontend
cp .env.example .env   # VITE_API_URL=http://localhost:8000 + Supabase keys
npm install
npm run dev
```

Open the app → sign in → **Diabetes Screening** → ask a question.  
The workspace calls `POST /query` and shows **recommendation → claims → citations** (document · page · section) plus the evidence panel.

### Same grounded pipeline from CLI

```bash
uv run clinic grounded "Who should be screened for type 2 diabetes?"
uv run clinic grounded "Do I have diabetes?"          # safety refusal (before retrieval)
uv run clinic calibrate                               # evidence threshold
uv run clinic test --out docs/day3/results.md         # answer-layer matrix
uv run clinic review --report                         # citation correctness summary
```

### API smoke test

```bash
curl -s http://localhost:8000/health | jq
# {"status":"ok","pipeline":"grounded",...}

curl -s -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"Who should be screened for type 2 diabetes?"}' \
  | jq '{kind,status,confidence,evidence:(.evidence[0]//null)}'

curl -s -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"Do I have diabetes?"}' \
  | jq '{kind,reason,status}'
```

## Pipeline (Day 3)

```
question
  → patient-specific safety gate (refuse dosage / “do I have…”)
  → dense retrieve top-k (Config B index)
  → evidence threshold + dedupe
  → grounding prompt + structured JSON answer
  → citation coverage validation (fail-closed)
  → recommendation + cited claims (+ evidence chunks)
```

Legacy free-text path (Day 2 style, no structured citations):

```bash
uv run clinic query "Who should be screened for type 2 diabetes?"
```

## Corpus

Active files in `data/raw_guidelines/`:

- `Diabetes-Canada-2024-CPG-Quick-Reference-Guide.pdf`
- `NICE-NG28-Type2-Diabetes-Adults-Recommendations.pdf`

See [`data/raw_guidelines/SOURCES.md`](data/raw_guidelines/SOURCES.md).

## Day 2 — retrieval evaluation

See [`eval/README.md`](eval/README.md) · report: [`eval/outputs/LAB_REPORT.md`](eval/outputs/LAB_REPORT.md)

| config | size | overlap | avg P@3 | avg P@5 |
|---|---:|---:|---:|---:|
| old | 1200 | 200 | 0.315 | 0.333 |
| cfgA | 512 | 50 | 0.370 | 0.356 |
| **cfgB** | **1024** | **100** | **0.407** | **0.433** |

## Day 3 — grounded answers

| Doc | Purpose |
|---|---|
| [`docs/day3/CHECKLIST.md`](docs/day3/CHECKLIST.md) | Lab steps, deliverables, failures, wiring notes |
| [`docs/day3/results.md`](docs/day3/results.md) | Supported / unsupported / unsafe matrix |
| [`docs/day3/citation_review.csv`](docs/day3/citation_review.csv) | Citation correctness reviews |

## Layout

```
backend/app/          CLI + FastAPI + grounded RAG pipeline
frontend/             Vite / TanStack UI (workspace → POST /query)
data/raw_guidelines/  source PDFs
data/index/           production numpy index
eval/                 Day 2 retrieval lab
docs/day3/            Day 3 grounded-answer lab
```
