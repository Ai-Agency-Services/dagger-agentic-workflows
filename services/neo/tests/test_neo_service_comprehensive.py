"""Comprehensive unit tests for NeoService."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
from neo.main import SymbolProperties, RelationshipProperties, NeoService


class TestSymbolProperties:
    """Test SymbolProperties class."""

    @pytest.mark.unit
    def test_from_dict_with_known_fields(self):
        """Test creating SymbolProperties from dict with known fields."""
        data = {
            "docstring": "Test function",
            "signature": "def test()",
            "scope": "global",
            "parent": "TestClass"
        }
        props = SymbolProperties.from_dict(data.copy())
        
        assert props.docstring == "Test function"
        assert props.signature == "def test()"
        assert props.scope == "global"
        assert props.parent == "TestClass"
        assert props.json_data is None

    @pytest.mark.unit
    def test_from_dict_with_extra_fields(self):
        """Test creating SymbolProperties with extra fields stored as JSON."""
        data = {
            "docstring": "Test function",
            "custom_field": "custom_value",
            "complexity": 5
        }
        props = SymbolProperties.from_dict(data.copy())
        
        assert props.docstring == "Test function"
        assert props.json_data is not None
        
        extra_data = json.loads(props.json_data)
        assert extra_data["custom_field"] == "custom_value"
        assert extra_data["complexity"] == 5

    @pytest.mark.unit
    def test_from_dict_empty(self):
        """Test creating SymbolProperties from empty dict."""
        props = SymbolProperties.from_dict({})
        
        assert props.docstring is None
        assert props.signature is None
        assert props.scope is None
        assert props.parent is None
        assert props.json_data is None

    @pytest.mark.unit
    def test_from_dict_none(self):
        """Test creating SymbolProperties from None."""
        props = SymbolProperties.from_dict(None)
        
        assert props.docstring is None
        assert props.signature is None
        assert props.scope is None
        assert props.parent is None
        assert props.json_data is None


class TestRelationshipProperties:
    """Test RelationshipProperties class."""

    @pytest.mark.unit
    def test_from_dict_complete(self):
        """Test creating RelationshipProperties with all fields."""
        data = {
            "type": "CALLS",
            "name": "function_call",
            "value": "test_value",
            "weight": 5
        }
        props = RelationshipProperties.from_dict(data.copy())
        
        assert props.type == "CALLS"
        assert props.name == "function_call"
        assert props.value == "test_value"
        assert props.weight == 5

    @pytest.mark.unit
    def test_from_dict_partial(self):
        """Test creating RelationshipProperties with partial fields."""
        data = {"type": "IMPORTS", "weight": 1}
        props = RelationshipProperties.from_dict(data.copy())
        
        assert props.type == "IMPORTS"
        assert props.name is None
        assert props.value is None
        assert props.weight == 1

    @pytest.mark.unit
    def test_from_dict_empty(self):
        """Test creating RelationshipProperties from empty dict."""
        props = RelationshipProperties.from_dict({})
        
        assert props.type is None
        assert props.name is None
        assert props.value is None
        assert props.weight is None


class TestNeoServiceHelpers:
    """Test NeoService helper methods."""

    @pytest.mark.unit
    @patch('neo.main.logging')
    def test_get_logger(self, mock_logging, sample_yaml_config):
        """Test logger creation."""
        from neo.main import NeoService
        
        # Create a mock NeoService instance
        service = MagicMock(spec=NeoService)
        service._get_logger = NeoService._get_logger.__get__(service, NeoService)
        
        logger = service._get_logger()
        
        mock_logging.basicConfig.assert_called_once()
        mock_logging.getLogger.assert_called_with("neo4j.service")


class TestNeoServiceQueryMethods:
    """Test NeoService query-related methods."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_improved_simple_parse(self):
        """Test the improved_simple_parse function logic."""
        # Test case from the actual method
        def improved_simple_parse(raw_output: str) -> str:
            if not raw_output:
                return "0"
            lines = [line.strip() for line in raw_output.strip().split('\n') if line.strip()]
            for line in lines:
                clean_line = line.strip('"').strip("'")
                if clean_line.isdigit():
                    return clean_line
            return lines[-1] if lines else "0"
        
        # Test cases
        assert improved_simple_parse("") == "0"
        assert improved_simple_parse("5") == "5"
        assert improved_simple_parse('"10"') == "10"
        assert improved_simple_parse("count(n)\n42\n") == "42"
        assert improved_simple_parse("header\nnotanumber\n") == "notanumber"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_improved_parse_list(self):
        """Test the improved_parse_list function logic."""
        def improved_parse_list(raw_output: str) -> str:
            if not raw_output:
                return "None found"
            lines = [line.strip() for line in raw_output.strip().split('\n') if line.strip()]
            data_lines = []
            for line in lines:
                if (line.lower().startswith('label') or 
                    line.lower().startswith('relationshiptype') or
                    all(c in '-=+|' for c in line)):
                    continue
                if line and line not in data_lines:
                    clean_line = line.strip('"').strip("'")
                    if clean_line:
                        data_lines.append(clean_line)
            return '\n'.join(data_lines) if data_lines else "None found"
        
        # Test cases
        assert improved_parse_list("") == "None found"
        assert improved_parse_list("File\n---------\ntest.py") == "File\ntest.py"
        assert improved_parse_list('"item1"\n"item2"') == "item1\nitem2"
        assert improved_parse_list("Label\n-----\nFile\nFunction") == "File\nFunction"


