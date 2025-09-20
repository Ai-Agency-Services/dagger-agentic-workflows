# Shared pytest plugin: fixtures usable across all modules
import os
import pytest

# Optional: mark that we are in testing context
os.environ.setdefault("TESTING", "1")

@pytest.fixture
def sample_yaml_config():
    """Sample YAML configuration for tests across modules."""
    return {
        "container": {
            "work_dir": "/app",
            "docker_file_path": "./Dockerfile"
        },
        "git": {
            "user_name": "Test User",
            "user_email": "test@example.com",
            "base_pull_request_branch": "main"
        },
        "core_api": {
            "model": "gpt-4o-mini",
            "provider": "openai"
        },
        "neo4j": {
            "uri": "neo4j://localhost:7687",
            "username": "neo4j",
            "database": "test"
        }
    }

# Add additional shared fixtures (moved from tests/conftest.py)
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator, Generator

@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver for testing."""
    driver = MagicMock()
    driver.session = MagicMock()
    driver.close = MagicMock()
    return driver

@pytest.fixture
def mock_dagger_container():
    """Mock Dagger container for testing."""
    container = AsyncMock()
    container.with_exec = AsyncMock(return_value=container)
    container.stdout = AsyncMock(return_value="test output")
    container.stderr = AsyncMock(return_value="")
    return container

@pytest.fixture
def mock_llm_credentials():
    """Mock LLM credentials for testing."""
    creds = MagicMock()
    creds.api_key = "test-api-key"
    creds.base_url = "https://api.openai.com/v1"
    return creds

@pytest.fixture
def mock_openai_model():
    """Mock OpenAI model for testing."""
    model = AsyncMock()
    model.request = AsyncMock()
    return model

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables for all tests."""
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
    os.environ.setdefault("NEO4J_URI", "neo4j://localhost:7687")
    os.environ.setdefault("NEO4J_USERNAME", "neo4j")
    os.environ.setdefault("NEO4J_PASSWORD", "test")
    yield

@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.py"
    file_path.write_text("def test_function():\n    return True\n")
    return str(file_path)

@pytest.fixture
def mock_code_file():
    """Mock code file for testing."""
    return {
        "path": "test/example.py",
        "content": "def example_function():\n    return 'Hello, World!'",
        "language": "python",
        "symbols": [
            {
                "name": "example_function",
                "type": "function",
                "line_start": 1,
                "line_end": 2
            }
        ]
    }

class AsyncContextManager:
    """Helper class for async context managers in tests."""
    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def async_context_manager():
    """Factory for creating async context managers in tests."""
    return AsyncContextManager
