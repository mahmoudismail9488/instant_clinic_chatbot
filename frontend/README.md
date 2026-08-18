# Instant Clinic frontend

UI from [cheerful-digital-garden](https://github.com/ahmed-nagah-r/cheerful-digital-garden) (Vite + TanStack Start / React).

## Setup

```bash
cd frontend
cp .env.example .env   # fill Supabase keys if needed
npm install            # or: bun install
npm run dev
```

Dev server uses Vite (`npm run dev`). Build with `npm run build`.

## Notes

- CliniRAG demo data/helpers: `src/lib/clinirag-data.ts`
- Auth / Supabase: see `.env.example` and `supabase/`
- Source upstream: `git@github.com:ahmed-nagah-r/cheerful-digital-garden.git`
