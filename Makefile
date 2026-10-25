.PHONY: test coverage lint format docs clean docker help install

help:
	@echo "Available targets:"
	@echo "  install   - Install dependencies with uv"
	@echo "  test      - Run all tests"
	@echo "  coverage  - Run tests with coverage report"
	@echo "  docs      - Run sphinx-build for generating documentation"
	@echo "  lint      - Run linting checks"
	@echo "  format    - Format code with ruff"
	@echo "  docker    - Build Docker image"
	@echo "  clean     - Remove build artifacts"

install:
	uv sync --dev

test: install
	uv run pytest

coverage: install
	uv run pytest --cov=noaa --cov-report=html --cov-report=term-missing

docs: install
	@echo "Building documentation..."
	@rm -rf docs/_build
	cd docs && uv run sphinx-build -b html . _build/html
	@echo "Documentation built in docs/_build/html/index.html"

lint: install
	uv run ruff format --check .
	uv run ruff check .
	uv run pyright src/noaa/

format: install
	uv run ruff format .
	uv run ruff check --fix .

docker:
	@echo "Building Docker image..."
	docker build -t noaa-api:latest .
	@echo "Docker image built successfully"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf docs/_build
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
