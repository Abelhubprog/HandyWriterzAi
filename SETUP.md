# Setup Guide

This document provides detailed instructions for setting up the development environment for the Multi-Agent AI Platform.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Python 3.11+**
*   **Node.js 18+** and **npm**
*   **PostgreSQL**
*   **Redis**
*   **Docker** and **Docker Compose** (for production deployment)

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/multiagent-platform.git
cd multiagent-platform
```

## 2. Configure Environment Variables

The application requires a number of environment variables to be set, including API keys for the various AI providers.

1.  **Copy the example environment file:**

    ```bash
    cp backend/backend/.env.example backend/backend/.env
    ```

2.  **Edit the `.env` file:**

    Open the `backend/backend/.env` file and fill in the required values for the following variables:

    *   `GEMINI_API_KEY`
    *   `ANTHROPIC_API_KEY`
    *   `OPENAI_API_KEY`
    *   `PERPLEXITY_API_KEY`
    *   `DEEPSEEK_API_KEY`
    *   `QWEN_API_KEY`
    *   `GROK_API_KEY`
    *   `GITHUB_TOKEN`
    *   `DATABASE_URL`
    *   `REDIS_URL`
    *   `SUPABASE_URL`
    *   `SUPABASE_KEY`
    *   `JWT_SECRET_KEY`
    *   ...and so on for all the variables in the file.

## 3. Run the Setup Script

The `setup.sh` script automates the process of setting up the Python virtual environment, installing dependencies, and configuring the database.

```bash
cd backend/backend
./scripts/setup.sh
```

This script will:

*   Create a Python virtual environment in `.venv/`.
*   Install all the required Python dependencies from `requirements.txt`.
*   Create the `handywriterz` PostgreSQL database if it doesn't already exist.
*   Enable the `pgvector` extension in the database.
*   Start the Redis server if it's not already running.
*   Run the Alembic database migrations to create the necessary tables.

## 4. Start the Application

Once the setup is complete, you can start the application using the following commands:

### Backend

```bash
cd backend/backend
uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

## 5. Production Deployment

For production deployment, you can use the provided Docker Compose files.

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

This will start all the necessary services in detached mode.