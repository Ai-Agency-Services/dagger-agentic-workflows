import sys
from pathlib import Path

# Attempt to add repo root to sys.path so `shared` package can be imported when running from this module only
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    # Ensure shared fixtures (mock_supabase_client, mock_openai_client, etc.) are available
    pytest_plugins = [
        "shared.pytest_plugins.fixtures",
    ]
except Exception:
    # Fallback: define only the fixtures needed by this module's tests
    from unittest.mock import MagicMock
    import pytest

    @pytest.fixture
    def mock_supabase_client():
        return MagicMock()

    @pytest.fixture
    def mock_openai_client():
        client = MagicMock()
        client.embeddings = MagicMock()
        client.embeddings.create = MagicMock()
        return client
