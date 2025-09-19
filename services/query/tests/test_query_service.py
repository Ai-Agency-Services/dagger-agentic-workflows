"""Comprehensive unit tests for QueryService."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


class TestQueryServiceCreation:
    """Test QueryService creation and initialization."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.yaml.safe_load')
    async def test_create_service_success(self, mock_yaml_load):
        """Test successful QueryService creation."""
        from query.main import QueryService
        
        mock_config = {
            "integration": {
                "cache_enabled": True,
                "cache_ttl": 7200,
                "parallel_processing": False,
                "embedding_dimension": 1024
            },
            "supabase": {
                "url": "https://test.supabase.co"
            }
        }
        mock_yaml_load.return_value = mock_config
        
        mock_file = AsyncMock()
        mock_file.contents = AsyncMock(return_value="config content")
        
        service = await QueryService.create(
            config_file=mock_file,
            open_router_api_key=MagicMock(),
            supabase_key=MagicMock(),
            neo_data=MagicMock(),
            neo_password=MagicMock(),
            supabase_url="https://test.supabase.co",
            github_access_token=MagicMock(),
            neo_auth=MagicMock()
        )
        
        assert service.config == mock_config
        assert service.cache_enabled is True
        assert service.cache_ttl == 7200
        assert service.parallel_processing is False
        assert service.embedding_dimension == 1024

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.yaml.safe_load')
    async def test_create_service_with_defaults(self, mock_yaml_load):
        """Test QueryService creation with default values."""
        from query.main import QueryService
        
        mock_config = {}  # Empty config
        mock_yaml_load.return_value = mock_config
        
        mock_file = AsyncMock()
        mock_file.contents = AsyncMock(return_value="{}")
        
        service = await QueryService.create(
            config_file=mock_file,
            open_router_api_key=MagicMock(),
            supabase_key=MagicMock(),
            neo_data=MagicMock(),
            neo_password=MagicMock(),
            supabase_url="https://test.supabase.co",
            github_access_token=MagicMock(),
            neo_auth=MagicMock()
        )
        
        # Check default values
        assert service.cache_enabled is True
        assert service.cache_ttl == 3600
        assert service.parallel_processing is True
        assert service.embedding_dimension == 1536

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.yaml.safe_load')
    async def test_create_service_invalid_config(self, mock_yaml_load):
        """Test QueryService creation with invalid config."""
        from query.main import QueryService
        
        mock_yaml_load.return_value = None  # Invalid config
        
        mock_file = AsyncMock()
        mock_file.contents = AsyncMock(return_value="invalid yaml")
        
        with pytest.raises(ValueError, match="Config file is empty or invalid YAML"):
            await QueryService.create(
                config_file=mock_file,
                open_router_api_key=MagicMock(),
                supabase_key=MagicMock(),
                neo_data=MagicMock(),
                neo_password=MagicMock(),
                supabase_url="https://test.supabase.co",
                github_access_token=MagicMock(),
                neo_auth=MagicMock()
            )


