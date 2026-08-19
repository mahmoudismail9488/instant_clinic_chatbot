# Deploy frontend to Vercel

The UI is a TanStack Start / Vite app under `frontend/` with Nitro preset **`vercel`**.

## 1. Project settings

- **Root Directory:** `frontend`
- **Install:** `npm install`
- **Build:** `npm run build`
- **Output:** handled by Nitro Vercel preset (`.vercel/output` / server functions)

`frontend/vercel.json` sets install/build commands.

## 2. Environment variables

| Name | Value |
|---|---|
| `VITE_API_URL` | Public HTTPS URL of the AWS API (no trailing slash) |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Supabase anon/publishable key |

Optional: `NITRO_PRESET=vercel` (already default in `vite.config.ts`).

## 3. CORS on the API

After you have the Vercel URL (e.g. `https://glucorag.vercel.app`), set on AWS:

```bash
CORS_ORIGINS=https://glucorag.vercel.app
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
```

## 4. Local verify

```bash
cd frontend
npm run build
npx vite preview
```

## 5. CLI deploy (optional)

```bash
cd frontend
npx vercel --prod
```