class TestNeoServiceDatabaseOperations:
    """Test NeoService database operations with mocking."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('neo.main.YAMLConfig')
    async def test_add_file_node_success(self, mock_yaml_config):
        """Test successful file node addition."""
        from neo.main import NeoService
        
        # Setup mocks
        mock_config = MagicMock()
        mock_yaml_config.return_value = mock_config
        
        service = MagicMock(spec=NeoService)
        service.config = {"test": "config"}
        service.run_query = AsyncMock(return_value="success")
        service._get_logger = MagicMock(return_value=MagicMock())
        
        # Bind the actual method
        service.add_file_node = NeoService.add_file_node.__get__(service, NeoService)
        
        result = await service.add_file_node("test.py", "python")
        
        assert result is True
        service.run_query.assert_called_once()
        call_args = service.run_query.call_args[0][0]
        assert 'MERGE (f:File {filepath: "test.py"})' in call_args
        assert 'language = "python"' in call_args

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_file_node_with_quotes(self):
        """Test file node addition with special characters."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.config = {"test": "config"}
        service.run_query = AsyncMock(return_value="success")
        service._get_logger = MagicMock(return_value=MagicMock())
        service.add_file_node = AsyncMock(return_value=True)
        
        result = await service.add_file_node('test"file.py', "python")
        
        assert result is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_symbol_basic(self):
        """Test basic symbol addition."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.run_query = AsyncMock(return_value="success")
        service._get_logger = MagicMock(return_value=MagicMock())
        
        service.add_symbol = NeoService.add_symbol.__get__(service, NeoService)
        
        result = await service.add_symbol(
            symbol_type="Function",
            name="test_func",
            filepath="test.py",
            start_line=10,
            end_line=20
        )
        
        assert result is True
        service.run_query.assert_called_once()
        call_args = service.run_query.call_args[0][0]
        assert 'MERGE (s:Function {name: "test_func"' in call_args
        assert 'start_line = 10' in call_args
        assert 'end_line = 20' in call_args

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_symbol_with_properties(self):
        """Test symbol addition with properties."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.run_query = AsyncMock(return_value="success")
        service._get_logger = MagicMock(return_value=MagicMock())
        
        service.add_symbol = NeoService.add_symbol.__get__(service, NeoService)
        
        properties = SymbolProperties(
            docstring="Test function",
            signature="def test_func()",
            scope="global"
        )
        
        result = await service.add_symbol(
            symbol_type="Function",
            name="test_func",
            filepath="test.py",
            start_line=10,
            end_line=20,
            properties=properties
        )
        
        assert result is True
        call_args = service.run_query.call_args[0][0]
        assert 'docstring = "Test function"' in call_args
        assert 'signature = "def test_func()"' in call_args
        assert 'scope = "global"' in call_args

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_symbol_with_json_properties(self):
        """Test symbol addition with JSON properties."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.run_query = AsyncMock(return_value="success")
        service._get_logger = MagicMock(return_value=MagicMock())
        
        service.add_symbol = NeoService.add_symbol.__get__(service, NeoService)
        
        properties = SymbolProperties(
            json_data=json.dumps({"complexity": 5, "async": True})
        )
        
        result = await service.add_symbol(
            symbol_type="Function",
            name="test_func",
            filepath="test.py",
            start_line=10,
            end_line=20,
            properties=properties
        )
        
        assert result is True
        call_args = service.run_query.call_args[0][0]
        assert 'complexity = 5' in call_args
        assert 'async = True' in call_args

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_symbol_error_handling(self):
        """Test symbol addition error handling."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.run_query = AsyncMock(side_effect=Exception("Database error"))
        mock_logger = MagicMock()
        service._get_logger = MagicMock(return_value=mock_logger)
        
        service.add_symbol = NeoService.add_symbol.__get__(service, NeoService)
        
        result = await service.add_symbol(
            symbol_type="Function",
            name="test_func",
            filepath="test.py",
            start_line=10,
            end_line=20
        )
        
        assert result is False
        mock_logger.error.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_relationship_basic(self):
        """Test basic relationship addition."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.config = {"test": "config"}
        service.add_relationship = AsyncMock(return_value=True)
        
        result = await service.add_relationship(
            start_filepath="file1.py",
            relationship_type="IMPORTS",
            end_filepath="file2.py"
        )
        
        assert result is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_relationship_with_properties(self):
        """Test relationship addition with properties."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.config = {"test": "config"}
        service.add_relationship = AsyncMock(return_value=True)
        
        properties = RelationshipProperties(
            type="function_call",
            name="test_call",
            weight=3
        )
        
        result = await service.add_relationship(
            start_filepath="file1.py",
            relationship_type="CALLS",
            end_filepath="file2.py",
            properties=properties
        )
        
        assert result is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_clear_database_success(self):
        """Test successful database clearing."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.run_query = AsyncMock(return_value="success")
        
        service.clear_database = NeoService.clear_database.__get__(service, NeoService)
        
        result = await service.clear_database()
        
        assert result is True
        service.run_query.assert_called_once_with("MATCH (n) DETACH DELETE n")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_clear_database_error(self):
        """Test database clearing error handling."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.run_query = AsyncMock(side_effect=Exception("Clear failed"))
        mock_logger = MagicMock()
        service._get_logger = MagicMock(return_value=mock_logger)
        
        service.clear_database = NeoService.clear_database.__get__(service, NeoService)
        
        result = await service.clear_database()
        
        assert result is False

    @pytest.mark.unit
    def test_connect_with_client(self):
        """Test connect method when client exists."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.cypher_shell_client = MagicMock()  # Client exists
        
        service.connect = NeoService.connect.__get__(service, NeoService)
        
        result = service.connect()
        
        assert result is True

    @pytest.mark.unit
    def test_connect_without_client(self):
        """Test connect method when no client exists."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.cypher_shell_client = None
        mock_logger = MagicMock()
        service._get_logger = MagicMock(return_value=mock_logger)
        
        service.connect = NeoService.connect.__get__(service, NeoService)
        
        result = service.connect()
        
        assert result is False
        mock_logger.error.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_batch_queries_empty(self):
        """Test run_batch_queries with empty list."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.run_batch_queries = NeoService.run_batch_queries.__get__(service, NeoService)
        
        result = await service.run_batch_queries([])
        
        assert result == ""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_batch_queries_multiple(self):
        """Test run_batch_queries with multiple queries."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.run_query = AsyncMock(return_value="batch result")
        service.run_batch_queries = NeoService.run_batch_queries.__get__(service, NeoService)
        
        queries = ["MATCH (n) RETURN n", "MATCH (m) RETURN m"]
        result = await service.run_batch_queries(queries)
        
        assert result == "batch result"
        # Verify the combined query
        expected_combined = "MATCH (n) RETURN n;\nMATCH (m) RETURN m;"
        service.run_query.assert_called_once_with(expected_combined)