class TestQueryServiceMethods:
    """Test QueryService main methods."""

    @pytest.mark.unit
    def test_get_logger(self):
        """Test logger creation and caching."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service._logger = None
        service._get_logger = QueryService._get_logger.__get__(service, QueryService)
        
        # First call should create logger
        logger1 = service._get_logger()
        assert logger1 is not None
        
        # Second call should return cached logger
        logger2 = service._get_logger()
        assert logger1 is logger2

    @pytest.mark.unit
    def test_parse_cypher_result_empty(self):
        """Test parsing empty Cypher results."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service._get_logger = MagicMock(return_value=MagicMock())
        service._parse_cypher_result = QueryService._parse_cypher_result.__get__(service, QueryService)
        
        result = service._parse_cypher_result("", ["col1", "col2"])
        assert result == []
        
        result = service._parse_cypher_result("header\n", ["col1", "col2"])
        assert result == []

    @pytest.mark.unit
    def test_parse_cypher_result_with_data(self):
        """Test parsing Cypher results with data."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service._get_logger = MagicMock(return_value=MagicMock())
        service._parse_cypher_result = QueryService._parse_cypher_result.__get__(service, QueryService)
        
        cypher_output = "name type filepath\ntest_func function test.py\nTestClass class main.py"
        columns = ["name", "type", "filepath"]
        
        result = service._parse_cypher_result(cypher_output, columns)
        
        assert len(result) == 2
        assert result[0] == {"name": "test_func", "type": "function", "filepath": "test.py"}
        assert result[1] == {"name": "TestClass", "type": "class", "filepath": "main.py"}

    @pytest.mark.unit
    def test_format_result(self):
        """Test result formatting."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service._get_logger = MagicMock(return_value=MagicMock())
        service._format_result = QueryService._format_result.__get__(service, QueryService)
        
        result_data = {
            "semantic_results": [
                {
                    "filepath": "test.py",
                    "content": "def test(): pass",
                    "score": 0.95,
                    "language": "python"
                }
            ],
            "structural_data": {
                "symbols": [
                    {"name": "test", "type": "function", "filepath": "test.py"}
                ]
            }
        }
        
        formatted = service._format_result(result_data)
        
        assert "=== Code Query Results ===" in formatted
        assert "test.py" in formatted
        assert "score: 0.95" in formatted
        assert "def test(): pass" in formatted

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalidate_cache(self):
        """Test cache invalidation."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service.invalidate_cache = QueryService.invalidate_cache.__get__(service, QueryService)
        
        result = await service.invalidate_cache("test.py")
        assert "test.py" in result
        
        result = await service.invalidate_cache()
        assert "all files" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_file_details(self):
        """Test get_file_details method."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service.get_file_details = QueryService.get_file_details.__get__(service, QueryService)
        
        result = await service.get_file_details("test.py")
        
        assert "test.py" in result
        assert "File Information:" in result
        assert "Language: py" in result


