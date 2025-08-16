Fast local dev tips

- Backend (FastAPI/Uvicorn)
  - Reload limited to backend folder only; avoids scanning node_modules and .next
  - DB connects fail fast (3s timeout). Set DEV_DB_FALLBACK=true to auto-fallback to SQLite if Postgres is down
  - Redis ping uses 2s timeout; set REDIS_PING_TIMEOUT env to adjust

- Frontend (Next.js)
  - Turbopack enabled in dev; modularized imports via optimizePackageImports
  - Lint and typecheck skipped during prod build (CI can re-enable)
  - Tailwind scans only needed folders

Run locally

1) Backend
   - VS Code task: Run Backend (cwd=backend)
   - Or: cd backend; python start_server.py

2) Frontend
   - VS Code task: Run Frontend (cwd=frontend)
   - Or: cd frontend; pnpm dev

3) Both
   - VS Code task: Run Both (Frontend + Backend)

Env knobs

- DB_CONNECT_TIMEOUT=3
- DEV_DB_FALLBACK=true
- DEV_FALLBACK_DB_URL=sqlite:///./handywriterz_dev.db
- REDIS_PING_TIMEOUT=2
