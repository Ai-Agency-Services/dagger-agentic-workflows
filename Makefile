# Makefile for dagger-agents project

.PHONY: help install test test-unit test-integration test-coverage test-all lint format clean

help:
	@echo "Available commands:"
	@echo "  install          - Install dependencies with uv"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage    - Run tests with coverage"
	@echo "  test-all         - Run all tests including slow ones"
	@echo "  lint             - Run linting"
	@echo "  format           - Format code"
	@echo "  clean            - Clean up generated files"

install:
	uv sync --extra test --extra dev

test:
	uv run pytest --maxfail=1 --tb=short -v

test-unit:
	uv run pytest -m "unit" --maxfail=1 --tb=short -v

test-integration:
	uv run pytest -m "integration" --maxfail=1 --tb=short -v

test-coverage:
	uv run pytest --cov --cov-report=term-missing --cov-report=html

test-coverage-all:
	@echo "📊 To run coverage for entire repository, use these commands:"
	@echo "  Root tests:    make test-coverage"
	@echo "  Neo service:   make test-services/neo-coverage"
	@echo "  Graph:         make test-workflows/graph-coverage"
	@echo "  Smell:         make test-workflows/smell-coverage"

test-services/neo-coverage:
	cd services/neo && uv run --extra test pytest tests/test_neo_service_comprehensive.py::TestSymbolProperties --cov=neo --cov-report=html:htmlcov --cov-report=term-missing && echo "✅ Neo coverage: services/neo/htmlcov/index.html"

test-workflows/graph-coverage:
	cd workflows/graph && uv run --extra test pytest tests/test_graph_basic_working.py --cov=graph --cov-report=html:htmlcov --cov-report=term-missing && echo "✅ Graph coverage: workflows/graph/htmlcov/index.html"

test-workflows/smell-coverage:
	cd workflows/smell && uv run --extra test pytest tests/ --cov=smell --cov-report=html:htmlcov --cov-report=term-missing && echo "✅ Smell coverage: workflows/smell/htmlcov/index.html"

test-all:
	uv run pytest --maxfail=1 --tb=short -v -m "not slow" 

test-slow:
	uv run pytest --maxfail=1 --tb=short -v

lint:
	ruff check .
	mypy .

format:
	ruff format .
	black .

clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

# Module-specific testing
test-neo:
	cd services/neo && uv run --extra test pytest

test-services/neo:
	cd services/neo && uv run --extra test pytest

test-query:
	cd services/query && uv run --extra test pytest

test-services/query:
	cd services/query && uv run --extra test pytest

test-index:
	cd workflows/index && uv run --extra test pytest

test-workflows/index:
	cd workflows/index && uv run --extra test pytest

test-graph:
	cd workflows/graph && uv run --extra test pytest

test-workflows/graph:
	cd workflows/graph && uv run --extra test pytest

test-smell:
	cd workflows/smell && uv run --extra test pytest

test-workflows/smell:
	cd workflows/smell && uv run --extra test pytest

test-cover:
	cd workflows/cover && uv run --extra test pytest

test-workflows/cover:
	cd workflows/cover && uv run --extra test pytest

test-codebuff:
	cd agents/codebuff && uv run --extra test pytest

test-agents/codebuff:
	cd agents/codebuff && uv run --extra test pytest

test-builder:
	cd agents/builder && uv run --extra test pytest

test-agents/builder:
	cd agents/builder && uv run --extra test pytest

test-pull-request:
	cd agents/pull_request && uv run --extra test pytest

test-agents/pull_request:
	cd agents/pull_request && uv run --extra test pytest

test-agent-utils:
	cd shared/agent-utils && uv run --extra test pytest

test-shared/agent-utils:
	cd shared/agent-utils && uv run --extra test pytest

# Neo4j specific tests (requires running Neo4j)
test-neo4j:
	uv run pytest -m "neo4j" --tb=short -v

# LLM tests (requires API keys)
test-llm:
	uv run pytest -m "llm" --tb=short -v