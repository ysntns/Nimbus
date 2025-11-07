# Nimbus Development Makefile

.PHONY: help install test lint format clean run gui docs

help:
	@echo "Nimbus Development Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make run        - Run CLI"
	@echo "  make gui        - Run GUI"
	@echo "  make docs       - Generate documentation"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app/ tests/
	mypy app/
	black --check app/ tests/
	isort --check-only app/ tests/

format:
	black app/ tests/
	isort app/ tests/

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python3 -m app.cli.main --help

gui:
	python3 -m app.gui.main

docs:
	@echo "Documentation generation coming soon..."

.DEFAULT_GOAL := help