class TestQueryServiceSemanticSearch:
    """Test semantic search functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.create_client')
    @patch('query.main.openai.OpenAI')
    async def test_semantic_search_success(self, mock_openai, mock_create_client, mock_supabase_client, mock_openai_client):
        """Test successful semantic search."""
        from query.main import QueryService
        
        # Setup mocks
        mock_create_client.return_value = mock_supabase_client
        mock_openai.return_value = mock_openai_client
        
        # Mock embedding response
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_openai_client.embeddings.create.return_value = mock_embedding_response
        
        # Mock Supabase response
        mock_response = MagicMock()
        mock_response.data = [
            {
                "filepath": "test.py",
                "content": "def test(): pass",
                "similarity": 0.95,
                "language": "python"
            }
        ]
        mock_response.execute.return_value = mock_response
        mock_supabase_client.rpc.return_value = mock_response
        
        # Create service
        service = MagicMock(spec=QueryService)
        service.supabase_url = "https://test.supabase.co"
        service.supabase_key = AsyncMock()
        service.supabase_key.plaintext = AsyncMock(return_value="test-key")
        service.open_router_api_key = AsyncMock()
        service.open_router_api_key.plaintext = AsyncMock(return_value="test-openai-key")
        service.embedding_dimension = 1536
        service._get_logger = MagicMock(return_value=MagicMock())
        
        service._semantic_search = QueryService._semantic_search.__get__(service, QueryService)
        
        result = await service._semantic_search("test query", 0.5, 10)
        
        assert len(result) == 1
        assert result[0]["filepath"] == "test.py"
        assert result[0]["score"] == 0.95
        mock_openai_client.embeddings.create.assert_called_once()
        mock_supabase_client.rpc.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.create_client')
    @patch('query.main.openai.OpenAI')
    async def test_semantic_search_no_results(self, mock_openai, mock_create_client, mock_supabase_client, mock_openai_client):
        """Test semantic search with no results."""
        from query.main import QueryService
        
        # Setup mocks
        mock_create_client.return_value = mock_supabase_client
        mock_openai.return_value = mock_openai_client
        
        # Mock embedding response
        mock_embedding_response = MagicMock()
        mock_embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_openai_client.embeddings.create.return_value = mock_embedding_response
        
        # Mock empty Supabase response
        mock_response = MagicMock()
        mock_response.data = []
        mock_response.execute.return_value = mock_response
        mock_supabase_client.rpc.return_value = mock_response
        
        # Create service
        service = MagicMock(spec=QueryService)
        service.supabase_url = "https://test.supabase.co"
        service.supabase_key = AsyncMock()
        service.supabase_key.plaintext = AsyncMock(return_value="test-key")
        service.open_router_api_key = AsyncMock()
        service.open_router_api_key.plaintext = AsyncMock(return_value="test-openai-key")
        service.embedding_dimension = 1536
        service._get_logger = MagicMock(return_value=MagicMock())
        
        service._semantic_search = QueryService._semantic_search.__get__(service, QueryService)
        
        result = await service._semantic_search("test query", 0.9, 10)
        
        assert result == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.create_client')
    @patch('query.main.openai.OpenAI')
    async def test_semantic_search_error_handling(self, mock_openai, mock_create_client):
        """Test semantic search error handling."""
        from query.main import QueryService
        
        # Setup mocks to raise exception
        mock_create_client.side_effect = Exception("Supabase connection failed")
        
        service = MagicMock(spec=QueryService)
        service.supabase_url = "https://test.supabase.co"
        service.supabase_key = AsyncMock()
        service.supabase_key.plaintext = AsyncMock(return_value="test-key")
        service.open_router_api_key = AsyncMock()
        service.open_router_api_key.plaintext = AsyncMock(return_value="test-openai-key")
        service._get_logger = MagicMock(return_value=MagicMock())
        
        service._semantic_search = QueryService._semantic_search.__get__(service, QueryService)
        
        result = await service._semantic_search("test query", 0.5, 10)
        
        assert result == []


class TestQueryServiceStructuralData:
    """Test structural data retrieval."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.dag')
    async def test_get_structural_data_success(self, mock_dag, sample_structural_data):
        """Test successful structural data retrieval."""
        from query.main import QueryService
        
        # Mock Neo4j service
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query = AsyncMock(side_effect=[
            "name type filepath\ntest_func function test.py",  # symbols query
            "source_file imported_file\ntest.py utils.py",  # imports query  
            "symbol_name symbol_type defined_in\ntest_func function test.py"  # references query
        ])
        mock_dag.neo_service.return_value = mock_neo_service
        
        service = MagicMock(spec=QueryService)
        service.config_file = MagicMock()
        service.neo_password = MagicMock()
        service.github_access_token = MagicMock()
        service.neo_auth = MagicMock()
        service.neo_data = MagicMock()
        service._get_logger = MagicMock(return_value=MagicMock())
        service._parse_cypher_result = QueryService._parse_cypher_result.__get__(service, QueryService)
        
        service._get_structural_data = QueryService._get_structural_data.__get__(service, QueryService)
        
        result = await service._get_structural_data(["test.py"], "test question")
        
        assert "symbols" in result
        assert "imports" in result
        assert "references" in result
        assert len(result["symbols"]) == 1
        assert len(result["imports"]) == 1
        assert len(result["references"]) == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.dag')
    async def test_get_structural_data_empty_files(self, mock_dag):
        """Test structural data retrieval with empty file list."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service._get_logger = MagicMock(return_value=MagicMock())
        
        service._get_structural_data = QueryService._get_structural_data.__get__(service, QueryService)
        
        result = await service._get_structural_data([], "test question")
        
        assert result == {"symbols": [], "imports": [], "references": []}

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('query.main.dag')
    async def test_get_structural_data_with_error(self, mock_dag):
        """Test structural data retrieval with query errors."""
        from query.main import QueryService
        
        # Mock Neo4j service that fails
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query = AsyncMock(side_effect=Exception("Query failed"))
        mock_dag.neo_service.return_value = mock_neo_service
        
        service = MagicMock(spec=QueryService)
        service.config_file = MagicMock()
        service.neo_password = MagicMock()
        service.github_access_token = MagicMock()
        service.neo_auth = MagicMock()
        service.neo_data = MagicMock()
        service._get_logger = MagicMock(return_value=MagicMock())
        service._parse_cypher_result = QueryService._parse_cypher_result.__get__(service, QueryService)
        
        service._get_structural_data = QueryService._get_structural_data.__get__(service, QueryService)
        
        result = await service._get_structural_data(["test.py"], "test question")
        
        # Should return fallback data structure
        assert "symbols" in result
        assert "imports" in result
        assert "references" in result


class TestQueryServicePublicAPI:
    """Test public API methods."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_method(self, sample_semantic_results):
        """Test the search method."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service._get_logger = MagicMock(return_value=MagicMock())
        service._semantic_search = AsyncMock(return_value=sample_semantic_results)
        
        service.search = QueryService.search.__get__(service, QueryService)
        
        result = await service.search("test query", 0.7, 5)
        
        assert "=== Code Search Results for: test query ===" in result
        assert "test/file1.py" in result
        assert "score: 0.95" in result
        service._semantic_search.assert_called_once_with("test query", 0.7, 5)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """Test search method with no results."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service._get_logger = MagicMock(return_value=MagicMock())
        service._semantic_search = AsyncMock(return_value=[])
        
        service.search = QueryService.search.__get__(service, QueryService)
        
        result = await service.search("no results query", 0.7, 5)
        
        assert result == "No results found matching your query."

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_error_handling(self):
        """Test search method error handling."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service._get_logger = MagicMock(return_value=MagicMock())
        service._semantic_search = AsyncMock(side_effect=Exception("Search failed"))
        
        service.search = QueryService.search.__get__(service, QueryService)
        
        result = await service.search("error query", 0.7, 5)
        
        assert "Error performing search: Search failed" in result


class TestQueryServiceIntegration:
    """Integration tests for QueryService (with mocked dependencies)."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch('services.query.src.query.main.time.time')
    async def test_query_method_parallel_processing(self, mock_time, sample_semantic_results, sample_structural_data):
        """Test main query method with parallel processing."""
        from query.main import QueryService
        
        # Mock time for consistent timing
        mock_time.side_effect = [0.0, 0.1, 0.2]  # start, middle, end
        
        service = MagicMock(spec=QueryService)
        service.cache_enabled = True
        service.parallel_processing = True
        service._get_logger = MagicMock(return_value=MagicMock())
        service._semantic_search = AsyncMock(return_value=sample_semantic_results)
        service._get_structural_data = AsyncMock(return_value=sample_structural_data)
        service._format_result = QueryService._format_result.__get__(service, QueryService)
        
        service.query = QueryService.query.__get__(service, QueryService)
        
        result = await service.query("test query", 0.5, 100, True)
        
        assert "=== Code Query Results ===" in result
        service._semantic_search.assert_called_once_with("test query", 0.5, 100)
        service._get_structural_data.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_query_method_sequential_processing(self, sample_semantic_results, sample_structural_data):
        """Test main query method with sequential processing."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service.cache_enabled = False
        service.parallel_processing = False
        service._get_logger = MagicMock(return_value=MagicMock())
        service._semantic_search = AsyncMock(return_value=sample_semantic_results)
        service._get_structural_data = AsyncMock(return_value=sample_structural_data)
        service._format_result = QueryService._format_result.__get__(service, QueryService)
        
        service.query = QueryService.query.__get__(service, QueryService)
        
        result = await service.query("test query", 0.5, 100, False)
        
        assert "=== Code Query Results ===" in result
        service._semantic_search.assert_called_once_with("test query", 0.5, 100)
        service._get_structural_data.assert_called_once()

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_debug_query_json_format(self, sample_semantic_results, sample_structural_data):
        """Test debug query with JSON format."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service.parallel_processing = True
        service._get_logger = MagicMock(return_value=MagicMock())
        service._semantic_search = AsyncMock(return_value=sample_semantic_results)
        service._get_structural_data = AsyncMock(return_value=sample_structural_data)
        
        service.debug_query = QueryService.debug_query.__get__(service, QueryService)
        
        result = await service.debug_query(
            "test query", 0.3, 100, True, "json"
        )
        
        # Should return valid JSON
        parsed = json.loads(result)
        assert "query" in parsed
        assert "parameters" in parsed
        assert "timings" in parsed
        assert "results" in parsed
        assert parsed["query"] == "test query"

    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_debug_query_text_format(self, sample_semantic_results, sample_structural_data):
        """Test debug query with text format."""
        from query.main import QueryService
        
        service = MagicMock(spec=QueryService)
        service.parallel_processing = False
        service._get_logger = MagicMock(return_value=MagicMock())
        service._semantic_search = AsyncMock(return_value=sample_semantic_results)
        service._get_structural_data = AsyncMock(return_value=sample_structural_data)
        service._format_debug_output = QueryService._format_debug_output.__get__(service, QueryService)
        
        service.debug_query = QueryService.debug_query.__get__(service, QueryService)
        
        result = await service.debug_query(
            "test query", 0.3, 100, True, "text"
        )
        
        assert "=== QUERY DEBUG INFO ===" in result
        assert "test query" in result
        assert "=== TIMINGS ===" in result
        assert "=== SEMANTIC RESULTS ===" in result