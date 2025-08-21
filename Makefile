# Load .env if available
ifneq (,$(wildcard .env))
include .env
export
ENV_FILE_PARAM = --env-file .env
endif

help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build and start containers
	docker compose up --build -d --remove-orphans

up: ## Start containers
	docker compose up -d
	docker compose down -v   # optional: remove old containers and volumes if DB creds changed
    docker compose up -d --build


down: ## Stop containers
	docker compose down

show-logs: ## Show logs
	docker compose logs

migrate: ## Run Django migrations
	docker compose exec api python3 manage.py migrate

makemigrations: ## Create Django migrations
	docker compose exec api python3 manage.py makemigrations

superuser: ## Create superuser
	docker compose exec api python3 manage.py createsuperuser

collectstatic: ## Collect static files
	docker compose exec api python3 manage.py collectstatic --no-input --clear

down-v: ## Stop containers and remove volumes
	docker compose down -v

volume: ## Inspect volume
	docker volume inspect estate-src_postgres_data

estate-db: ## Access Postgres CLI
	docker compose exec postgres-db psql --username=admin --dbname=estate

test: ## Run tests
	docker compose exec api pytest -p no:warnings --cov=.

test-html: ## Run tests with HTML coverage report
	docker compose exec api pytest -p no:warnings --cov=. --cov-report html

flake8: ## Lint code with flake8
	docker compose exec api flake8 .

black-check: ## Check black formatting
	docker compose exec api black --check --exclude=migrations .

black-diff: ## Show black formatting diff
	docker compose exec api black --diff --exclude=migrations .

black: ## Format code with black
	docker compose exec api black --exclude=migrations .

isort-check: ## Check import order
	docker compose exec api isort . --check-only --skip env --skip migrations

isort-diff: ## Show import order diff
	docker compose exec api isort . --diff --skip env --skip migrations

isort: ## Auto sort imports
	docker compose exec api isort . --skip env --skip migrations

shell: ## Django shell
	docker compose exec api python3 manage.py shell

lint: flake8 black-check isort-check ## Run all code quality checks

reset-db: down-v build migrate superuser ## Full reset of DB and setup