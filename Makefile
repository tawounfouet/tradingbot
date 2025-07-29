# Crypto Trading Bot - Makefile
# Convenient commands for development and deployment

.PHONY: help install install-dev test lint format clean run docker-up docker-down

# Default target
help:
	@echo "Crypto Trading Bot - Available Commands:"
	@echo ""
	@echo "Development:"
		@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  run          Run the FastAPI application"
	@echo "  test         Run tests with coverage"
	@echo "  lint         Run linting (flake8, mypy, bandit)"
	@echo "  format       Format code (black, isort)"
	@echo "  clean        Clean up cache files and build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  docs-serve   Serve documentation locally (http://127.0.0.1:8000)"
	@echo "  docs-build   Build documentation site"
	@echo "  docs-deploy  Deploy documentation to GitHub Pages"
	@echo "  docs-clean   Clean documentation build files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up    Start all services with Docker Compose"
	@echo "  docker-down  Stop all Docker services"
	@echo "  docker-logs  Show Docker logs"
	@echo ""
	@echo "Quality:"
	@echo "  check        Run all quality checks (lint + test)"
	@echo "  pre-commit   Install and run pre-commit hooks"

# Python and pip commands (using absolute paths)
PROJECT_DIR := $(shell pwd)
PYTHON := $(PROJECT_DIR)/.venv/bin/python
PIP := $(PROJECT_DIR)/.venv/bin/pip

# Install production dependencies
install:
	$(PIP) install -e .

# Install development dependencies
install-dev:
	$(PIP) install -e ".[dev,test,docs]"
	$(PIP) install pre-commit
	pre-commit install

# Run the FastAPI application
run:
	cd src/tradingbot && $(PYTHON) main.py

# Run tests with coverage
test:
	$(PYTHON) -m pytest --cov=src --cov-report=term-missing --cov-report=html

# Run linting tools
lint:
	@echo "Running flake8..."
	$(PYTHON) -m flake8 src/
	@echo "Running mypy..."
	$(PYTHON) -m mypy src/
	@echo "Running bandit..."
	$(PYTHON) -m bandit -r src/ -f json -o bandit-report.json || true
	@echo "Linting complete!"

# Format code
format:
	@echo "Running black..."
	$(PYTHON) -m black src/
	@echo "Running isort..."
	$(PYTHON) -m isort src/
	@echo "Code formatting complete!"

# Clean up cache files and build artifacts
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .coverage
	@echo "Cleanup complete!"

# Run all quality checks
check: lint test
	@echo "All quality checks passed!"

# Docker commands
docker-up:
	docker-compose up -d
	@echo "All services started! Check status with: docker-compose ps"

docker-down:
	docker-compose down
	@echo "All services stopped!"

docker-logs:
	docker-compose logs -f

# Pre-commit hooks
pre-commit:
	pre-commit install
	pre-commit run --all-files

# Virtual environment setup
venv:
	python3.11 -m venv .venv
	$(PIP) install --upgrade pip setuptools wheel
	@echo "Virtual environment created! Activate with: source .venv/bin/activate"

# Database commands
db-upgrade:
	cd src/tradingbot && $(PYTHON) -m alembic upgrade head

db-downgrade:
	cd src/tradingbot && $(PYTHON) -m alembic downgrade -1

db-migration:
	cd src/tradingbot && $(PYTHON) -m alembic revision --autogenerate -m "$(MESSAGE)"

# Development server with auto-reload
dev:
	cd src/tradingbot && $(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
prod:
	cd src/tradingbot && $(PYTHON) -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Health check
health:
	curl -f http://localhost:8000/health || echo "Service is not running"

# Documentation commands
docs-serve:
	$(PYTHON) -m mkdocs serve

docs-build:
	$(PYTHON) -m mkdocs build

docs-deploy:
	$(PYTHON) -m mkdocs gh-deploy --force

docs-clean:
	rm -rf site/

# Show project info
info:
	@echo "Project: Crypto Trading Bot API"
	@echo "Python version: $(shell $(PYTHON) --version)"
	@echo "Virtual environment: $(shell which python)"
	@echo "Dependencies:"
	@$(PIP) list | grep -E "(fastapi|uvicorn|pydantic|sqlalchemy)"
