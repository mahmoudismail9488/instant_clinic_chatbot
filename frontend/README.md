# Instant Clinic frontend

UI from [cheerful-digital-garden](https://github.com/ahmed-nagah-r/cheerful-digital-garden) (Vite + TanStack Start / React).

Talks to the **Day 3 grounded** FastAPI backend via `VITE_API_URL`  
(`src/lib/clinirag-api.ts` → `POST /query`).

## Setup

```bash
# from repo root — start grounded API first
uv run clinic-api

# then frontend
cd frontend
cp .env.example .env
# required:
#   VITE_API_URL=http://localhost:8000
#   VITE_SUPABASE_URL / VITE_SUPABASE_PUBLISHABLE_KEY (auth)
npm install
npm run dev
# → usually http://localhost:8080/
```

CORS on the API already allows `localhost` / `127.0.0.1` on common Vite ports (including **8080**).

## What the workspace does

| Piece | Behavior |
|---|---|
| `src/routes/_authenticated/workspace.tsx` | Live chat (not demo turns) |
| `src/lib/clinirag-api.ts` | Maps API JSON → answer / refusal turns |
| Answer card | Recommendation + claim list + citation chips (doc · page · section) |
| Evidence panel | Retrieved chunks with scores |
| Refusals | Patient-specific, insufficient evidence, out of scope |

Try:

- Supported: *Who should be screened for type 2 diabetes?*
- Refusal: *Do I have diabetes?*

## Notes

- Auth / admin document upload still use **Supabase**
- Upstream: `git@github.com:ahmed-nagah-r/cheerful-digital-garden.git`
- Backend Day 3 docs: [`../docs/day3/CHECKLIST.md`](../docs/day3/CHECKLIST.md)
