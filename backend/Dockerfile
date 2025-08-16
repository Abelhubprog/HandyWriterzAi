# Stage 1: Dependencies Builder
FROM python:3.11-slim as dependencies

# Set environment variables for build optimization
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip to latest version
RUN pip install --upgrade pip wheel setuptools

# Copy and install requirements with caching
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-deps -r requirements.txt && \
    pip install --no-deps --no-binary :all: psycopg2-binary && \
    pip cache purge

# Stage 2: Production Runtime
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy virtual environment from dependencies stage
COPY --from=dependencies /opt/venv /opt/venv

# Create non-root user for security
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
# Bind to PORT if provided (Railway/Heroku), else default to 8000
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-2} --log-level info"]

# Stage 3: Development Runtime (optional)
FROM production as development

# Switch back to root to install dev dependencies
USER root

# Install development dependencies
COPY requirements-dev.txt* ./
RUN if [ -f requirements-dev.txt ]; then \
    pip install -r requirements-dev.txt; \
    fi

# Switch back to appuser
USER appuser

# Development command with hot reload
CMD ["uvicorn", "handywriterz_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
