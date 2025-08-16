# Running the Multi-Agent Application Locally

This guide provides instructions on how to set up and run the backend and frontend services for the multi-agent application.

## Quick Start

1.  **Configure Backend:** From the project root, copy `backend/.env.example` to `backend/.env` and fill in your API keys.
2.  **Configure Frontend:** From the project root, copy `frontend/.env.example` to `frontend/.env.local` and fill in the required variables.
3.  **Run Backend Services:** From the project root, run `docker-compose up --build`. This will start the backend, database, and Redis.
4.  **Run Frontend:** In a **new terminal**, navigate to the `frontend` directory (`cd frontend`), run `pnpm install`, and then `pnpm run dev`.

---

## Prerequisites

- Docker
- Node.js and pnpm (for frontend)

---

## Detailed Step-by-Step Instructions

### Backend Setup

1.  **Create `.env` file:** From the project root (`d:/MultiAgentWriterz`), run:
    ```bash
    cp backend/.env.example backend/.env
    ```

2.  **Add Secrets:** Edit the newly created `backend/.env` file and fill in your API keys and any other required secrets.

3.  **Run Docker:** From the project root (`d:/MultiAgentWriterz`), run:
    ```bash
    docker-compose up --build
    ```
    This will start the backend, database, and redis services. The backend will be available at `http://localhost:8000`. Keep this terminal running.

### Frontend Setup

**In a new terminal:**

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Create `.env.local` file:**
    ```bash
    cp .env.example .env.local
    ```

3.  **Add Environment Variables:** Edit the newly created `frontend/.env.local` file and fill in the required variables.

4.  **Install Dependencies (IMPORTANT):** You must install dependencies before running the application.
    ```bash
    pnpm install
    ```

5.  **Run Development Server:**
    ```bash
    pnpm run dev
    ```

The frontend will be available at `http://localhost:3000`.

---

## WSL (Ubuntu) Dev Setup

If you are using VS Code in a WSL Ubuntu 24.04 terminal, do not use Windows PowerShell activation paths like `d:/.../.venv/Scripts/activate`. Create/activate a Linux venv inside WSL and run the dev script:

1) Create a Linux venv and install backend deps

```bash
cd /mnt/d/HandyWriterzAi
python3 -m venv .venv
source .venv/bin/activate
make install-deps
```

2) Start dev (Redis + backend + frontend)

```bash
./start-local.sh
```

Notes:
- VS Code is configured to use the WSL venv automatically (`.vscode/settings.json` sets the interpreter to `.venv/bin/python`).
- If you accidentally created a Windows venv, remove it (`rm -rf .venv`) and recreate it from WSL with `python3 -m venv .venv`.
