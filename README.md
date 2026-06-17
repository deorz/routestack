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
make requirements
```

## Development

Run tests:

```bash
make test
```

Run lint and type checks:

```bash
make lint
make format
make check
```

Start the local HTTP app:

```bash
make start
```

Copy `.env-defaults` into `.env` and override secrets before non-local deployment.

## Docker

Build and run the app container:

```bash
make start
```

Run tests inside Docker without host Python dependencies:

```bash
make docker-test
```
