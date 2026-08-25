# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_HTTP_TIMEOUT=300 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc pkg-config libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY meilisync ./meilisync

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --extra all --no-editable

FROM python:3.13-slim-bookworm AS runtime

RUN groupadd --system --gid 1000 appgroup \
    && useradd --system --uid 1000 --gid 1000 --home-dir /home/appuser --create-home appuser

WORKDIR /app

RUN mkdir -p /app/data \
    && chown -R appuser:appgroup /app

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --chown=appuser:appgroup config.example.yml /app/config.example.yml

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

CMD ["meilisync", "start"]
