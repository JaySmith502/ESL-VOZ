.PHONY: dev db migrate lint-content test-backend test-acceptance backend frontend seed deploy prod down

dev: db
	@echo "Starting backend and frontend dev servers..."
	$(MAKE) backend &
	$(MAKE) frontend

install:
	cd backend && uv sync --extra dev
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

db:
	docker compose -f infra/docker-compose.yml up -d
	@echo "Waiting for Postgres..."
	@sleep 3
	$(MAKE) migrate
	$(MAKE) seed

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m scripts.seed_lessons

lint-content:
	backend/.venv/bin/python scripts/lint_lessons.py || python scripts/lint_lessons.py

test-backend:
	cd backend && pytest -q

test-acceptance:
	cd backend && pytest tests/test_acceptance.py -v

test-frontend:
	cd frontend && npm test

test-all: test-backend test-frontend lint-content

prod:
	docker compose -f infra/docker-compose.prod.yml --env-file .env up -d --build

down:
	docker compose -f infra/docker-compose.yml down

down-prod:
	docker compose -f infra/docker-compose.prod.yml down
