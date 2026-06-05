include .env
export

.PHONY: up down logs test lint dev help

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f

test:
	pytest tests/ -v --cov=api --cov-fail-under=75

lint:
	flake8 api/ dashboard/ tests/

dev:
	uvicorn api.main:app --reload --port 8000 &
	streamlit run dashboard/app.py

help:
	@echo "Available commands:"
	@echo "  make up       - Start the full stack with Docker"
	@echo "  make down     - Stop and remove containers"
	@echo "  make logs     - Follow container logs"
	@echo "  make test     - Run tests with coverage"
	@echo "  make lint     - Run flake8 linter"
	@echo "  make dev      - Run API + dashboard locally without Docker"