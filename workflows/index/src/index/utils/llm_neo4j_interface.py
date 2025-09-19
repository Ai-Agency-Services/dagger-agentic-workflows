import logging
from typing import Any, Dict, List, Optional

from ..services.neo4j_service import Neo4jService


class CodeGraphInterface:
    """Interface for LLMs to query the code graph database"""

    def __init__(self, neo4j: Neo4jService):
        self.neo4j = neo4j
        self.logger = logging.getLogger(__name__)

    async def get_file_structure(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the structure of files in the codebase"""
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (s)-[:DEFINED_IN]->(f)
        WITH f, count(s) as symbol_count
        RETURN f.filepath as filepath, f.language as language, symbol_count
        ORDER BY symbol_count DESC
        LIMIT $limit
        """
        return await self.neo4j.execute_query(query, {"limit": limit})

    async def get_function_details(self, function_name: str) -> List[Dict[str, Any]]:
        """Get details about a specific function"""
        query = """
        MATCH (f:Function {name: $name})
        RETURN f.name as name, f.filepath as filepath, 
               f.start_line as start_line, f.end_line as end_line,
               f.signature as signature
        """
        return await self.neo4j.execute_query(query, {"name": function_name})

    async def get_function_callers(self, function_name: str) -> List[Dict[str, Any]]:
        """Find all callers of a specific function"""
        query = """
        MATCH (caller)-[:CALLS]->(f:Function {name: $name})
        RETURN caller.name as caller_name, caller.type as caller_type,
               caller.filepath as caller_filepath, caller.start_line as caller_line
        """
        return await self.neo4j.execute_query(query, {"name": function_name})

    async def get_class_hierarchy(self, class_name: str) -> List[Dict[str, Any]]:
        """Get class inheritance hierarchy"""
        query = """
        MATCH p = (c:Class {name: $name})-[:INHERITS_FROM*]->(parent:Class)
        RETURN [node in nodes(p) | node.name] as inheritance_path
        """
        return await self.neo4j.execute_query(query, {"name": class_name})

    async def get_module_dependencies(self, filepath: str) -> List[Dict[str, Any]]:
        """Get files imported by a specific file"""
        query = """
        MATCH (f:File {filepath: $filepath})-[:IMPORTS]->(imported:File)
        RETURN imported.filepath as imported_file, 
               imported.language as language
        ORDER BY imported_file
        """
        return await self.neo4j.execute_query(query, {"filepath": filepath})

    async def get_dependent_files(self, filepath: str) -> List[Dict[str, Any]]:
        """Get files that import this file"""
        query = """
        MATCH (f:File)-[:IMPORTS]->(target:File {filepath: $filepath})
        RETURN f.filepath as importing_file, 
               f.language as language
        ORDER BY importing_file
        """
        return await self.neo4j.execute_query(query, {"filepath": filepath})

    async def get_import_graph(self, depth: int = 2) -> List[Dict[str, Any]]:
        """Get the import graph of the codebase up to a certain depth"""
        query = """
        MATCH path = (f:File)-[:IMPORTS*1..{depth}]->(imported:File)
        RETURN [node in nodes(path) | node.filepath] as import_chain,
               length(path) as depth
        LIMIT 100
        """
        return await self.neo4j.execute_query(query, {"depth": depth})

    async def find_circular_imports(self) -> List[Dict[str, Any]]:
        """Find circular dependencies in the codebase"""
        query = """
        MATCH path = (f:File)-[:IMPORTS*2..10]->(f)
        WITH nodes(path) as files
        RETURN [file in files | file.filepath] as circular_dependency
        LIMIT 20
        """
        return await self.neo4j.execute_query(query, {})

    async def get_most_imported_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find the most imported files in the codebase"""
        query = """
        MATCH (f:File)<-[r:IMPORTS]-(importer:File)
        WITH f, count(r) as import_count
        RETURN f.filepath as filepath, 
               f.language as language,
               import_count
        ORDER BY import_count DESC
        LIMIT $limit
        """
        return await self.neo4j.execute_query(query, {"limit": limit})

    async def get_files_with_most_imports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find files that import the most other files"""
        query = """
        MATCH (f:File)-[r:IMPORTS]->(imported:File)
        WITH f, count(r) as import_count
        RETURN f.filepath as filepath, 
               f.language as language,
               import_count
        ORDER BY import_count DESC
        LIMIT $limit
        """
        return await self.neo4j.execute_query(query, {"limit": limit})

    async def analyze_module_coupling(self) -> List[Dict[str, Any]]:
        """Analyze module coupling by finding directories with most inter-dependencies"""
        query = """
        // Extract directories from file paths
        MATCH (f1:File)-[:IMPORTS]->(f2:File)
        WITH 
          CASE 
            WHEN f1.filepath CONTAINS '/' 
            THEN substring(f1.filepath, 0, split(f1.filepath, '/')[0])
            ELSE f1.filepath 
          END AS dir1,
          CASE 
            WHEN f2.filepath CONTAINS '/' 
            THEN substring(f2.filepath, 0, split(f2.filepath, '/')[0])
            ELSE f2.filepath 
          END AS dir2
        WHERE dir1 <> dir2
        WITH dir1, dir2, count(*) as coupling
        RETURN dir1 as source_directory,
               dir2 as target_directory,
               coupling as dependency_count
        ORDER BY coupling DESC
        LIMIT 20
        """
        return await self.neo4j.execute_query(query, {})

    async def generate_import_visualization(self) -> Dict[str, Any]:
        """Generate data for import graph visualization"""
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (f)-[:IMPORTS]->(imported:File)
        WITH f, collect(imported) as imports
        RETURN {
            nodes: collect({
                id: f.filepath,
                label: last(split(f.filepath, "/")),
                language: f.language,
                imports_count: size(imports)
            }),
            edges: [
                (f)-[:IMPORTS]->(imported) |
                {
                    source: f.filepath,
                    target: imported.filepath
                }
            ]
        } as graph
        """
        result = await self.neo4j.execute_query(query, {})
        return result[0] if result else {"nodes": [], "edges": []}
