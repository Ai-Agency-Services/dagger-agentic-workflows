import logging
from typing import Any, Dict, List, Optional

import dagger
from index.services.neo4j_service import Neo4jService
from index.utils.embeddings import generate_embeddings
from supabase import Client


class CodebaseQueryEngine:
    """Unified interface that combines semantic search with structural graph analysis"""

    def __init__(
        self,
        graph_interface: Neo4jService,
        supabase_client: Client,
        openai_api_key: dagger.Secret,
        logger: Optional[logging.Logger] = None
    ):
        self.graph = graph_interface
        self.supabase = supabase_client
        self.openai_api_key = openai_api_key
        self.logger = logger or logging.getLogger(__name__)

    async def query(self, question: str, similarity_threshold: float = 0.7, max_results: int = 10) -> Dict[str, Any]:
        """
        Two-stage query process:
        1. First find semantically relevant code using vector DB
        2. Then enrich with structural information from the graph DB
        """
        # Stage 1: Semantic search to find relevant files
        vector_results = await self._semantic_search(question, similarity_threshold, max_results)

        # Extract relevant file paths for structural queries
        file_paths = list(set(item["filepath"] for item in vector_results))
        self.logger.info(
            f"Found {len(file_paths)} semantically relevant files")

        # Stage 2: Perform structural queries on these files
        structural_data = await self._get_structural_data(file_paths, question)

        # Combine the results
        return {
            "semantic_results": vector_results,
            "structural_data": structural_data,
            "relevant_files": file_paths
        }

    async def _semantic_search(self, query: str, threshold: float, limit: int) -> List[Dict[str, Any]]:
        """Search the vector database for semantically similar code using text query"""
        try:
            # 1. Generate embedding for the query text using your existing function
            query_embedding = await generate_embeddings(
                text=query,
                openai_api_key=self.openai_api_key,
                model="text-embedding-3-small"  # Use the same model as your stored embeddings
            )

            # 2. Use the embedding to query the database with your existing function
            response = self.supabase.rpc(
                'match_code_embeddings',  # Your existing vector search function
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_limit': limit
                }
            ).execute()

            if hasattr(response, 'data'):
                return response.data
            return []

        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []

    async def _get_structural_data(self, file_paths: List[str], question: str) -> Dict[str, Any]:
        """Get structural information from the graph database for the provided file paths"""
        results = {}

        # Get imports and exports for these files
        imports = []
        for file_path in file_paths:
            file_imports = await self.graph.execute_query("""
                MATCH (f:File {filepath: $filepath})-[:IMPORTS]->(imported:File)
                RETURN imported.filepath as imported_file
            """, {"filepath": file_path})
            imports.extend(file_imports)

        # Get symbols defined in these files
        symbols = []
        for file_path in file_paths:
            file_symbols = await self.graph.execute_query("""
                MATCH (s)-[:DEFINED_IN]->(f:File {filepath: $filepath})
                RETURN s.name as name, s.type as type, s.signature as signature, 
                       s.start_line as line, f.filepath as filepath
            """, {"filepath": file_path})
            symbols.extend(file_symbols)

        # Get files that import these files (dependents)
        dependents = []
        for file_path in file_paths:
            file_dependents = await self.graph.execute_query("""
                MATCH (f:File)-[:IMPORTS]->(target:File {filepath: $filepath})
                RETURN f.filepath as dependent_file, f.language as language
            """, {"filepath": file_path})
            dependents.extend(file_dependents)

        results["imports"] = imports
        results["symbols"] = symbols
        results["dependents"] = dependents

        return results

    # Additional methods for the CodebaseQueryEngine class

    async def find_code_by_functionality(self, description: str, limit: int = 5) -> List[Dict]:
        """Find code related to a specific functionality description"""
        # Start with semantic search
        semantic_results = await self._semantic_search(description, 0.7, limit)

        # Get detailed information for each result
        enriched_results = []
        for result in semantic_results:
            # Get function/class details
            symbols = await self.graph.execute_query("""
                MATCH (s)-[:DEFINED_IN]->(f:File {filepath: $filepath})
                WHERE s.start_line <= $start_line AND s.end_line >= $end_line
                RETURN s.name as name, s.type as type, s.signature as signature
            """, {
                "filepath": result["filepath"],
                "start_line": result["start_line"],
                "end_line": result["end_line"]
            })

            # Add symbol info to the result
            result["defined_symbols"] = symbols
            enriched_results.append(result)

        return enriched_results

    async def find_implementation_details(self, functionality: str, limit: int = 10) -> Dict:
        """Find implementation details for a specific functionality"""
        # First find semantically relevant code
        semantic_results = await self._semantic_search(functionality, 0.75, limit)

        # Extract the most relevant file paths
        file_paths = list(set(item["filepath"]
                          for item in semantic_results[:5]))

        # Get function calls and class hierarchy
        implementation = {}

        # Get functions for these files
        functions = []
        for file_path in file_paths:
            file_functions = await self.graph.execute_query("""
                MATCH (f:Function)-[:DEFINED_IN]->(file:File {filepath: $filepath})
                RETURN f.name as name, f.signature as signature, 
                       f.start_line as start_line, f.end_line as end_line
            """, {"filepath": file_path})
            functions.extend(file_functions)

        # Get function call graph
        calls = []
        for file_path in file_paths:
            function_calls = await self.graph.execute_query("""
                MATCH (caller)-[:CALLS]->(callee)
                WHERE (caller)-[:DEFINED_IN]->(:File {filepath: $filepath})
                OR (callee)-[:DEFINED_IN]->(:File {filepath: $filepath})
                RETURN caller.name as caller, callee.name as callee,
                       caller.filepath as caller_file, callee.filepath as callee_file
            """, {"filepath": file_path})
            calls.extend(function_calls)

        implementation["functions"] = functions
        implementation["calls"] = calls
        implementation["semantic_matches"] = semantic_results

        return implementation
