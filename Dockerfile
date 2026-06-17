# syntax=docker/dockerfile:1.7

FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock README.md ./

FROM base AS runtime-deps

RUN uv sync --frozen --no-dev --no-install-project

FROM base AS test-deps

RUN uv sync --frozen --group dev --no-install-project

FROM runtime-deps AS runtime

COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations

EXPOSE 8000

CMD ["python", "src/manage.py"]

FROM test-deps AS test

COPY src ./src
COPY tests ./tests
COPY alembic.ini ./
COPY migrations ./migrations
COPY Dockerfile docker-compose.yml compose.test.yml .dockerignore ./

CMD ["uv", "run", "--group", "dev", "pytest"]
