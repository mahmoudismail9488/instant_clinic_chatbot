# syntax=docker/dockerfile:1
# AWS-ready GlucoRAG API image (App Runner / ECS Fargate / EC2).
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# System deps for scientific wheels / SSL
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv then project deps (API runtime only — no torch/CUDA eval extras)
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock README.md ./
COPY backend ./backend
# Pre-built vector index (rebuild in CI if guidelines change)
COPY data/index ./data/index
COPY data/raw_guidelines ./data/raw_guidelines

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH" \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    API_WORKERS=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Use the venv binary directly (avoid `uv run` rebuild delay on every boot).
CMD [".venv/bin/clinic-api"]
