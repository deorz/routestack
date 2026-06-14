# RouteStack

Self-hosted web panel for configuring and managing VPN and proxy protocols.

## Runtime

The project targets Python `>=3.13,<3.15`. Development can use Python 3.14
free-threaded builds, but production code must stay compatible with Python 3.13.

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
docker compose up --build routestack-app
```

Run tests inside Docker without host Python dependencies:

```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm routestack-test
```

Start out-of-process integration dependencies:

```bash
docker compose --profile integration up -d routestack-postgres routestack-redis
```

Run the integration test container with those dependencies:

```bash
docker compose -f docker-compose.yml -f compose.test.yml --profile integration run --rm routestack-test-integration
```
