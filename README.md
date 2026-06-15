# RouteStack

Self-hosted web panel for configuring and managing VPN and proxy protocols.

## Runtime

The project targets Python `3.13`. Development, CI, and production should use
the same minor version to keep runtime behavior and code style predictable.

## Dependencies

Production dependencies live in `[project].dependencies`.
Development-only tools live in `[dependency-groups].dev`.

Install production dependencies only:

```bash
uv sync --no-dev
```

Install the development environment:

```bash
uv sync --group dev
```

## Development

Run tests:

```bash
uv run --group dev pytest
```

Run lint checks:

```bash
uv run --group dev ruff check .
```

Start the local HTTP app:

```bash
uv run python main.py
```

## Docker

Build and run the app container:

```bash
docker compose up --build app
```

Run tests inside Docker without host Python dependencies:

```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test
```
