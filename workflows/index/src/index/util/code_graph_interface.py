import logging
from typing import Any, Dict, List

from index.utils.neo4j_connector import Neo4jConnector


class CodeGraphInterface:
    """Interface for LLMs to query the code graph database"""

    def __init__(self, neo4j: Neo4jConnector):
        self.neo4j = neo4j
        self.logger = logging.getLogger(__name__)

    def get_file_structure(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the structure of files in the codebase"""
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (s)-[:DEFINED_IN]->(f)
        WITH f, count(s) as symbol_count
        RETURN f.path as filepath, f.language as language, symbol_count
        ORDER BY symbol_count DESC
        LIMIT $limit
        """
        return self.neo4j.execute_query(query, {"limit": limit})

    def get_function_details(self, function_name: str) -> List[Dict[str, Any]]:
        """Get details about a specific function"""
        query = """
        MATCH (f:Function {name: $name})
        RETURN f.name as name, f.filepath as filepath, 
               f.start_line as start_line, f.end_line as end_line,
               f.signature as signature
        """
        return self.neo4j.execute_query(query, {"name": function_name})

    def get_function_callers(self, function_name: str) -> List[Dict[str, Any]]:
        """Find all callers of a specific function"""
        query = """
        MATCH (caller)-[:CALLS]->(f:Function {name: $name})
        RETURN caller.name as caller_name, caller.type as caller_type,
               caller.filepath as caller_filepath, caller.start_line as caller_line
        """
        return self.neo4j.execute_query(query, {"name": function_name})

    def get_class_hierarchy(self, class_name: str) -> List[Dict[str, Any]]:
        """Get class inheritance hierarchy"""
        query = """
        MATCH p = (c:Class {name: $name})-[:INHERITS_FROM*]->(parent:Class)
        RETURN [node in nodes(p) | node.name] as inheritance_path
        """
        return self.neo4j.execute_query(query, {"name": class_name})

    def get_dependencies(self, filepath: str) -> List[Dict[str, Any]]:
        """Get dependencies of a specific file/module"""
        query = """
        MATCH (f:File {path: $filepath})-[:IMPORTS]->(m)
        RETURN m.name as module_name
        """
        return self.neo4j.execute_query(query, {"filepath": filepath})

    def find_related_code(self, query_text: str) -> List[Dict[str, Any]]:
        """Find code elements related to a text query (using basic text matching)"""
        query = """
        MATCH (n)
        WHERE n.name CONTAINS $query OR n.signature CONTAINS $query
        RETURN n.name as name, n.type as type, n.filepath as filepath,
               n.start_line as line
        LIMIT 10
        """
        return self.neo4j.execute_query(query, {"query": query_text})
