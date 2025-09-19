"""Basic tests for graph workflow."""

import pytest


class TestGraphBasic:
    """Basic tests to verify graph workflow setup."""
    
    @pytest.mark.unit
    def test_basic_import(self):
        """Test that basic imports work."""
        try:
            import yaml
            import pydantic
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
    
    @pytest.mark.graph
    def test_graph_marker_works(self):
        """Test that graph marker works."""
        assert True