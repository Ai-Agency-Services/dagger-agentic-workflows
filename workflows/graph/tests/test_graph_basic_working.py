"""Basic working tests for graph workflow."""

import pytest
from unittest.mock import MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

class TestGraphBasicFunctionality:
    """Basic tests to verify graph workflow setup."""
    
    @pytest.mark.unit
    def test_escape_cypher_string(self):
        """Test Cypher string escaping."""
        from graph.main import Graph
        
        graph = MagicMock(spec=Graph)
        graph._escape_cypher_string = Graph._escape_cypher_string.__get__(graph, Graph)
        
        assert graph._escape_cypher_string("simple") == "simple"
        assert graph._escape_cypher_string('test"quote') == 'test\\"quote'
        assert graph._escape_cypher_string("test'quote") == "test\\'quote"
    
    @pytest.mark.unit
    def test_build_file_cypher(self):
        """Test file Cypher query building."""
        from graph.main import Graph
        
        graph = MagicMock(spec=Graph)
        graph._escape_cypher_string = Graph._escape_cypher_string.__get__(graph, Graph)
        graph._build_file_cypher = Graph._build_file_cypher.__get__(graph, Graph)
        
        query = graph._build_file_cypher("test.py", "python")
        
        assert "MERGE (f:File {filepath: \"test.py\"})" in query
        assert 'language = "python"' in query
        assert query.endswith(';')
    
    @pytest.mark.unit
    def test_build_import_cypher(self):
        """Test import Cypher query building."""
        from graph.main import Graph
        
        graph = MagicMock(spec=Graph)
        graph._escape_cypher_string = Graph._escape_cypher_string.__get__(graph, Graph)
        graph._build_import_cypher = Graph._build_import_cypher.__get__(graph, Graph)
        
        query = graph._build_import_cypher("file1.py", "file2.py")
        
        assert "MERGE (from:File {filepath: \"file1.py\"})" in query
        assert "MERGE (to:File {filepath: \"file2.py\"})" in query
        assert "MERGE (from)-[:IMPORTS]->(to)" in query
    
    @pytest.mark.unit
    def test_resolve_relative_import_basic(self):
        """Test basic relative import resolution."""
        from graph.main import Graph
        
        graph = MagicMock(spec=Graph)
        graph._resolve_relative_import = Graph._resolve_relative_import.__get__(graph, Graph)
        
        # Test same directory import
        result = graph._resolve_relative_import("src/main.py", "./utils")
        assert "src/utils" in result
        
        # Test absolute import (should return None)
        result = graph._resolve_relative_import("src/main.py", "absolute_module")
        assert result is None
    
    @pytest.mark.graph
    def test_graph_marker_works(self):
        """Test that graph marker works."""
        assert True