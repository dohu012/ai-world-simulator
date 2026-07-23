.PHONY: dev infra-up infra-down backend-dev frontend-dev test lint format migrate migration-check

dev:
	@echo "Run 'make infra-up', then start backend and frontend in separate terminals."

infra-up:
	docker compose up -d postgres redis

infra-down:
	docker compose down

backend-dev:
	cd backend && python -m uvicorn app.main:app --reload

frontend-dev:
	cd frontend && npm run dev

test:
	cd backend && python -m pytest
	cd frontend && npm run test

lint:
	cd backend && python -m ruff check . && python -m mypy app
	cd frontend && npm run lint

format:
	cd backend && python -m ruff format . && python -m ruff check --fix .
	cd frontend && npm run format

migrate:
	cd backend && python -m alembic upgrade head

migration-check:
	cd backend && python -m alembic check

