.PHONY: help install test lint format clean docker-build docker-run

help:
	@echo "Advanced AI Agent - Makefile Commands"
	@echo "======================================"
	@echo "install         - Install dependencies"
	@echo "install-dev     - Install dev dependencies"
	@echo "test            - Run tests"
	@echo "test-cov        - Run tests with coverage"
	@echo "lint            - Run all linters"
	@echo "format          - Format code with black and isort"
	@echo "type-check      - Run mypy type checking"
	@echo "security        - Run security checks"
	@echo "clean           - Clean build artifacts"
	@echo "docker-build    - Build Docker image"
	@echo "docker-run      - Run Docker container"
	@echo "docker-compose  - Run with docker-compose"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-asyncio black flake8 mypy isort bandit safety pre-commit
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=agent --cov-report=html --cov-report=term-missing

lint:
	flake8 agent/ tests/
	mypy agent/
	bandit -r agent/ -ll

format:
	black agent/ tests/ examples/
	isort agent/ tests/ examples/

type-check:
	mypy agent/ --ignore-missing-imports

security:
	bandit -r agent/ -ll
	safety check

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf build/ dist/ *.egg-info htmlcov/ .pytest_cache/ .mypy_cache/ .tox/

docker-build:
	docker build -t advanced-ai-agent:latest .

docker-run:
	docker run -it --rm \
		-v $$(pwd)/data:/app/data \
		-v $$(pwd)/logs:/app/logs \
		advanced-ai-agent:latest

docker-compose:
	docker-compose up -d

docker-compose-down:
	docker-compose down -v

pre-commit:
	pre-commit run --all-files

all: format lint test
