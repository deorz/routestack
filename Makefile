target ?= tests
rev ?= head

requirements:
	uv sync --group dev

start:
	docker compose up --build -d app

stop:
	docker compose stop

# Migrations
migrations:
	uv run alembic upgrade head

create_migration:
	uv run alembic revision --autogenerate --message "$(name)"

docker-migrations-create:
	docker compose run --rm app alembic revision --autogenerate -m "$(msg)"

docker-migrations-up:
	docker compose run --rm app alembic upgrade $(rev)

docker-migrations-down:
	docker compose run --rm app alembic downgrade $(rev)

# Formatting
ruff-format:
	uv run --group dev ruff format $(arg1) .

ruff-isort:
	uv run --group dev ruff check --select I --fix .

format: ruff-isort ruff-format

# Linting
ruff-check:
	uv run --group dev ruff check $(arg1) .

ruff-format-check:
	uv run --group dev ruff format --check .

pyrefly:
	uv run --group dev pyrefly check

bandit:
	uv run --group dev bandit -q -r src

lint: bandit ruff-check ruff-format-check pyrefly

docker-build-test:
	docker compose -f docker-compose.yml -f compose.test.yml build test

docker-lint: docker-build-test
	docker compose -f docker-compose.yml -f compose.test.yml run --rm test uv run --group dev bandit -q -r src
	docker compose -f docker-compose.yml -f compose.test.yml run --rm test uv run --group dev ruff check .
	docker compose -f docker-compose.yml -f compose.test.yml run --rm test uv run --group dev ruff format --check .
	docker compose -f docker-compose.yml -f compose.test.yml run --rm test uv run --group dev pyrefly check

# Tests
test:
	uv run --group dev pytest -vv $(target) $(or $(foreach var,$(ignore),--ignore=$(var)))

docker-test: docker-build-test
	docker compose -f docker-compose.yml -f compose.test.yml run --rm test uv run --group dev pytest -vv $(target) $(or $(foreach var,$(ignore),--ignore=$(var)))

check: format lint test

docker-check: docker-format docker-lint docker-test

docker-format: docker-build-test
	docker compose -f docker-compose.yml -f compose.test.yml run --rm test uv run --group dev ruff check --select I .
	docker compose -f docker-compose.yml -f compose.test.yml run --rm test uv run --group dev ruff format --check .
