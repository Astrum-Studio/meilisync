FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN groupadd --system --gid 1000 appgroup && \
    useradd --system --uid 1000 --gid 1000 --home-dir /home/appuser --create-home appuser

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      curl \
      ca-certificates \
      gcc \
      pkg-config \
      libffi-dev \
      make; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_HTTP_TIMEOUT=300
ENV UV_LINK_MODE=copy

COPY --chown=appuser:appgroup pyproject.toml uv.lock /app/

RUN uv sync --no-install-project --extra postgres

COPY --chown=appuser:appgroup . /app

RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "meilisync", "start"]
