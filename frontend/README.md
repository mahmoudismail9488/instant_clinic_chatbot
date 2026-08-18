# Instant Clinic frontend

UI from [cheerful-digital-garden](https://github.com/ahmed-nagah-r/cheerful-digital-garden) (Vite + TanStack Start / React).

Talks to the CliniRAG FastAPI backend via `VITE_API_URL` (`src/lib/clinirag-api.ts` → `POST /query`).

## Setup

```bash
# from repo root — start API first
uv run clinic-api

# then frontend
cd frontend
cp .env.example .env
# ensure:
#   VITE_API_URL=http://127.0.0.1:8000
#   VITE_SUPABASE_* keys filled
npm install
npm run dev
```

## Notes

- Workspace chat is live RAG (not demo turns): `src/routes/_authenticated/workspace.tsx`
- Auth / admin uploads still use Supabase
- Source upstream: `git@github.com:ahmed-nagah-r/cheerful-digital-garden.git`
