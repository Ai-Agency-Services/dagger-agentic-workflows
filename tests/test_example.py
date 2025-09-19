"""Example tests to demonstrate pytest setup for dagger-agents."""

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestProjectSetup:
    """Test basic project setup and configuration."""
    
    def test_imports_work(self):
        """Test that basic imports work."""
        try:
            import dagger
            import yaml
            import pydantic
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
    
    def test_pytest_markers_configured(self, pytestconfig):
        """Test that custom pytest markers are configured."""
        markers = pytestconfig.getini("markers")
        expected_markers = ["slow", "integration", "unit", "neo4j", "llm", "dagger"]
        
        for marker in expected_markers:
            assert any(marker in m for m in markers), f"Marker {marker} not found"
    
    def test_coverage_configured(self, pytestconfig):
        """Test that coverage is configured."""
        addopts = pytestconfig.getini("addopts")
        assert any("--cov" in opt for opt in addopts), "Coverage not configured"
    
    @pytest.mark.unit
    def test_unit_marker_works(self):
        """Test that unit marker works."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker_works(self):
        """Test that integration marker works."""
        assert True


class TestMockFixtures:
    """Test that mock fixtures work correctly."""
    
    def test_mock_neo4j_driver(self, mock_neo4j_driver):
        """Test mock Neo4j driver fixture."""
        assert mock_neo4j_driver is not None
        assert hasattr(mock_neo4j_driver, 'session')
        assert hasattr(mock_neo4j_driver, 'close')
    
    def test_mock_dagger_container(self, mock_dagger_container):
        """Test mock Dagger container fixture."""
        assert mock_dagger_container is not None
        assert hasattr(mock_dagger_container, 'with_exec')
        assert hasattr(mock_dagger_container, 'stdout')
    
    def test_sample_yaml_config(self, sample_yaml_config):
        """Test sample YAML config fixture."""
        assert 'container' in sample_yaml_config
        assert 'git' in sample_yaml_config
        assert 'core_api' in sample_yaml_config
        assert sample_yaml_config['core_api']['model'] == 'gpt-4o-mini'


class TestAsyncSupport:
    """Test async test support."""
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async test execution."""
        async def sample_async_func():
            return "success"
        
        result = await sample_async_func()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_async_mock(self, mock_dagger_container):
        """Test async mock usage."""
        mock_dagger_container.stdout.return_value = "mocked output"
        
        result = await mock_dagger_container.stdout()
        assert result == "mocked output"