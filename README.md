# Instant Clinic — CLI RAG demo

Query diabetes screening guidelines from `data/raw_guidelines` via the terminal.

**Stack:** Groq for answers · local `fastembed` for retrieval embeddings
(Groq does not currently expose embedding models on this API).

## Setup

1. Put keys in `backend/app/.env` (see `.env.example`):
   - `GROQ_API_KEY` — answer generation
2. Install deps:

```bash
uv sync
```

## Ingest

```bash
# Fast demo (3 .txt files)
uv run clinic ingest --txt-only

# Full corpus (PDF + txt)
uv run clinic ingest
```

## Query

```bash
uv run clinic query "Who should be screened for type 2 diabetes?"
```

Prints the grounded **answer** and **related chunks** with scores and source filenames.