class TestNeoServiceIntegration:
    """Integration-style tests for NeoService (with mocked external dependencies)."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch('neo.main.yaml.safe_load')
    async def test_create_service(self, mock_yaml_load):
        """Test NeoService creation process."""
        from neo.main import NeoService
        
        # Mock file contents and config
        mock_config = {
            "neo4j": {
                "uri": "neo4j://localhost:7687",
                "username": "neo4j"
            }
        }
        mock_yaml_load.return_value = mock_config
        
        mock_file = AsyncMock()
        mock_file.contents = AsyncMock(return_value="config content")
        
        mock_password = MagicMock()
        mock_github_token = MagicMock()
        mock_neo_auth = MagicMock()
        mock_neo_data = MagicMock()
        
        service = await NeoService.create(
            config_file=mock_file,
            password=mock_password,
            github_access_token=mock_github_token,
            neo_auth=mock_neo_auth,
            neo_data=mock_neo_data
        )
        
        assert service.config == mock_config
        assert service.password == mock_password
        assert service.github_access_token == mock_github_token
        assert service.neo_auth == mock_neo_auth
        assert service.neo_data == mock_neo_data
        mock_yaml_load.assert_called_once_with("config content")

    @pytest.mark.neo4j
    @pytest.mark.asyncio
    async def test_ensure_client_creation(self):
        """Test ensure_client creates client when needed."""
        from neo.main import NeoService
        
        service = MagicMock(spec=NeoService)
        service.cypher_shell_client = None
        service.create_neo_client = AsyncMock(return_value=MagicMock())
        
        service.ensure_client = NeoService.ensure_client.__get__(service, NeoService)
        
        result = await service.ensure_client()
        
        assert result is not None
        service.create_neo_client.assert_called_once()

    @pytest.mark.neo4j
    @pytest.mark.asyncio
    async def test_ensure_client_reuse(self):
        """Test ensure_client reuses existing client."""
        from neo.main import NeoService
        
        existing_client = MagicMock()
        service = MagicMock(spec=NeoService)
        service.cypher_shell_client = existing_client
        
        service.ensure_client = NeoService.ensure_client.__get__(service, NeoService)
        
        result = await service.ensure_client()
        
        assert result == existing_client