import json
import logging
import os
from typing import Annotated, Dict, List, Optional, Set, Tuple

import anyio
import dagger
import yaml
from ais_dagger_agents_config.models import YAMLConfig
from dagger import Doc, dag, function, object_type
from dagger.client.gen import NeoService


@object_type
class Graph:
    config: dict
    config_file: dagger.File
    neo_service: Optional[NeoService] = None
    neo_data: Optional[dagger.CacheVolume] = None

    @classmethod
    async def create(cls,
                     config_file: Annotated[dagger.File, Doc("Path to the YAML config file")],
                     neo_data: Annotated[dagger.CacheVolume, Doc("Neo4j data cache volume")]) -> "Graph":
        """Create a Graph object from a YAML config file."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, config_file=config_file, neo_data=neo_data)

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("graph.main")

    def _get_processing_config(self) -> dict:
        """Extract processing configuration from YAML config."""
        config_obj = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config

        # Check for concurrency config first, fall back to indexing config
        concurrency_config = getattr(config_obj, 'concurrency', None)
        indexing_config = getattr(config_obj, 'indexing', None)

        return {
            'max_concurrent': (
                getattr(concurrency_config, 'max_concurrent',
                        None) if concurrency_config else None
            ) or (
                getattr(indexing_config, 'batch_size',
                        None) if indexing_config else None
            ) or 3,  # REDUCED from 5 to 3 for better performance
            'batch_size': 1,  # Always use individual queries for best performance
            'throttle_ms': getattr(indexing_config, 'throttle_ms', None)
        }

    def _escape_cypher_string(self, value: str) -> str:
        """Escape special characters in Cypher string values."""
        if not value:
            return ""
        # Escape quotes and backslashes
        return value.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

    def _build_file_cypher(self, filepath: str, language: str) -> str:
        """Build Cypher query for creating a file node """
        escaped_filepath = self._escape_cypher_string(filepath)
        escaped_language = self._escape_cypher_string(language)
        # Single MERGE with ON CREATE/MATCH for optimal performance
        return f'MERGE (f:File {{filepath: "{escaped_filepath}"}}) ON CREATE SET f.language = "{escaped_language}", f.path = "{escaped_filepath}" ON MATCH SET f.language = "{escaped_language}";'

    def _build_symbol_cypher(self, symbol_dict: dict, filepath: str) -> str:
        """Build Cypher query for creating a symbol node."""
        symbol_name = self._escape_cypher_string(symbol_dict.get("name", ""))
        symbol_type = symbol_dict.get("type", "symbol").capitalize()
        start_line = symbol_dict.get("line_number", 0) or 0
        end_line = symbol_dict.get("end_line_number", -1) or -1
        escaped_filepath = self._escape_cypher_string(filepath)

        # Handle optional properties
        properties = []
        for attr in ['scope', 'docstring', 'parent', 'signature', 'visibility']:
            if attr in symbol_dict and symbol_dict[attr]:
                escaped_value = self._escape_cypher_string(str(symbol_dict[attr]))
                properties.append(f'{attr}: "{escaped_value}"')

        props_string = ', ' + ', '.join(properties) if properties else ''

        # Use appropriate line property based on symbol type
        if symbol_type == "Variable":
            return f'MERGE (s:{symbol_type} {{name: "{symbol_name}", filepath: "{escaped_filepath}", line_number: {start_line}}}) SET s.end_line = {end_line}{props_string};'
        else:
            return f'MERGE (s:{symbol_type} {{name: "{symbol_name}", filepath: "{escaped_filepath}", start_line: {start_line}}}) SET s.end_line = {end_line}{props_string};'

    def _build_import_cypher(self, from_file: str, to_file: str) -> str:
        """Build Cypher query for creating import relationships - OPTIMIZED VERSION."""
        escaped_from = self._escape_cypher_string(from_file)
        escaped_to = self._escape_cypher_string(to_file)
        # Single efficient query
        return f'MERGE (from:File {{filepath: "{escaped_from}"}}) MERGE (to:File {{filepath: "{escaped_to}"}}) MERGE (from)-[:IMPORTS]->(to);'

    def _build_relationship_cypher(self, filepath: str, symbol_type: str) -> str:
        """Build DEFINED_IN relationship query."""
        escaped_filepath = self._escape_cypher_string(filepath)
        return f'MATCH (s:{symbol_type} {{filepath: "{escaped_filepath}"}}) MATCH (f:File {{filepath: "{escaped_filepath}"}}) MERGE (s)-[:DEFINED_IN]->(f);'

    def _build_symbol_relationship_cypher(self, from_symbol: str, to_symbol: str,
                                          relationship_type: str, filepath: str) -> str:
        """Build Cypher query for creating symbol-to-symbol relationships within a file."""
        escaped_from = self._escape_cypher_string(from_symbol)
        escaped_to = self._escape_cypher_string(to_symbol)
        escaped_filepath = self._escape_cypher_string(filepath)

        return f'''MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "{escaped_from}" AND s1.filepath = "{escaped_filepath}"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "{escaped_to}" AND s2.filepath = "{escaped_filepath}"
MERGE (s1)-[:{relationship_type}]->(s2);'''

    def _build_cross_file_symbol_relationship_cypher(self, from_symbol: str, from_filepath: str,
                                                     to_symbol: str, to_filepath: str,
                                                     relationship_type: str) -> str:
        """Build Cypher for creating symbol-to-symbol relationships across files."""
        ef = self._escape_cypher_string
        return f'''MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface)
AND s1.name = "{ef(from_symbol)}" AND s1.filepath = "{ef(from_filepath)}"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface)
AND s2.name = "{ef(to_symbol)}" AND s2.filepath = "{ef(to_filepath)}"
MERGE (s1)-[:{relationship_type}]->(s2);'''

    def _resolve_relative_import(self, current_file: str, import_path: str) -> Optional[str]:
        """Resolve relative import paths to absolute paths."""
        try:
            import os

            # Get the directory of the current file
            current_dir = os.path.dirname(current_file)

            # Handle different relative import patterns
            if import_path.startswith('./'):
                # Same directory import
                relative_path = import_path[2:]  # Remove './'
            elif import_path.startswith('../'):
                # Parent directory import
                relative_path = import_path
            else:
                return None

            # Join with current directory and normalize
            resolved_path = os.path.normpath(
                os.path.join(current_dir, relative_path))

            # Add common file extensions if none provided
            if not os.path.splitext(resolved_path)[1]:
                # Try common extensions
                for ext in ['.js', '.ts', '.jsx', '.tsx', '.py']:
                    potential_path = resolved_path + ext
                    # For now, just return the path with extension
                    # In a real implementation, you'd check if the file exists
                    return potential_path
                # Try index files
                for ext in ['.js', '.ts', '.jsx', '.tsx']:
                    index_path = os.path.join(resolved_path, f'index{ext}')
                    return index_path

            return resolved_path

        except Exception:
            return None

    def _extract_symbol_references(self, content: str, symbols: List[dict], filepath: str) -> List[str]:
        """Extract CALLS and REFERENCES relationships between symbols."""
        relationships = []

        # Create a map of symbols by name for quick lookup
        symbol_map = {s.get("name", ""): s for s in symbols if s.get("name")}

        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Find symbols that appear in this line
            symbols_in_line = []
            for symbol_name, symbol_info in symbol_map.items():
                if symbol_name in line and symbol_info.get("line_number") != i:
                    symbols_in_line.append((symbol_name, symbol_info))

            # For each symbol found in this line, check what it might be referencing
            for current_symbol_name, current_symbol in symbols_in_line:
                current_line = current_symbol.get("line_number", 0)

                # Skip if this is the symbol's definition line
                if current_line == i:
                    continue

                # Determine relationship type based on context
                if '(' in line and current_symbol_name + '(' in line:
                    # Function call
                    # Find the symbol that contains this line
                    containing_symbol = self._find_containing_symbol(
                        i, symbol_map)
                    if containing_symbol:
                        rel_query = self._build_symbol_relationship_cypher(
                            containing_symbol, current_symbol_name, "CALLS", filepath
                        )
                        relationships.append(rel_query)
                else:
                    # Variable/property reference
                    containing_symbol = self._find_containing_symbol(
                        i, symbol_map)
                    if containing_symbol and containing_symbol != current_symbol_name:
                        rel_query = self._build_symbol_relationship_cypher(
                            containing_symbol, current_symbol_name, "REFERENCES", filepath
                        )
                        relationships.append(rel_query)

        return relationships

    def _find_containing_symbol(self, line_number: int, symbol_map: dict) -> Optional[str]:
        """Find which symbol (function/class/method) contains the given line number."""
        containing_symbols = []

        for symbol_name, symbol_info in symbol_map.items():
            start_line = symbol_info.get(
                "line_number") or symbol_info.get("start_line", 0)
            end_line = symbol_info.get(
                "end_line_number") or symbol_info.get("end_line", 0)

            # Check if line falls within symbol boundaries
            if start_line <= line_number <= end_line:
                # Prefer functions and methods over classes (more specific scope)
                symbol_type = symbol_info.get("type", "").lower()
                if symbol_type in ["function", "method"]:
                    containing_symbols.append(
                        (symbol_name, symbol_info, 1))  # High priority
                elif symbol_type == "class":
                    containing_symbols.append(
                        (symbol_name, symbol_info, 0))  # Lower priority

        # Return the highest priority containing symbol
        if containing_symbols:
            containing_symbols.sort(key=lambda x: x[2], reverse=True)
            return containing_symbols[0][0]

        return None

    async def _execute_queries_concurrently(
        self,
        queries: List[str],
        query_type: str,
        logger: logging.Logger,
        max_concurrent: int = 15
    ) -> Tuple[int, int]:
        """Execute queries concurrently with controlled concurrency."""
        if not queries:
            return 0, 0

        semaphore = anyio.Semaphore(max_concurrent)
        successful = 0
        failed = 0

        async def execute_with_limit(query: str, index: int):
            nonlocal successful, failed
            async with semaphore:
                try:
                    await self.neo_service.run_query(query)
                    successful += 1
                    # Log progress every 50 queries
                    if index % 50 == 0:
                        logger.info(
                            f"Executed {index + 1}/{len(queries)} {query_type} queries")
                    return True
                except Exception as e:
                    failed += 1
                    logger.error(
                        f"Failed to execute {query_type} query {index + 1}: {e}")
                    return False

        # Use anyio task group for concurrent execution
        async with anyio.create_task_group() as tg:
            for i, query in enumerate(queries):
                tg.start_soon(execute_with_limit, query, i)

        logger.info(
            f"Completed {query_type} queries: {successful} successful, {failed} failed")
        return successful, failed

    def _join_batches(self, batches: List[str]) -> str:
        parts: List[str] = []
        for i, b in enumerate(batches or [], 1):
            parts.append(f"// BATCH {i:05d}\n{b}\n")
        return "\n".join(parts)

    async def _execute_queries_in_concurrent_batches(
        self,
        queries: List[str],
        query_type: str,
        logger: logging.Logger,
        batch_size: int = 5,
        max_concurrent_batches: int = 5,
        export_accumulator: Optional[Dict[str, List[str]]] = None,
        exports: Optional[List[Tuple[str, str]]] = None,
        export_prefix: Optional[str] = None,
        execute: bool = True,
        throttle_ms: Optional[int] = None,
    ) -> Tuple[int, int]:
        batches = [queries[i:i + batch_size] for i in range(0, len(queries), batch_size)]
        semaphore = anyio.Semaphore(max_concurrent_batches)
        total_successful = 0
        total_failed = 0

        async def execute_batch_with_limit(batch: List[str], batch_index: int):
            nonlocal total_successful, total_failed
            async with semaphore:
                batch_query = "\n".join(batch)

                if export_accumulator is not None:
                    export_accumulator.setdefault(query_type, []).append(batch_query)
                elif exports is not None:
                    prefix = export_prefix or "batches"
                    rel_path = f"{prefix}/{query_type}/batch_{batch_index + 1:05d}.cypher"
                    exports.append((rel_path, batch_query))

                async def _maybe_throttle():
                    if throttle_ms and throttle_ms > 0:
                        try:
                            await anyio.sleep(throttle_ms / 1000.0)
                        except Exception:
                            pass

                if not execute:
                    logger.info(f"DRY-RUN captured {query_type} batch {batch_index + 1}/{len(batches)} ({len(batch)} queries)")
                    total_successful += len(batch)
                    await _maybe_throttle()
                    return len(batch), 0

                try:
                    await self.neo_service.run_query(batch_query)
                    total_successful += len(batch)
                    logger.info(f"Executed {query_type} batch {batch_index + 1}/{len(batches)} ({len(batch)} queries)")
                    await _maybe_throttle()
                    return len(batch), 0
                except Exception as e:
                    logger.error(f"Failed {query_type} batch {batch_index + 1}: {e}. Retrying individually…")
                    succ = 0
                    fail = 0
                    for qi, q in enumerate(batch):
                        try:
                            await self.neo_service.run_query(q)
                            succ += 1
                        except Exception as qe:
                            fail += 1
                            preview = (q[:240] + '…') if len(q) > 240 else q
                            logger.error(f"{query_type} query failed in batch {batch_index + 1}, item {qi + 1}: {qe}. Query preview: {preview}")
                    total_successful += succ
                    total_failed += fail
                    await _maybe_throttle()
                    return succ, fail

        async with anyio.create_task_group() as tg:
            for i, batch in enumerate(batches):
                tg.start_soon(execute_batch_with_limit, batch, i)

        logger.info(f"Completed {query_type} batches: {total_successful} successful, {total_failed} failed")
        return total_successful, total_failed

    def _build_chunked_export_files(
        self,
        export_prefix: str,
        export_acc: Dict[str, List[str]],
        summary: dict,
    ) -> List[Tuple[str, str]]:
        files: List[Tuple[str, str]] = []
        max_chunks = 20
        for qtype, blist in (export_acc or {}).items():
            if not blist:
                continue
            n = len(blist)
            chunks = min(max_chunks, max(1, n))
            size = max(1, (n + chunks - 1) // chunks)
            for ci in range(chunks):
                start = ci * size
                end = min(n, start + size)
                if start >= end:
                    break
                files.append((f"{export_prefix}/{qtype}_{ci + 1:04d}.cypher", self._join_batches(blist[start:end])))
        files.append((f"{export_prefix}/summary.json", json.dumps(summary, indent=2)))
        return files

    async def _safe_build_graph_data_for_file(
        self,
        filepath: str,
        container: dagger.Container,
        logger: logging.Logger
    ) -> Dict[str, any]:
        """Safely process a single file and return graph data instead of executing queries."""
        try:
            # Get file content
            content = await container.file(filepath).contents()
            if not content.strip():
                logger.debug(f"Skipping empty file: {filepath}")
                return {"success": True, "queries": [], "imports": [], "symbols": [], "symbol_relationships": []}

            logger.debug(f"Processing file: {filepath} ({len(content)} chars)")

            # Parse and build graph data for file
            result = await self._build_graph_data_for_file(filepath, content, container, logger)

            if result["success"]:
                logger.debug(f"Successfully processed {filepath}")
            else:
                logger.warning(f"Failed to process {filepath}")

            return result

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            return {"success": False, "queries": [], "imports": [], "symbols": [], "symbol_relationships": []}

    async def _build_graph_data_for_file(
        self,
        filepath: str,
        content: str,
        container: dagger.Container,
        logger: logging.Logger
    ) -> Dict[str, any]:
        """Process a file and return Cypher queries instead of executing them."""
        try:
            # Additional file types to explicitly exclude
            excluded_extensions = ['xml', 'json', 'md',
                                   'txt', 'csv', 'yml', 'yaml', 'html']

            # Extract extension and check if it's explicitly excluded
            _, ext = os.path.splitext(filepath)
            ext = ext.lstrip('.').lower()

            if ext in excluded_extensions:
                logger.debug(
                    f"Skipping excluded file type: {filepath} (extension: {ext})")
                return {"success": True, "queries": [], "imports": [], "symbols": [], "symbol_relationships": []}

            # Check against allowed extensions if configured
            config_obj = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config
            if hasattr(config_obj, 'indexing') and hasattr(config_obj.indexing, 'file_extensions'):
                valid_extensions = config_obj.indexing.file_extensions
                if ext not in valid_extensions:
                    logger.debug(
                        f"Skipping non-code file: {filepath} (extension: {ext})")
                    return {"success": True, "queries": [], "imports": [], "symbols": [], "symbol_relationships": []}

            # Resolve ignore directories from config (optional)
            ignore_dirs = []
            try:
                if hasattr(config_obj, 'indexing') and hasattr(config_obj.indexing, 'ignore_directories'):
                    ignore_dirs = list(config_obj.indexing.ignore_directories or [])
            except Exception:
                ignore_dirs = []

            queries = []
            imports = []
            symbols = []
            symbol_relationships = []
            symbol_names = []

            # Parse code file using the agent_utils parser
            try:
                agent_utils = dag.agent_utils()
                code_file_json = await agent_utils.parse_code_file_to_json(content, filepath, ignore_dirs=ignore_dirs)
                json_content = await code_file_json.contents()
                code_file_dict = json.loads(json_content)

                if not code_file_dict:
                    logger.warning(f"Could not parse {filepath}")
                    return {"success": False, "queries": [], "imports": [], "symbols": [], "symbol_relationships": []}

                language = code_file_dict["language"]
                parsed_symbols = code_file_dict["symbols"]
                # Extract imports from parsed data
                parsed_imports = code_file_dict.get("imports", [])

                # Fallback: add re-export sources as imports (handles `export {X} from '...';`)
                try:
                    import re as _re
                    for m in _re.finditer(r'export\\s*\\{[^}]*\\}\\s*from\\s*[\'"]([^\'"]+)[\'"]\\s*;?', content):
                        parsed_imports.append(m.group(1))
                except Exception as _re_err:
                    logger.debug(
                        f"Re-export scan failed for {filepath}: {_re_err}")

                # Build file creation query
                queries.append(self._build_file_cypher(filepath, language))

                # Build symbol creation queries and collect symbol info
                if parsed_symbols:
                    for symbol_dict in parsed_symbols:
                        symbol_name = symbol_dict.get("name", "")
                        if symbol_name:
                            symbol_type = symbol_dict.get(
                                "type", "symbol").capitalize()
                            queries.append(self._build_symbol_cypher(
                                symbol_dict, filepath))
                            symbols.append((filepath, symbol_type))
                            symbol_names.append(symbol_name)

                    # Extract symbol relationships (CALLS and REFERENCES)
                    try:
                        relationship_queries = self._extract_symbol_references(
                            content, parsed_symbols, filepath
                        )
                        symbol_relationships.extend(relationship_queries)
                        logger.debug(
                            f"Found {len(relationship_queries)} symbol relationships in {filepath}")
                    except Exception as rel_err:
                        logger.warning(
                            f"Error extracting symbol relationships for {filepath}: {rel_err}")

                # Process imports from parsed code
                if parsed_imports:
                    for import_path in parsed_imports:
                        # Convert relative imports to absolute paths
                        if import_path.startswith('./') or import_path.startswith('../'):
                            # Handle relative imports
                            import_file_path = self._resolve_relative_import(
                                filepath, import_path)
                            if import_file_path:
                                imports.append((filepath, import_file_path))
                        elif not import_path.startswith('/') and '.' in import_path:
                            # Handle module-style imports (e.g., 'react', '@types/node')
                            # Skip external modules for now, focus on local files
                            continue
                        else:
                            # Handle absolute imports
                            imports.append((filepath, import_path))

            except Exception as parse_err:
                logger.error(f"Failed to parse {filepath}: {parse_err}")
                return {"success": False, "queries": [], "imports": [], "symbols": [], "symbol_relationships": []}

            # Simple config file handling
            if filepath.endswith(('config.js', 'config.ts', 'setup.js', 'setup.ts')):
                if "module.exports" in content or "export default" in content:
                    config_query = f'MERGE (f:File {{filepath: "{self._escape_cypher_string(filepath)}"}}) MERGE (f)-[:EXPORTS]->(:ConfigExport {{type: "configuration"}});'
                    queries.append(config_query)

            return {
                "success": True,
                "file": filepath,
                "queries": queries,
                "imports": imports,
                "symbols": symbols,
                "symbol_relationships": symbol_relationships,
                "symbol_names": symbol_names
            }

        except Exception as e:
            logger.error(f"Failed to build graph data for {filepath}: {e}")
            return {"success": False, "queries": [], "imports": [], "symbols": [], "symbol_relationships": []}

    async def _process_files_with_semaphore(
        self,
        files: List[str],
        container: dagger.Container,
        logger: logging.Logger,
        max_concurrent: int = 3
    ) -> Tuple[int, int, List[str], List[Tuple[str, str]], List[Tuple[str, str]], List[str], List[Tuple[str, str]]]:
        """Process files with semaphore-controlled concurrency and collect all queries."""
        if not files:
            return 0, 0, [], [], [], [], []

        semaphore = anyio.Semaphore(max_concurrent)
        results = []
        all_queries = []
        all_imports = []
        all_symbols = []
        all_symbol_relationships = []
        all_symbol_names: List[Tuple[str, str]] = []

        async def process_with_limit(filepath: str):
            async with semaphore:
                result = await self._safe_build_graph_data_for_file(filepath, container, logger)
                results.append(result["success"])
                if result["success"]:
                    all_queries.extend(result.get("queries", []))
                    all_imports.extend(result.get("imports", []))
                    all_symbols.extend(result.get("symbols", []))
                    all_symbol_relationships.extend(
                        result.get("symbol_relationships", []))
                    for n in result.get("symbol_names", []):
                        all_symbol_names.append((result.get("file", filepath), n))
                return result

        # Use anyio task group for concurrent processing
        async with anyio.create_task_group() as tg:
            for filepath in files:
                tg.start_soon(process_with_limit, filepath)

        # Count results
        processed = sum(1 for result in results if result is True)
        failed = sum(1 for result in results if result is False)

        logger.info(
            f"Processed {processed} files successfully, {failed} failed")
        logger.info(f"Generated {len(all_queries)} node/symbol queries, {len(all_imports)} import relationships, {len(all_symbols)} symbol relationships, {len(all_symbol_relationships)} symbol-to-symbol relationships, {len(all_symbol_names)} symbol names")

        return processed, failed, all_queries, all_imports, all_symbols, all_symbol_relationships, all_symbol_names

    @function
    async def setup_neo(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
    ) -> str:
        """Set up Neo4j service and return connection status."""
        logger = self._setup_logging()

        try:
            self.config = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config

            # Create Neo4j service
            self.neo_service = dag.neo_service(
                self.config_file,
                password=neo_password,
                github_access_token=github_access_token,
                neo_auth=neo_auth,
                neo_data=self.neo_data
            )
            # Test connection
            test_result = await self.neo_service.test_connection()
            logger.info(f"Neo4j connection established")
            clear = await self.neo_service.clear_database()
            if clear:
                logger.info("Neo4j database cleared successfully")

            return f"Neo4j connection successful: {test_result}"
        except Exception as e:
            logger.error(f"Failed to setup Neo4j: {e}")
            raise

    @function
    async def build_graph_for_repository(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to analyze")],
        branch: Annotated[str, Doc("Branch to analyze")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
        open_router_api_key: Annotated[dagger.Secret, Doc(
            "OpenRouter API key")]
    ) -> str:
        """Build a graph representation of an entire repository using concurrent query execution."""
        # Setup logging
        logger = self._setup_logging()
        processing_config = self._get_processing_config()

        try:
            # Setup Neo4j first
            await self.setup_neo(
                github_access_token=github_access_token,
                neo_password=neo_password,
                neo_auth=neo_auth
            )

            # Clone repository
            source = (
                await dag.git(url=repository_url, keep_git_dir=True, http_auth_token=github_access_token)
                .branch(branch)
                .tree()
            )

            # Build container
            self.config: YAMLConfig = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config
            container = await dag.builder(
                self.config_file
            ).build_test_environment(
                source=source,
                dockerfile_path=self.config.container.docker_file_path,
                open_router_api_key=open_router_api_key,
                provider=self.config.core_api.provider if self.config.core_api else None,
                openai_api_key=open_router_api_key
            )

            # Get working directory from config
            work_dir = getattr(self.config.container, 'work_dir', '/app')
            logger.info(f"Using work directory: {work_dir}")

            # Get file extensions to process
            file_extensions = getattr(
                # include TSX/JSX by default
                self.config.indexing, 'file_extensions', ['py', 'js', 'ts', 'tsx', 'jsx'])

            # Build find command for multiple extensions with exclusions
            find_cmd = ["find", work_dir, "-type", "f", "("]

            # Add extension patterns
            for i, ext in enumerate(file_extensions):
                ext = ext.strip('.')
                if i > 0:
                    find_cmd.append("-o")
                find_cmd.extend(["-name", f"*.{ext}"])

            find_cmd.append(")")

            # Exclude specific patterns including test directories
            find_cmd.extend([
                "!", "-path", "*/node_modules/*",
                "!", "-path", r"*/\.*",
                "!", "-path", "*/dist/*",
                "!", "-path", "*/build/*",
                "!", "-path", "*/tests/*",
                "!", "-path", "*/test/*",
                "!", "-path", "*/__tests__/*",
                "!", "-path", "*/spec/*",
                "!", "-path", "*/.pytest_cache/*",
                "!", "-path", "*/.coverage/*",
                "!", "-name", "*.test.*",
                "!", "-name", "*.spec.*",
                "!", "-name", "*_test.*",
                "!", "-name", "test_*",
                "!", "-name", "*.min.*",
                "!", "-name", "*.xml",
                "!", "-name", "*.json",
                "!", "-name", "*.md",
                "!", "-name", "*.yaml",
                "!", "-name", "*.yml"
            ])
            # Exclude user-configured ignore directories
            try:
                cfg_obj = YAMLConfig(**self.config) if isinstance(self.config, dict) else self.config
                user_ignores = list(getattr(getattr(cfg_obj, 'indexing', None), 'ignore_directories', []) or [])
                for d in user_ignores:
                    d = str(d).strip()
                    if not d:
                        continue
                    find_cmd.extend(["!", "-path", f"*/{d}/*"])
            except Exception:
                pass

            logger.info(f"Running find command: {' '.join(find_cmd)}")
            file_list = await container.with_exec(find_cmd).stdout()

            # Parse file list
            files = file_list.strip().split("\n")
            files = [f for f in files if f.strip()]

            if not files:
                logger.warning(
                    f"No files found in {work_dir} with extensions: {file_extensions}")
                return f"No files found in {work_dir} with specified extensions"

            logger.info(f"Found {len(files)} files to process")

            # Process files concurrently and collect all queries
            processed, failed, all_queries, all_imports, all_symbols, all_symbol_relationships, all_symbol_names = await self._process_files_with_semaphore(
                files=files,
                container=container,
                logger=logger,
                max_concurrent=processing_config['max_concurrent']
            )

            # Create constraints and indexes to match neo4j_schema
            logger.info("Creating constraints and indexes")
            constraints_and_indexes = [
                "CREATE CONSTRAINT file_path_constraint IF NOT EXISTS FOR (file:File) REQUIRE file.path IS UNIQUE",
                "CREATE CONSTRAINT file_filepath_unique IF NOT EXISTS FOR (f:File) REQUIRE f.filepath IS UNIQUE",
                "CREATE CONSTRAINT function_name_path_line IF NOT EXISTS FOR (function:Function) REQUIRE (function.name, function.filepath, function.start_line) IS UNIQUE",
                "CREATE CONSTRAINT class_name_path_line IF NOT EXISTS FOR (class:Class) REQUIRE (class.name, class.filepath, class.start_line) IS UNIQUE",
                "CREATE CONSTRAINT variable_name_path_line IF NOT EXISTS FOR (variable:Variable) REQUIRE (variable.name, variable.filepath, variable.line_number) IS UNIQUE",
                "CREATE CONSTRAINT method_name_path_line IF NOT EXISTS FOR (m:Method) REQUIRE (m.name, m.filepath, m.start_line) IS UNIQUE",
                "CREATE INDEX function_name_idx IF NOT EXISTS FOR (f:Function) ON (f.name)",
                "CREATE INDEX file_language_idx IF NOT EXISTS FOR (f:File) ON (f.language)",
                "CREATE INDEX file_filepath_idx IF NOT EXISTS FOR (f:File) ON (f.filepath)"
            ]

            for query in constraints_and_indexes:
                try:
                    await self.neo_service.run_query(query)
                    constraint_name = query.split()[2]
                    logger.info(f"Created constraint/index: {constraint_name}")
                except Exception as e:
                    logger.warning(f"Could not create constraint/index: {e}")

            # Execute file/symbol node queries
            logger.info(f"Executing {len(all_queries)} node/symbol queries using concurrent batches")
            await self._execute_queries_in_concurrent_batches(
                all_queries, "node/symbol", logger, batch_size=5, max_concurrent_batches=8
            )

            # Create DEFINED_IN relationships
            logger.info(f"Creating {len(all_symbols)} DEFINED_IN relationships using concurrent batches")
            relationship_queries = []
            for filepath, symbol_type in set(all_symbols):
                relationship_queries.append(self._build_relationship_cypher(filepath, symbol_type))
            await self._execute_queries_in_concurrent_batches(
                relationship_queries, "relationship", logger, batch_size=5, max_concurrent_batches=8
            )

            # Create IMPORTS relationships
            logger.info(f"Creating {len(all_imports)} import relationships using concurrent batches")
            import_queries = [self._build_import_cypher(frm, to) for frm, to in set(all_imports)]
            await self._execute_queries_in_concurrent_batches(
                import_queries, "import", logger, batch_size=5, max_concurrent_batches=8
            )

            # Within-file symbol relationships
            if all_symbol_relationships:
                logger.info(f"Creating {len(all_symbol_relationships)} symbol relationships using concurrent batches")
                await self._execute_queries_in_concurrent_batches(
                    all_symbol_relationships, "symbol-relationship", logger, batch_size=5, max_concurrent_batches=8
                )

            # Cross-file symbol resolution (reuses same logic as repository mode)
            try:
                file_to_imports: Dict[str, Set[str]] = {}
                for frm, to in set(all_imports):
                    file_to_imports.setdefault(frm, set()).add(to)
                symbols_by_file: Dict[str, Set[str]] = {}
                for f, n in all_symbol_names:
                    symbols_by_file.setdefault(f, set()).add(n)

                cross_file_queries: List[str] = []
                agent_utils = dag.agent_utils()
                for a_file, imported_files in file_to_imports.items():
                    try:
                        a_content = await container.file(a_file).contents()
                        code_file_json = await agent_utils.parse_code_file_to_json(a_content, a_file)
                        a_dict = json.loads(await code_file_json.contents())
                        a_symbol_map = {s.get("name"): s for s in a_dict.get("symbols", []) if s.get("name")}
                        a_lines = a_content.split('\n')

                        for b_file in imported_files:
                            for name in symbols_by_file.get(b_file, set()):
                                for i, line in enumerate(a_lines, 1):
                                    if name not in line:
                                        continue
                                    container_symbol = self._find_containing_symbol(i, a_symbol_map)
                                    if not container_symbol or container_symbol == name:
                                        continue
                                    rel_type = "CALLS" if f"{name}(" in line else "REFERENCES"
                                    cross_file_queries.append(
                                        self._build_cross_file_symbol_relationship_cypher(
                                            container_symbol, a_file, name, b_file, rel_type
                                        )
                                    )
                    except Exception as cf_err:
                        logger.debug(f"Cross-file resolution skipped for {a_file}: {cf_err}")

                if cross_file_queries:
                    logger.info(f"Creating {len(cross_file_queries)} cross-file symbol relationships")
                    await self._execute_queries_in_concurrent_batches(
                        cross_file_queries, "cross-file-symbol-relationship", logger, batch_size=5, max_concurrent_batches=8
                    )
            except Exception as e:
                logger.warning(f"Cross-file symbol resolution encountered an issue: {e}")

            # Verify connection
            test_result = await self.neo_service.test_connection()
            return (
                f"Graph built successfully: {processed} files processed, {failed} file failures, {len(all_queries)} nodes created."
                f" Database status: {test_result}"
            )

        except Exception as e:
            logger.error(f"Graph building failed: {e}")
            raise

    @function
    async def build_graph_for_directory(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        local_path: Annotated[str, Doc("Local path to a checked-out repository (attached directory mode)")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
        open_router_api_key: Annotated[dagger.Secret, Doc("OpenRouter API key")],
    ) -> str:
        """Build a graph representation of a locally checked-out repository (attached directory mode).
        Mirrors build_graph_for_repository, but uses a local path for the source tree.
        """
        logger = self._setup_logging()
        processing_config = self._get_processing_config()

        try:
            # Setup Neo4j first
            await self.setup_neo(
                github_access_token=github_access_token,
                neo_password=neo_password,
                neo_auth=neo_auth
            )

            # Use attached directory as source
            source = dag.host().directory(local_path)

            # Build container environment from local source
            self.config: YAMLConfig = YAMLConfig(
                **self.config) if isinstance(self.config, dict) else self.config
            container = await dag.builder(self.config_file).build_test_environment(
                source=source,
                dockerfile_path=self.config.container.docker_file_path,
                open_router_api_key=open_router_api_key,
                provider=self.config.core_api.provider if self.config.core_api else None,
                openai_api_key=open_router_api_key
            )

            # Get working directory from config
            work_dir = getattr(self.config.container, 'work_dir', '/app')
            logger.info(f"Using work directory: {work_dir}")

            # Get file extensions to process (include TSX/JSX by default)
            file_extensions = getattr(
                self.config.indexing, 'file_extensions', ['py', 'js', 'ts', 'tsx', 'jsx'])

            # Build find command for multiple extensions with exclusions
            find_cmd = ["find", work_dir, "-type", "f", "("]
            for i, ext in enumerate(file_extensions):
                ext = ext.strip('.')
                if i > 0:
                    find_cmd.append("-o")
                find_cmd.extend(["-name", f"*.{ext}"])
            find_cmd.append(")")

            # Exclude common vendor/test/build paths and noisy files
            find_cmd.extend([
                "!", "-path", "*/node_modules/*",
                "!", "-path", r"*/\.*",
                "!", "-path", "*/dist/*",
                "!", "-path", "*/build/*",
                "!", "-path", "*/tests/*",
                "!", "-path", "*/test/*",
                "!", "-path", "*/__tests__/*",
                "!", "-path", "*/spec/*",
                "!", "-path", "*/.pytest_cache/*",
                "!", "-name", "*.test.*",
                "!", "-name", "*.spec.*",
                "!", "-name", "*_test.*",
                "!", "-name", "test_*",
                "!", "-name", "*.min.*",
                "!", "-name", "*.xml",
                "!", "-name", "*.json",
                "!", "-name", "*.md",
                "!", "-name", "*.yaml",
                "!", "-name", "*.yml"
            ])
            # Exclude user-configured ignore directories
            try:
                cfg_obj = YAMLConfig(**self.config) if isinstance(self.config, dict) else self.config
                user_ignores = list(getattr(getattr(cfg_obj, 'indexing', None), 'ignore_directories', []) or [])
                for d in user_ignores:
                    d = str(d).strip()
                    if not d:
                        continue
                    find_cmd.extend(["!", "-path", f"*/{d}/*"])
            except Exception:
                pass

            logger.info(f"Running find command: {' '.join(find_cmd)}")
            file_list = await container.with_exec(find_cmd).stdout()
            files = [f for f in file_list.strip().split("\n") if f.strip()]

            if not files:
                logger.warning(f"No files found in {work_dir} with extensions: {file_extensions}")
                return f"No files found in {work_dir} with specified extensions"

            logger.info(f"Found {len(files)} files to process")

            # Process files concurrently and collect all queries
            processed, failed, all_queries, all_imports, all_symbols, all_symbol_relationships, all_symbol_names = await self._process_files_with_semaphore(
                files=files,
                container=container,
                logger=logger,
                max_concurrent=processing_config['max_concurrent']
            )

            # Create constraints and indexes to match neo4j_schema
            logger.info("Creating constraints and indexes")
            constraints_and_indexes = [
                "CREATE CONSTRAINT file_path_constraint IF NOT EXISTS FOR (file:File) REQUIRE file.path IS UNIQUE",
                "CREATE CONSTRAINT file_filepath_unique IF NOT EXISTS FOR (f:File) REQUIRE f.filepath IS UNIQUE",
                "CREATE CONSTRAINT function_name_path_line IF NOT EXISTS FOR (function:Function) REQUIRE (function.name, function.filepath, function.start_line) IS UNIQUE",
                "CREATE CONSTRAINT class_name_path_line IF NOT EXISTS FOR (class:Class) REQUIRE (class.name, class.filepath, class.start_line) IS UNIQUE",
                "CREATE CONSTRAINT variable_name_path_line IF NOT EXISTS FOR (variable:Variable) REQUIRE (variable.name, variable.filepath, variable.line_number) IS UNIQUE",
                "CREATE CONSTRAINT method_name_path_line IF NOT EXISTS FOR (m:Method) REQUIRE (m.name, m.filepath, m.start_line) IS UNIQUE",
                "CREATE INDEX function_name_idx IF NOT EXISTS FOR (f:Function) ON (f.name)",
                "CREATE INDEX file_language_idx IF NOT EXISTS FOR (f:File) ON (f.language)",
                "CREATE INDEX file_filepath_idx IF NOT EXISTS FOR (f:File) ON (f.filepath)"
            ]

            for query in constraints_and_indexes:
                try:
                    await self.neo_service.run_query(query)
                    constraint_name = query.split()[2]
                    logger.info(f"Created constraint/index: {constraint_name}")
                except Exception as e:
                    logger.warning(f"Could not create constraint/index: {e}")

            # Execute file/symbol node queries
            logger.info(f"Executing {len(all_queries)} node/symbol queries using concurrent batches")
            await self._execute_queries_in_concurrent_batches(
                all_queries, "node/symbol", logger, batch_size=5, max_concurrent_batches=8
            )

            # Create DEFINED_IN relationships
            logger.info(f"Creating {len(all_symbols)} DEFINED_IN relationships using concurrent batches")
            relationship_queries = []
            for filepath, symbol_type in set(all_symbols):
                relationship_queries.append(self._build_relationship_cypher(filepath, symbol_type))
            await self._execute_queries_in_concurrent_batches(
                relationship_queries, "relationship", logger, batch_size=5, max_concurrent_batches=8
            )

            # Create IMPORTS relationships
            logger.info(f"Creating {len(all_imports)} import relationships using concurrent batches")
            import_queries = [self._build_import_cypher(frm, to) for frm, to in set(all_imports)]
            await self._execute_queries_in_concurrent_batches(
                import_queries, "import", logger, batch_size=5, max_concurrent_batches=8
            )

            # Within-file symbol relationships
            if all_symbol_relationships:
                logger.info(f"Creating {len(all_symbol_relationships)} symbol relationships using concurrent batches")
                await self._execute_queries_in_concurrent_batches(
                    all_symbol_relationships, "symbol-relationship", logger, batch_size=5, max_concurrent_batches=8
                )

            # Cross-file symbol resolution (reuses same logic as repository mode)
            try:
                file_to_imports: Dict[str, Set[str]] = {}
                for frm, to in set(all_imports):
                    file_to_imports.setdefault(frm, set()).add(to)
                symbols_by_file: Dict[str, Set[str]] = {}
                for f, n in all_symbol_names:
                    symbols_by_file.setdefault(f, set()).add(n)

                cross_file_queries: List[str] = []
                agent_utils = dagger.agent_utils()
                for a_file, imported_files in file_to_imports.items():
                    try:
                        a_content = await container.file(a_file).contents()
                        code_file_json = await agent_utils.parse_code_file_to_json(a_content, a_file)
                        a_dict = json.loads(await code_file_json.contents())
                        a_symbol_map = {s.get("name"): s for s in a_dict.get("symbols", []) if s.get("name")}
                        a_lines = a_content.split('\n')

                        for b_file in imported_files:
                            for name in symbols_by_file.get(b_file, set()):
                                for i, line in enumerate(a_lines, 1):
                                    if name not in line:
                                        continue
                                    container_symbol = self._find_containing_symbol(i, a_symbol_map)
                                    if not container_symbol or container_symbol == name:
                                        continue
                                    rel_type = "CALLS" if f"{name}(" in line else "REFERENCES"
                                    cross_file_queries.append(
                                        self._build_cross_file_symbol_relationship_cypher(
                                            container_symbol, a_file, name, b_file, rel_type
                                        )
                                    )
                    except Exception as cf_err:
                        logger.debug(f"Cross-file resolution skipped for {a_file}: {cf_err}")

                if cross_file_queries:
                    logger.info(f"Creating {len(cross_file_queries)} cross-file symbol relationships")
                    await self._execute_queries_in_concurrent_batches(
                        cross_file_queries, "cross-file-symbol-relationship", logger, batch_size=5, max_concurrent_batches=8
                    )
            except Exception as e:
                logger.warning(f"Cross-file symbol resolution encountered an issue: {e}")

            # Verify connection
            test_result = await self.neo_service.test_connection()
            return (
                f"Graph built successfully from directory: {processed} files processed, {failed} file failures. "
                f"Database status: {test_result}"
            )

        except Exception as e:
            logger.error(f"Graph building (directory) failed: {e}")
            raise

    @function
    async def build_graph_for_repository_export(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        repository_url: Annotated[str, Doc("Repository URL to analyze")],
        branch: Annotated[str, Doc("Branch to analyze")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
        open_router_api_key: Annotated[dagger.Secret, Doc("OpenRouter API key")],
        dry_run: Annotated[bool, Doc("If true, export batches without executing")] = True,
    ) -> dagger.Directory:
        """Export chunked Cypher batches for a remote repo; when dry_run is True, do not execute queries."""
        logger = self._setup_logging()
        processing_config = self._get_processing_config()

        # Clone repository tree
        source = (
            await dag.git(url=repository_url, keep_git_dir=True, http_auth_token=github_access_token)
            .branch(branch)
            .tree()
        )

        # Build analysis container (no Neo connection required for dry-run)
        cfg: YAMLConfig = YAMLConfig(**self.config) if isinstance(self.config, dict) else self.config
        container = await dag.builder(self.config_file).build_test_environment(
            source=source,
            dockerfile_path=cfg.container.docker_file_path,
            open_router_api_key=open_router_api_key,
            provider=(cfg.core_api.provider if getattr(cfg, 'core_api', None) else None),
            openai_api_key=open_router_api_key
        )
        work_dir = getattr(cfg.container, 'work_dir', '/app')

        # Discover files by configured extensions
        file_extensions = getattr(cfg.indexing, 'file_extensions', ['py', 'js', 'ts', 'tsx', 'jsx'])
        find_cmd = ["find", work_dir, "-type", "f", "("]
        for i, ext in enumerate(file_extensions):
            ext = str(ext).strip('.')
            if i > 0:
                find_cmd.append("-o")
            find_cmd.extend(["-name", f"*.{ext}"])
        find_cmd.append(")")
        # Basic excludes + user-configured ignore_directories
        find_cmd.extend([
            "!", "-path", "*/node_modules/*",
            "!", "-path", r"*/\.*",
            "!", "-path", "*/dist/*",
            "!", "-path", "*/build/*",
            "!", "-path", "*/tests/*",
            "!", "-path", "*/test/*",
            "!", "-path", "*/__tests__/*",
            "!", "-path", "*/spec/*",
            "!", "-path", "*/.pytest_cache/*",
        ])
        try:
            ignores = list(getattr(getattr(cfg, 'indexing', None), 'ignore_directories', []) or [])
            for d in ignores:
                d = str(d).strip()
                if d:
                    find_cmd.extend(["!", "-path", f"*/{d}/*"])
        except Exception:
            pass
        files = [f for f in (await container.with_exec(find_cmd).stdout()).strip().split("\n") if f.strip()]

        # Parse & build queries
        processed, failed, all_queries, all_imports, all_symbols, all_symbol_relationships, all_symbol_names = await self._process_files_with_semaphore(
            files=files,
            container=container,
            logger=logger,
            max_concurrent=processing_config['max_concurrent']
        )

        # Build relationship & import queries
        relationship_queries = self._build_relationship_queries(all_symbols)
        import_queries = self._build_import_queries(all_imports)

        # Capture batches without executing when dry_run=True
        export_acc: Dict[str, List[str]] = {}
        throttle = processing_config.get('throttle_ms')
        await self._execute_queries_in_concurrent_batches(
            all_queries, "node-symbol", logger,
            batch_size=processing_config.get('batch_size', 5),
            max_concurrent_batches=processing_config.get('max_concurrent', 8),
            export_accumulator=export_acc,
            execute=(not dry_run),
            throttle_ms=throttle,
        )
        await self._execute_queries_in_concurrent_batches(
            relationship_queries, "defined-in", logger,
            batch_size=processing_config.get('batch_size', 5),
            max_concurrent_batches=processing_config.get('max_concurrent', 8),
            export_accumulator=export_acc,
            execute=(not dry_run),
            throttle_ms=throttle,
        )
        await self._execute_queries_in_concurrent_batches(
            import_queries, "import", logger,
            batch_size=processing_config.get('batch_size', 5),
            max_concurrent_batches=processing_config.get('max_concurrent', 8),
            export_accumulator=export_acc,
            execute=(not dry_run),
            throttle_ms=throttle,
        )
        if all_symbol_relationships:
            await self._execute_queries_in_concurrent_batches(
                all_symbol_relationships, "symbol-relationship", logger,
                batch_size=processing_config.get('batch_size', 5),
                max_concurrent_batches=processing_config.get('max_concurrent', 8),
                export_accumulator=export_acc,
                execute=(not dry_run),
                throttle_ms=throttle,
            )

        # Setup file (semicolon separated for Neo4j 5.x)
        constraints_and_indexes = self._get_constraints_and_indexes()
        export_prefix = "batches"
        exports: List[Tuple[str, str]] = [
            (f"{export_prefix}/setup/constraints_and_indexes.cypher", ";\n".join(constraints_and_indexes) + ";\n")
        ]
        summary = {
            "processed_files": processed,
            "failed_files": failed,
            "batches_dir": export_prefix,
            "dry_run": bool(dry_run),
            "batch_counts": {qt: len(bl) for qt, bl in export_acc.items()},
        }
        # Add chunked files + summary
        exports.extend(self._build_chunked_export_files(export_prefix, export_acc, summary))

        # Materialize Directory
        out_dir = dag.directory()
        for rel_path, content in exports:
            out_dir = out_dir.with_new_file(rel_path, content)
        return out_dir

    @function
    async def build_graph_for_directory_export(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        local_path: Annotated[str, Doc("Local path to a checked-out repository")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
        open_router_api_key: Annotated[dagger.Secret, Doc("OpenRouter API key")],
        dry_run: Annotated[bool, Doc("If true, export batches without executing")] = True,
    ) -> dagger.Directory:
        """Export chunked Cypher batches for a local directory; when dry_run is True, do not execute queries."""
        logger = self._setup_logging()
        processing_config = self._get_processing_config()

        # Host directory source
        source = dag.host().directory(local_path)
        cfg: YAMLConfig = YAMLConfig(**self.config) if isinstance(self.config, dict) else self.config
        container = await dag.builder(self.config_file).build_test_environment(
            source=source,
            dockerfile_path=cfg.container.docker_file_path,
            open_router_api_key=open_router_api_key,
            provider=(cfg.core_api.provider if getattr(cfg, 'core_api', None) else None),
            openai_api_key=open_router_api_key
        )
        work_dir = getattr(cfg.container, 'work_dir', '/app')

        # Discover files
        file_extensions = getattr(cfg.indexing, 'file_extensions', ['py', 'js', 'ts', 'tsx', 'jsx'])
        find_cmd = ["find", work_dir, "-type", "f", "("]
        for i, ext in enumerate(file_extensions):
            ext = str(ext).strip('.')
            if i > 0:
                find_cmd.append("-o")
            find_cmd.extend(["-name", f"*.{ext}"])
        find_cmd.append(")")
        find_cmd.extend([
            "!", "-path", "*/node_modules/*",
            "!", "-path", r"*/\.*",
            "!", "-path", "*/dist/*",
            "!", "-path", "*/build/*",
            "!", "-path", "*/tests/*",
            "!", "-path", "*/test/*",
            "!", "-path", "*/__tests__/*",
            "!", "-path", "*/spec/*",
            "!", "-path", "*/.pytest_cache/*",
        ])
        try:
            ignores = list(getattr(getattr(cfg, 'indexing', None), 'ignore_directories', []) or [])
            for d in ignores:
                d = str(d).strip()
                if d:
                    find_cmd.extend(["!", "-path", f"*/{d}/*"])
        except Exception:
            pass
        files = [f for f in (await container.with_exec(find_cmd).stdout()).strip().split("\n") if f.strip()]

        # Parse & build queries
        processed, failed, all_queries, all_imports, all_symbols, all_symbol_relationships, all_symbol_names = await self._process_files_with_semaphore(
            files=files,
            container=container,
            logger=logger,
            max_concurrent=processing_config['max_concurrent']
        )

        relationship_queries = self._build_relationship_queries(all_symbols)
        import_queries = self._build_import_queries(all_imports)

        export_acc: Dict[str, List[str]] = {}
        throttle = processing_config.get('throttle_ms')
        await self._execute_queries_in_concurrent_batches(
            all_queries, "node-symbol", logger,
            batch_size=processing_config.get('batch_size', 5),
            max_concurrent_batches=processing_config.get('max_concurrent', 8),
            export_accumulator=export_acc,
            execute=(not dry_run),
            throttle_ms=throttle,
        )
        await self._execute_queries_in_concurrent_batches(
            relationship_queries, "defined-in", logger,
            batch_size=processing_config.get('batch_size', 5),
            max_concurrent_batches=processing_config.get('max_concurrent', 8),
            export_accumulator=export_acc,
            execute=(not dry_run),
            throttle_ms=throttle,
        )
        await self._execute_queries_in_concurrent_batches(
            import_queries, "import", logger,
            batch_size=processing_config.get('batch_size', 5),
            max_concurrent_batches=processing_config.get('max_concurrent', 8),
            export_accumulator=export_acc,
            execute=(not dry_run),
            throttle_ms=throttle,
        )
        if all_symbol_relationships:
            await self._execute_queries_in_concurrent_batches(
                all_symbol_relationships, "symbol-relationship", logger,
                batch_size=processing_config.get('batch_size', 5),
                max_concurrent_batches=processing_config.get('max_concurrent', 8),
                export_accumulator=export_acc,
                execute=(not dry_run),
                throttle_ms=throttle,
            )

        constraints_and_indexes = self._get_constraints_and_indexes()
        export_prefix = "batches"
        exports: List[Tuple[str, str]] = [
            (f"{export_prefix}/setup/constraints_and_indexes.cypher", ";\n".join(constraints_and_indexes) + ";\n")
        ]
        summary = {
            "processed_files": processed,
            "failed_files": failed,
            "batches_dir": export_prefix,
            "dry_run": bool(dry_run),
            "batch_counts": {qt: len(bl) for qt, bl in export_acc.items()},
        }
        exports.extend(self._build_chunked_export_files(export_prefix, export_acc, summary))

        out_dir = dag.directory()
        for rel_path, content in exports:
            out_dir = out_dir.with_new_file(rel_path, content)
        return out_dir

    def _build_relationship_queries(self, symbols: List[Tuple[str, str]]) -> List[str]:
        queries = []
        for filepath, symbol_type in set(symbols):
            queries.append(self._build_relationship_cypher(filepath, symbol_type))
        return queries

    def _build_import_queries(self, imports: List[Tuple[str, str]]) -> List[str]:
        return [self._build_import_cypher(frm, to) for frm, to in set(imports)]

    def _get_constraints_and_indexes(self) -> List[str]:
        return [
            "CREATE CONSTRAINT file_path_constraint IF NOT EXISTS FOR (file:File) REQUIRE file.path IS UNIQUE",
            "CREATE CONSTRAINT file_filepath_unique IF NOT EXISTS FOR (f:File) REQUIRE f.filepath IS UNIQUE",
            "CREATE CONSTRAINT function_name_path_line IF NOT EXISTS FOR (function:Function) REQUIRE (function.name, function.filepath, function.start_line) IS UNIQUE",
            "CREATE CONSTRAINT class_name_path_line IF NOT EXISTS FOR (class:Class) REQUIRE (class.name, class.filepath, class.start_line) IS UNIQUE",
            "CREATE CONSTRAINT variable_name_path_line IF NOT EXISTS FOR (variable:Variable) REQUIRE (variable.name, variable.filepath, variable.line_number) IS UNIQUE",
            "CREATE CONSTRAINT method_name_path_line IF NOT EXISTS FOR (m:Method) REQUIRE (m.name, m.filepath, m.start_line) IS UNIQUE",
            "CREATE INDEX function_name_idx IF NOT EXISTS FOR (f:Function) ON (f.name)",
            "CREATE INDEX file_language_idx IF NOT EXISTS FOR (f:File) ON (f.language)",
            "CREATE INDEX file_filepath_idx IF NOT EXISTS FOR (f:File) ON (f.filepath)"
        ]

