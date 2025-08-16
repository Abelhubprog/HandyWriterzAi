# HandyWriterzAI — Dev Environment and Runtime Guide

This guide summarizes the environment variables, proxying, and startup steps for a smooth local dev loop with direct provider APIs and SSE streaming.

## Environment Overview

- Backend (.env or backend/.env)
  - `OPENAI_API_KEY`: REQUIRED for direct OpenAI usage (planner/research models).
  - `GEMINI_API_KEY`: Recommended for writer/formatter models.
  - `ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY`: Optional (if used by policies).
  - `APP_URL`: Set to frontend origin (default `http://localhost:3000`). Used for provider headers.
  - `REDIS_URL`: Default `redis://localhost:6379`. Required for SSE.
  - `DATABASE_URL`: Optional in dev; streaming works without DB.
  - `CREDITS_ENFORCE`: Default `false` in dev (prevents preflight credit blocking).

- Frontend (.env.development or .env.local)
  - `BACKEND_URL`: Backend origin for Next.js rewrite (default `http://localhost:8000`).
  - `NEXT_PUBLIC_BACKEND_URL`: Public mirror of backend origin; used in app/api routes.
  - `NEXT_PUBLIC_API_BASE_URL`: Optional; used for server-side fetches.
  - Browser requests use relative paths via Next.js API routes (proxy) — no CORS in dev.

## How Requests Flow

- POST Chat: Browser → Next `/api/chat` → Backend `/api/chat` → returns `{trace_id}`.
- SSE Stream: Browser → Next `/api/chat/stream/{trace_id}` → Backend `/api/stream/{trace_id}`
  - Next API route forwards SSE bytes unmodified; the UI listens for progress, token deltas, and `credits:used` events.

## Providers (Direct APIs)

- Research/Planning: direct OpenAI models via `OPENAI_API_KEY` (e.g., `o3`, `gpt-5`).
- Writing/Formatting: direct Gemini (`gemini-2.5-pro` / `gemini-2.5-flash`) via `GEMINI_API_KEY`.
- OpenRouter: disabled by default; not required in dev.

## Credits (Dev Defaults)

- `CREDITS_ENFORCE=false`: No preflight reservation; calls won’t be blocked for lack of credits.
- Credits are still recorded and emitted in SSE (`credits:used`) for UI display.

## Startup Checklist

1) Redis for SSE
   - `docker run -d --name handywriterz-redis -p 6379:6379 redis:7-alpine`

2) Backend (Python 3.12 venv)
   - `source .venv/bin/activate`
   - Set env: `OPENAI_API_KEY=...`, `GEMINI_API_KEY=...` (and optionally others)
   - `python backend/start_server.py`
   - Health check: `curl -s http://localhost:8000/health/ready`

3) Frontend (Next.js)
   - `cd frontend && pnpm dev` (or `npm run dev`)
   - Open `http://localhost:3000`

## Troubleshooting

- 503 on `/api/chat`:
  - Backend not reachable; check backend logs and ensure `BACKEND_URL` points to `http://localhost:8000` in frontend envs.

- 500 on `/api/chat/stream/{trace_id}`:
  - Redis not running; SSE requires Redis.

- “Insufficient credits” error:
  - Ensure `CREDITS_ENFORCE=false` in dev, or raise user tier via admin endpoint.

- No streaming tokens:
  - Verify SSE events in browser Network tab; backend logs should show route `/api/stream/{trace_id}` connected.

## Useful Endpoints

- User credits: `GET /api/credits/me`
- Estimate credits: `POST /api/credits/estimate`
- Admin credits: `GET /api/admin/credits/{user}`, `PUT /api/admin/credits/{user}/tier`

