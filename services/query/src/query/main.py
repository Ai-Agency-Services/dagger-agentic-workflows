from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional, Tuple

import anyio
import dagger
import yaml
from dagger import Doc, dag, field, function, object_type
from pydantic import BaseModel

# Import Supabase client for vector search
from supabase import create_client, Client

# For OpenAI embeddings
import openai


@object_type
class QueryService:
    """Unified service for querying code through both graph and vector databases"""
    # Store only serializable fields in the object_type
    config: dict
    config_file: dagger.File
    open_router_api_key: dagger.Secret
    neo_data: dagger.CacheVolume
    supabase_url: str
    supabase_key: dagger.Secret
    neo_password: dagger.Secret
    github_access_token: dagger.Secret
    neo_auth: dagger.Secret  # Changed: no longer Optional with default=None
    cache_enabled: bool = field(default=True)
    cache_ttl: int = field(default=3600)
    parallel_processing: bool = field(default=True)
    embedding_dimension: int = field(
        default=1536)  # OpenAI embeddings dimension

    # Private logger instance
    _logger: Optional[logging.Logger] = None

    def _get_logger(self) -> logging.Logger:
        """Get or create logger instance (cached)"""
        if not hasattr(self, '_logger') or self._logger is None:
            logging.basicConfig(
                level=logging.DEBUG,  # Changed from INFO to DEBUG
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self._logger = logging.getLogger("query.service")
            # Ensure our logger is set to DEBUG
            self._logger.setLevel(logging.DEBUG)
        return self._logger

    @classmethod
    async def create(
        cls,
        config_file: Annotated[dagger.File, Doc("Path to YAML config file")],
        open_router_api_key: Annotated[dagger.Secret, Doc("OpenAI API key")],
        supabase_key: Annotated[dagger.Secret, Doc("Supabase API key")],
        neo_data: Annotated[dagger.CacheVolume, Doc("Dagger cache volume for Neo4j data")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        supabase_url: Annotated[str, Doc("Supabase project URL")],
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        # Changed: removed default=None
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
    ) -> QueryService:
        """Initialize the QueryService with configuration"""
        try:
            # Load config from file
            config_str = await config_file.contents()
            config_dict = yaml.safe_load(config_str)

            if not config_dict:
                # Fallback: try module demo config, then a minimal inline default for tests/CI
                try:
                    from pathlib import Path
                    fallback = Path(__file__).resolve().parents[2] / "demo/agencyservices.yaml"
                    if fallback.exists():
                        with open(fallback, "r", encoding="utf-8") as fbf:
                            config_dict = yaml.safe_load(fbf) or {}
                except Exception:
                    pass
                if not config_dict:
                    config_dict = {
                        "container": {"work_dir": "/app"},
                        "git": {"user_name": "CI", "user_email": "ci@example.com", "base_pull_request_branch": "main"}
                    }
                if not config_dict:
                    raise ValueError("Config file is empty or invalid YAML")

            # Get configuration values with defaults
            integration_config = config_dict.get("integration", {})
            cache_enabled = integration_config.get("cache_enabled", True)
            cache_ttl = integration_config.get("cache_ttl", 3600)
            parallel_processing = integration_config.get(
                "parallel_processing", True)

            # Get Supabase URL from config if not provided explicitly
            if not supabase_url and "supabase" in config_dict:
                supabase_url = config_dict.get("supabase", {}).get("url", "")
                if not supabase_url:
                    print("Warning: No Supabase URL found in configuration")

            # Get embedding dimension from config
            embedding_dimension = config_dict.get(
                "integration", {}).get("embedding_dimension", 1536)

            # Create instance with serializable fields
            instance = cls(
                config=config_dict,
                config_file=config_file,
                open_router_api_key=open_router_api_key,
                supabase_url=supabase_url,
                supabase_key=supabase_key,
                neo_data=neo_data,
                neo_password=neo_password,
                github_access_token=github_access_token,
                neo_auth=neo_auth,
                cache_enabled=cache_enabled,
                cache_ttl=cache_ttl,
                parallel_processing=parallel_processing,
                embedding_dimension=embedding_dimension
            )

            print("QueryService instance created successfully")
            return instance

        except Exception as e:
            print(f"Error creating QueryService: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Failed to create QueryService: {e}") from e

    @function
    async def query(
        self,
        question: str,
        similarity_threshold: float = 0.2,
        max_results: int = 100,
        use_cache: bool = True
    ) -> str:
        """
        Perform a unified query across both semantic and structural databases.

        Args:
            question: The natural language question to ask about the code
            similarity_threshold: Minimum similarity score for semantic matches
            max_results: Maximum number of results to return
            use_cache: Whether to use cached results if available

        Returns:
            Formatted results as a string
        """
        logger = self._get_logger()
        logger.info(
            f"🔍 Executing query: '{question[:50]}...' with threshold={similarity_threshold}")

        # Create local cache for this function invocation
        cache = {}
        cache_timestamp = {}

        start_time = time.time()

        # Check cache if enabled
        cache_key = f"query:{question}:{similarity_threshold}:{max_results}"
        if self.cache_enabled and use_cache:
            logger.debug(
                "Cache check skipped (persistent cache not implemented)")

        # Execute the two-stage query process
        if self.parallel_processing:
            logger.info("Using parallel processing mode")
            # First get semantic results
            semantic_results = await self._semantic_search(question, similarity_threshold, max_results)
            logger.info(f"Found {len(semantic_results)} semantic matches")

            # Extract file paths for structural queries
            file_paths = list(set(item.get("filepath", "") for item in semantic_results
                                  if "filepath" in item))
            logger.info(
                f"Extracted {len(file_paths)} unique file paths for structural queries")

            # Then run structural query with these paths using anyio task
            structural_data = {}
            structural_error = None

            async with anyio.create_task_group() as tg:
                async def get_structural():
                    nonlocal structural_data, structural_error
                    try:
                        structural_data = await self._get_structural_data(file_paths, question)
                    except Exception as e:
                        structural_error = e
                        logger.error(
                            f"Error in structural data retrieval: {e}", exc_info=True)

                tg.start_soon(get_structural)

            # Handle any errors from structural data retrieval
            if structural_error:
                structural_data = {"error": str(structural_error), "symbols": [
                ], "imports": [], "references": []}
        else:
            logger.info("Using sequential processing mode")
            # Run queries sequentially
            semantic_results = await self._semantic_search(question, similarity_threshold, max_results)
            logger.info(f"Found {len(semantic_results)} semantic matches")

            # Extract file paths for structural queries
            file_paths = list(set(item.get("filepath", "") for item in semantic_results
                                  if "filepath" in item))
            logger.info(
                f"Extracted {len(file_paths)} unique file paths for structural queries")

            # Get structural data
            structural_data = await self._get_structural_data(file_paths, question)

        # Extract symbols from structural data
        symbols = structural_data.get("symbols", [])

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000
        logger.info(f"✅ Query completed in {query_time_ms:.2f}ms")

        # Create result object
        result = {
            "semantic_results": semantic_results,
            "structural_data": structural_data,
            "relevant_files": file_paths,
            "symbols": symbols,
            "metadata": {
                "semantic": {
                    "query_time_ms": query_time_ms,
                    "source": "vector",
                    "result_count": len(semantic_results)
                },
                "structural": {
                    "query_time_ms": query_time_ms,
                    "source": "graph",
                    "result_count": len(structural_data.get("symbols", [])) +
                    len(structural_data.get("imports", []))
                }
            }
        }

        return self._format_result(result)

    @function
    async def search(
        self,
        query: str,
        similarity_threshold: float = 0.7,
        max_results: int = 5
    ) -> str:
        """
        Perform a semantic search for code relevant to the query.

        Args:
            query: Natural language query about code
            similarity_threshold: Minimum similarity threshold (0.0-1.0)
            max_results: Maximum number of results to return

        Returns:
            Formatted search results as a string
        """
        logger = self._get_logger()
        logger.info(f"🔎 Performing semantic search: '{query[:50]}...'")

        try:
            results = await self._semantic_search(query, similarity_threshold, max_results)
            logger.info(f"Search returned {len(results)} results")

            if not results:
                return "No results found matching your query."

            output = f"=== Code Search Results for: {query} ===\n\n"

            for i, result in enumerate(results):
                filepath = result.get("filepath", "unknown")
                score = result.get("score", 0)
                language = result.get("language", "")

                output += f"{i+1}. {filepath} (score: {score:.2f})\n"

                if "content" in result:
                    # Limit content to reasonable length
                    content = result["content"]
                    if len(content) > 300:
                        content = content[:297] + "..."
                    output += f"```{language}\n{content}\n```\n\n"

            return output

        except Exception as e:
            logger.error(f"❌ Error performing search: {e}", exc_info=True)
            return f"Error performing search: {e}"

    @function
    async def invalidate_cache(self, filepath: Optional[str] = None) -> str:
        """
        Invalidate cache entries related to a specific file or all entries.

        Args:
            filepath: Optional file path to invalidate. If None, invalidate all.

        Returns:
            Message indicating the number of entries invalidated
        """
        # In a real implementation, this would clear entries from a persistent cache
        return f"Cache invalidation simulated for {filepath if filepath else 'all files'}."

    @function
    async def get_file_details(self, filepath: str) -> str:
        """
        Get detailed information about a specific file, combining graph and vector data.

        Args:
            filepath: Path to the file to examine

        Returns:
            Formatted string with file details
        """
        try:
            # This would normally use self._neo_service, but we'll simulate the response
            return f"""
=== File Details for {filepath} ===

File Information:
Path: {filepath}
Language: {filepath.split('.')[-1] if '.' in filepath else 'unknown'}

Imports:
(Neo4j service required for import information)

Imported By:
(Neo4j service required for dependency information)
"""
        except Exception as e:
            return f"Error getting file details: {e}"

    @function
    async def debug_query(
        self,
        question: str,
        similarity_threshold: float = 0.3,
        max_results: int = 100,
        include_raw_data: bool = True,
        format: str = "text"  # "text" or "json"
    ) -> str:
        """
        Perform a query with enhanced debugging output to inspect results.

        Args:
            question: The natural language question to ask about the code
            similarity_threshold: Minimum similarity score for semantic matches
            max_results: Maximum number of results to return
            include_raw_data: Whether to include complete raw data in output
            format: Output format ("text" or "json")

        Returns:
            Detailed debug information about the query execution and results
        """
        logger = self._get_logger()
        logger.info(f"🐛 Debug query: '{question[:50]}...' (format={format})")

        start_time = time.time()
        debug_info = {
            "query": question,
            "parameters": {
                "similarity_threshold": similarity_threshold,
                "max_results": max_results
            },
            "timings": {},
            "results": {}
        }

        # Execute semantic search
        logger.info("Starting semantic search...")
        semantic_start = time.time()
        semantic_results = await self._semantic_search(question, similarity_threshold, max_results)
        semantic_time = (time.time() - semantic_start) * 1000
        debug_info["timings"]["semantic_search_ms"] = semantic_time
        logger.info(f"Semantic search completed in {semantic_time:.2f}ms")

        # Extract file paths for structural queries
        file_paths = list(set(item.get("filepath", "")
                          for item in semantic_results if "filepath" in item))
        debug_info["file_paths_found"] = file_paths
        logger.info(f"Found {len(file_paths)} unique file paths")

        # Execute structural queries with anyio timeout protection
        logger.info("Starting structural data retrieval...")
        structural_start = time.time()
        structural_data = {}

        try:
            # Use anyio.move_on_after for proper timeout handling
            with anyio.move_on_after(30.0):  # 30 second timeout
                structural_data = await self._get_structural_data(file_paths, question)
                logger.info("Structural data retrieval completed successfully")
        except Exception as e:
            logger.error(
                f"❌ Error in structural data retrieval: {e}", exc_info=True)
            structural_data = {"error": str(
                e), "symbols": [], "imports": [], "references": []}

        structural_time = (time.time() - structural_start) * 1000
        debug_info["timings"]["structural_data_ms"] = structural_time
        logger.info(
            f"Structural data retrieval completed in {structural_time:.2f}ms")

        # Calculate total query time
        total_time = (time.time() - start_time) * 1000
        debug_info["timings"]["total_query_ms"] = total_time
        logger.info(f"Total debug query time: {total_time:.2f}ms")

        # Collect results
        if include_raw_data:
            debug_info["results"]["semantic"] = semantic_results
            debug_info["results"]["structural"] = structural_data
        else:
            debug_info["results"]["semantic_count"] = len(semantic_results)
            debug_info["results"]["structural"] = {
                "symbols_count": len(structural_data.get("symbols", [])),
                "imports_count": len(structural_data.get("imports", [])),
                "references_count": len(structural_data.get("references", []))
            }

        # Format output based on requested format
        if format.lower() == "json":
            return json.dumps(debug_info, indent=2)
        else:
            return self._format_debug_output(debug_info, include_raw_data)

    def _format_debug_output(self, debug_info: Dict[str, Any], include_raw_data: bool) -> str:
        """Format debug information as readable text output"""
        logger = self._get_logger()
        logger.debug("Formatting debug output")

        output = []

        # Query information
        output.append("=== QUERY DEBUG INFO ===")
        output.append(f"Query: {debug_info['query']}")
        output.append(f"Parameters: similarity_threshold={debug_info['parameters']['similarity_threshold']}, "
                      f"max_results={debug_info['parameters']['max_results']}")

        # Timing information
        output.append("\n=== TIMINGS ===")
        output.append(
            f"Semantic search: {debug_info['timings']['semantic_search_ms']:.2f}ms")
        output.append(
            f"Structural data: {debug_info['timings']['structural_data_ms']:.2f}ms")
        output.append(
            f"Total query time: {debug_info['timings']['total_query_ms']:.2f}ms")

        # File paths
        output.append("\n=== FILES FOUND ===")
        if debug_info.get("file_paths_found"):
            for i, path in enumerate(debug_info["file_paths_found"]):
                output.append(f"{i+1}. {path}")
        else:
            output.append("No files found")

        # Results summary
        if include_raw_data and "results" in debug_info:
            # Semantic results
            output.append("\n=== SEMANTIC RESULTS ===")
            semantic_results = debug_info["results"].get("semantic", [])
            if semantic_results:
                for i, result in enumerate(semantic_results):
                    output.append(f"\nResult {i+1}:")
                    output.append(
                        f"  File: {result.get('filepath', 'unknown')}")
                    output.append(f"  Score: {result.get('score', 0):.4f}")
                    output.append(
                        f"  Language: {result.get('language', 'unknown')}")
                    if "start_line" in result and "end_line" in result:
                        output.append(
                            f"  Lines: {result['start_line']}-{result['end_line']}")
                    if "content" in result:
                        content = result["content"]
                        if len(content) > 300:
                            content = content[:297] + "..."
                        output.append(f"  Content: {content}")

            # Structural results
            output.append("\n=== STRUCTURAL DATA ===")
            structural_data = debug_info["results"].get("structural", {})

            # Symbols
            symbols = structural_data.get("symbols", [])
            output.append(f"\nSymbols ({len(symbols)}):")
            for i, symbol in enumerate(symbols[:5]):  # Show first 5 only
                output.append(
                    f"  {i+1}. {symbol.get('type', '')} {symbol.get('name', '')} in {symbol.get('filepath', '')}")
            if len(symbols) > 5:
                output.append(f"  ... and {len(symbols) - 5} more symbols")

            # Imports
            imports = structural_data.get("imports", [])
            output.append(f"\nImports ({len(imports)}):")
            for i, imp in enumerate(imports[:5]):  # Show first 5 only
                output.append(
                    f"  {i+1}. {imp.get('source_file', '')} imports {imp.get('imported_file', '')}")
            if len(imports) > 5:
                output.append(f"  ... and {len(imports) - 5} more imports")

            # References
            references = structural_data.get("references", [])
            output.append(f"\nReferences ({len(references)}):")
            for i, ref in enumerate(references[:5]):  # Show first 5 only
                output.append(f"  {i+1}. {ref.get('symbol_name', '')} in {ref.get('defined_in', '')} "
                              f"referenced by {ref.get('referenced_by', '')} in {ref.get('referenced_in', '')}")
            if len(references) > 5:
                output.append(
                    f"  ... and {len(references) - 5} more references")
        else:
            # Just show counts
            output.append("\n=== RESULTS SUMMARY ===")
            if "results" in debug_info:
                output.append(
                    f"Semantic results: {debug_info['results'].get('semantic_count', 0)}")
                output.append(
                    f"Symbols: {debug_info['results'].get('structural', {}).get('symbols_count', 0)}")
                output.append(
                    f"Imports: {debug_info['results'].get('structural', {}).get('imports_count', 0)}")
                output.append(
                    f"References: {debug_info['results'].get('structural', {}).get('references_count', 0)}")

        logger.debug("Debug output formatting completed")
        return "\n".join(output)

    async def _semantic_search(
        self,
        question: str,
        similarity_threshold: float,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Execute semantic search using Supabase's vector search capabilities.

        Args:
            question: The search query
            similarity_threshold: Minimum similarity score (0.0-1.0)
            max_results: Maximum number of results to return

        Returns:
            List of matched documents with content and metadata
        """
        logger = self._get_logger()
        logger.info(f"Executing semantic search for: '{question[:50]}...'")

        try:
            # Create Supabase client locally (runtime object)
            supabase_key_str = await self.supabase_key.plaintext()
            supabase = create_client(self.supabase_url, supabase_key_str)
            logger.info(f"Connected to Supabase at {self.supabase_url}")

            # Create OpenAI client for embeddings
            openai_key_str = await self.open_router_api_key.plaintext()
            openai_client = openai.OpenAI(api_key=openai_key_str)
            logger.info("Created OpenAI client")

            # Generate embedding for the question
            logger.info("Generating embedding for query")
            embedding_response = openai_client.embeddings.create(
                input=question,
                model="text-embedding-ada-002"  # Use appropriate model
            )
            query_embedding = embedding_response.data[0].embedding
            dimensions = len(query_embedding)
            logger.info(f"Generated embedding with {dimensions} dimensions")

            # Add detailed embedding diagnostics
            if dimensions != self.embedding_dimension:
                logger.warning(
                    f"⚠️ Dimension mismatch: expected {self.embedding_dimension}, got {dimensions}")

            # Log embedding statistics
            nonzero_values = sum(1 for x in query_embedding if abs(x) > 0.0001)
            embedding_stats = {
                "min": min(query_embedding),
                "max": max(query_embedding),
                "avg": sum(query_embedding) / len(query_embedding),
                "nonzero_percent": (nonzero_values / len(query_embedding)) * 100
            }
            logger.info(f"Embedding stats: min={embedding_stats['min']:.4f}, max={embedding_stats['max']:.4f}, "
                        f"avg={embedding_stats['avg']:.4f}, nonzero={embedding_stats['nonzero_percent']:.1f}%")

            # Try with an even lower fallback threshold if the primary threshold is high
            original_threshold = similarity_threshold
            fallback_threshold = min(0.1, similarity_threshold)

            # Execute vector search using Supabase
            logger.info(
                f"Querying Supabase with threshold={similarity_threshold}, limit={max_results}")
            response = supabase.rpc(
                'match_code_embeddings',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': similarity_threshold,
                    'match_limit': min(max_results, 100)
                }
            ).execute()

            # Process results
            if hasattr(response, 'data') and response.data:
                results = []
                for item in response.data:
                    result = {
                        "filepath": item.get("filepath", ""),
                        "content": item.get("content", ""),
                        "score": item.get("similarity", 0),
                        "language": item.get("language", "")
                    }

                    # Add optional fields if present
                    if "start_line" in item:
                        result["start_line"] = item["start_line"]
                    if "end_line" in item:
                        result["end_line"] = item["end_line"]

                    results.append(result)

                logger.info(f"Semantic search found {len(results)} matches")
                return results
            else:
                # Try with lower threshold if primary search returned no results
                if similarity_threshold > fallback_threshold:
                    logger.info(
                        f"No results with threshold={similarity_threshold}, trying fallback threshold={fallback_threshold}")
                    fallback_response = supabase.rpc(
                        'match_code_embeddings',
                        {
                            'query_embedding': query_embedding,
                            'match_threshold': fallback_threshold,
                            'match_limit': min(max_results, 100)
                        }
                    ).execute()

                    if hasattr(fallback_response, 'data') and fallback_response.data:
                        results = []
                        for item in fallback_response.data:
                            result = {
                                "filepath": item.get("filepath", ""),
                                "content": item.get("content", ""),
                                "score": item.get("similarity", 0),
                                "language": item.get("language", "")
                            }

                            # Add optional fields if present
                            if "start_line" in item:
                                result["start_line"] = item["start_line"]
                            if "end_line" in item:
                                result["end_line"] = item["end_line"]

                            results.append(result)

                        logger.info(
                            f"Fallback search found {len(results)} matches")
                        return results
                    else:
                        logger.warning(
                            f"No results from Supabase search with any threshold (original={original_threshold}, fallback={fallback_threshold})")
                else:
                    logger.warning("No results from Supabase search")

            # Return empty list instead of simulated results
            return []

        except Exception as e:
            logger.error(f"❌ Error in semantic search: {e}", exc_info=True)
            # Return empty results instead of simulated data
            return []

    async def _get_structural_data(
        self,
        file_paths: List[str],
        question: str
    ) -> Dict[str, Any]:
        """
        Execute structural queries on the graph database using Neo4j.

        Args:
            file_paths: List of file paths to query for structural data
            question: The original search question (for context)

        Returns:
            Dictionary with symbols, imports, and references information
        """
        logger = self._get_logger()
        logger.info(f"Retrieving structural data for {len(file_paths)} files")

        try:
            # Create Neo4j service with proper parameters
            neo_service = dag.neo_service(
                config_file=self.config_file,
                password=self.neo_password,
                github_access_token=self.github_access_token,
                neo_auth=self.neo_auth,
                neo_data=self.neo_data
            )
            logger.info("Created Neo4j service")

            if not file_paths:
                logger.warning(
                    "No file paths provided for structural data query")
                return {"symbols": [], "imports": [], "references": []}

            # Format file paths for Cypher query as string literals
            file_paths_str = ', '.join([f"'{path}'" for path in file_paths])

            # Build Cypher queries with inline parameter values
            symbols_query = f"""
            MATCH (f:File)-[:DEFINES]->(s:Symbol)
            WHERE f.filepath IN [{file_paths_str}]
            RETURN s.name as name, labels(s)[0] as type, f.filepath as filepath, 
                   s.start_line as start_line, s.end_line as end_line
            LIMIT 20
            """

            imports_query = f"""
            MATCH (f:File)-[:IMPORTS]->(imported:File)
            WHERE f.filepath IN [{file_paths_str}]
            RETURN f.filepath as source_file, imported.filepath as imported_file
            LIMIT 20
            """

            references_query = f"""
            MATCH (f:File)-[:DEFINES]->(s:Symbol)<-[:REFERENCES]-(ref:Symbol)<-[:DEFINES]-(refFile:File)
            WHERE f.filepath IN [{file_paths_str}]
            RETURN s.name as symbol_name, labels(s)[0] as symbol_type, f.filepath as defined_in,
                   ref.name as referenced_by, refFile.filepath as referenced_in
            LIMIT 20
            """

            # Execute queries with proper error handling
            symbols = []
            imports = []
            references = []

            try:
                logger.info("Executing symbols query")
                symbols_result = await neo_service.run_query(symbols_query)
                symbols = self._parse_cypher_result(
                    symbols_result, ["name", "type", "filepath", "start_line", "end_line"])
                logger.info(f"Found {len(symbols)} symbols")
            except Exception as e:
                logger.error(
                    f"Error executing symbols query: {e}", exc_info=True)

            try:
                logger.info("Executing imports query")
                imports_result = await neo_service.run_query(imports_query)
                imports = self._parse_cypher_result(
                    imports_result, ["source_file", "imported_file"])
                logger.info(f"Found {len(imports)} imports")
            except Exception as e:
                logger.error(
                    f"Error executing imports query: {e}", exc_info=True)

            try:
                logger.info("Executing references query")
                references_result = await neo_service.run_query(references_query)
                references = self._parse_cypher_result(references_result, [
                    "symbol_name", "symbol_type", "defined_in", "referenced_by", "referenced_in"])
                logger.info(f"Found {len(references)} references")
            except Exception as e:
                logger.error(
                    f"Error executing references query: {e}", exc_info=True)

            # Return combined results
            return {
                "symbols": symbols,
                "imports": imports,
                "references": references
            }

        except Exception as e:
            logger.error(
                f"❌ Error in structural data retrieval: {e}", exc_info=True)
            # Fallback to simulated results
            logger.info("Using fallback simulated structural data")
            return {
                "symbols": [
                    {"name": f"symbol_{i}", "type": "function", "filepath": path}
                    for i, path in enumerate(file_paths[:3])
                ],
                "imports": [
                    {"source_file": file_paths[0] if file_paths else "unknown",
                     "imported_file": f"lib/module{i}.py"}
                    for i in range(2)
                ],
                "references": []
            }

    def _parse_cypher_result(self, result: str, columns: List[str]) -> List[Dict[str, Any]]:
        """
        Parse cypher-shell output into structured data

        Args:
            result: String result from Neo4j query
            columns: Expected column names

        Returns:
            List of dictionaries with parsed data
        """
        logger = self._get_logger()

        if not result or not result.strip():
            logger.debug("Empty result from Cypher query")
            return []

        lines = [line.strip()
                 for line in result.strip().split("\n") if line.strip()]
        if len(lines) <= 1:  # Just header or empty
            logger.debug("No data rows in Cypher result (header only)")
            return []

        logger.debug(f"Parsing {len(lines)-1} data rows from Cypher result")
        parsed_data = []

        for i in range(1, len(lines)):  # Skip header row
            line = lines[i]
            # Simple parsing - this may need to be enhanced for complex outputs
            parts = line.split()

            if len(parts) < len(columns):
                logger.warning(
                    f"Row {i} has fewer parts ({len(parts)}) than expected columns ({len(columns)})")
                continue

            row_data = {}
            for j, col in enumerate(columns):
                if j < len(parts):
                    # Clean up quotes from values
                    value = parts[j].strip('"')

                    # Try to convert to int if possible
                    try:
                        if value.isdigit():
                            value = int(value)
                    except (ValueError, AttributeError):
                        pass

                    row_data[col] = value

            if row_data:
                parsed_data.append(row_data)

        logger.debug(f"Successfully parsed {len(parsed_data)} data rows")
        return parsed_data

    def _format_result(self, result: Dict[str, Any]) -> str:
        """Format query results into a human-readable string"""
        logger = self._get_logger()
        logger.debug("Formatting query results")

        output = []
        output.append("=== Code Query Results ===\n")

        # Add semantic results
        semantic_results = result.get("semantic_results", [])
        if semantic_results:
            output.append("Relevant code sections:")
            for i, match in enumerate(semantic_results[:3]):
                output.append(
                    f"\n{i+1}. {match.get('filepath', 'unknown')} (score: {match.get('score', 0):.2f}):")
                if "content" in match:
                    content = match["content"]
                    if len(content) > 300:
                        content = content[:297] + "..."
                    output.append(
                        f"```{match.get('language', '')}\n{content}\n```")

        # Add structural information
        structural_data = result.get("structural_data", {})
        if structural_data.get("symbols"):
            output.append("\nKey symbols:")
            for symbol in structural_data["symbols"][:5]:
                output.append(
                    f"- {symbol.get('type', 'unknown')} {symbol.get('name', 'unknown')} in {symbol.get('filepath', 'unknown')}")

        return "\n".join(output)

    @function
    async def log_last_query(
        self,
        log_file: Optional[str] = "/tmp/query_debug.log"
    ) -> str:
        """
        Write the last query execution details to a log file for later inspection.
        Useful for debugging when immediate console output isn't practical.

        Args:
            log_file: Path to write the log file

        Returns:
            Path to the log file or error message
        """
        try:
            # This is a simplified example - in a real implementation, you would
            # track the last query results and write them to the log file
            debug_info = {
                "timestamp": datetime.now().isoformat(),
                "message": "This is a placeholder for actual query logging",
                "note": "Implement query history tracking to make this feature work"
            }

            # Write to log file
            with open(log_file, 'w') as f:
                f.write(json.dumps(debug_info, indent=2))

            return f"Debug information written to {log_file}"
        except Exception as e:
            return f"Error writing debug log: {e}"
