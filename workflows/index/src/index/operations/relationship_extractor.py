from typing import Optional
import re
import os
import logging
from typing import Dict, List, Any

from index.services.neo4j_service import Neo4jService  # Updated import


class RelationshipExtractor:
    """Extracts relationships between code elements"""

    @staticmethod
    async def extract_relationships(filepath: str, code_file: Any, neo4j: Optional[Neo4jService] = None) -> None:
        """Extract relationships between code symbols"""
        if not neo4j or not hasattr(code_file, 'symbols') or not code_file.symbols:
            return

        logger = logging.getLogger(__name__)

        try:
            # Map symbols by name for quick lookup
            symbol_map = {}
            for symbol in code_file.symbols:
                if hasattr(symbol, 'name') and symbol.name:
                    symbol_map[symbol.name] = symbol

            # Process internal relationships between symbols
            await RelationshipExtractor._extract_internal_relationships(filepath, code_file, symbol_map, neo4j, logger)

            # Process file import relationships
            await RelationshipExtractor._extract_file_imports(filepath, code_file, neo4j, logger)

        except Exception as e:
            logger.error(f"Error extracting relationships for {filepath}: {e}")

    @staticmethod
    async def _extract_internal_relationships(filepath: str, code_file: Any, symbol_map: Dict, neo4j: Neo4jService, logger: logging.Logger) -> None:
        """Extract relationships between symbols within the same file"""
        for symbol in code_file.symbols:
            if not hasattr(symbol, 'name') or not symbol.name:
                continue

            symbol_type = symbol.type.capitalize() if hasattr(symbol, 'type') else 'Symbol'
            symbol_name = symbol.name
            line_number = getattr(symbol, 'line_number', 0)

            # Extract class inheritance
            if symbol_type == 'Class' and hasattr(symbol, 'base_classes'):
                for base in getattr(symbol, 'base_classes', []):
                    if base in symbol_map:
                        base_symbol = symbol_map[base]
                        base_type = base_symbol.type.capitalize() if hasattr(
                            base_symbol, 'type') else 'Symbol'

                        await neo4j.add_relationship(
                            from_type=symbol_type,
                            from_name=symbol_name,
                            from_filepath=filepath,
                            from_line=line_number,
                            to_type=base_type,
                            to_name=base,
                            to_filepath=filepath,
                            to_line=getattr(base_symbol, 'line_number', 0),
                            rel_type='INHERITS_FROM'
                        )

            # Extract function calls
            if hasattr(symbol, 'calls'):
                for called_name in getattr(symbol, 'calls', []):
                    if called_name in symbol_map:
                        called_symbol = symbol_map[called_name]
                        called_type = called_symbol.type.capitalize() if hasattr(
                            called_symbol, 'type') else 'Symbol'

                        await neo4j.add_relationship(
                            from_type=symbol_type,
                            from_name=symbol_name,
                            from_filepath=filepath,
                            from_line=line_number,
                            to_type=called_type,
                            to_name=called_name,
                            to_filepath=filepath,
                            to_line=getattr(called_symbol, 'line_number', 0),
                            rel_type='CALLS'
                        )

    @staticmethod
    async def _extract_file_imports(filepath: str, code_file: Any, neo4j: Neo4jService, logger: logging.Logger) -> None:
        """Extract file import relationships"""
        logger.info(f"Extracting imports from {filepath}")
        
        if not hasattr(code_file, 'language'):
            logger.info(f"Skipping import extraction for {filepath}: no language attribute")
            return
            
        language = getattr(code_file, 'language', '').lower()
        content = getattr(code_file, 'content', '')
        
        if not content:
            logger.info(f"Skipping import extraction for {filepath}: no content")
            return

        content_lines = content.split('\n')
        imported_files = set()  # Track to avoid duplicates

        try:
            # Python imports
            if language in ('python', 'py'):
                await RelationshipExtractor._extract_python_imports(filepath, content_lines, neo4j, imported_files)

            # JavaScript/TypeScript imports
            elif language in ('javascript', 'typescript', 'js', 'ts', 'jsx', 'tsx'):
                await RelationshipExtractor._extract_js_imports(filepath, content_lines, neo4j, imported_files)

            # Java imports
            elif language in ('java'):
                await RelationshipExtractor._extract_java_imports(filepath, content_lines, neo4j, imported_files)

            # Go imports
            elif language in ('go'):
                await RelationshipExtractor._extract_go_imports(filepath, content_lines, neo4j, imported_files)

            # Rust imports
            elif language in ('rust', 'rs'):
                await RelationshipExtractor._extract_rust_imports(filepath, content_lines, neo4j, imported_files)

        except Exception as e:
            logger.error(f"Error extracting imports for {filepath}: {e}")
        
        logger.info(f"Found {len(imported_files)} imports in {filepath}")

    @staticmethod
    async def _extract_python_imports(filepath: str, content_lines: List[str], neo4j: Neo4jService, imported_files: set) -> None:
        """Extract Python import statements"""
        # Python import patterns
        patterns = [
            r'import\s+(\w+(?:\.\w+)*)',  # import module
            r'from\s+([^\s]+)\s+import',   # from module import ...
            r'import\s+(\w+(?:\.\w+)*)\s+as\s+\w+'  # import module as alias
        ]

        for i, line in enumerate(content_lines):
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    module_path = match.group(1).replace('.', '/')

                    # Skip standard library modules
                    if '/' not in module_path:
                        continue

                    # Check if it's a local module (file exists in repo)
                    possible_paths = [
                        f"{module_path}.py",
                        f"{module_path}/__init__.py"
                    ]

                    for path in possible_paths:
                        if path not in imported_files:
                            imported_files.add(path)
                            await neo4j.add_relationship(
                                from_type='File',
                                from_name='',
                                from_filepath=filepath,
                                from_line=i + 1,
                                to_type='File',
                                to_name='',
                                to_filepath=path,
                                to_line=0,
                                rel_type='IMPORTS'
                            )

    @staticmethod
    async def _extract_js_imports(filepath: str, content_lines: List[str], neo4j: Neo4jService, imported_files: set) -> None:
        """Extract JavaScript/TypeScript import statements"""
        # JS/TS import patterns
        patterns = [
            # import x from 'module'
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',            # require('module')
            # import('module') - dynamic import
            r'import\([\'"]([^\'"]+)[\'"]\)'
        ]

        for i, line in enumerate(content_lines):
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    module_path = match.group(1)

                    # Skip node_modules and absolute imports
                    if module_path.startswith('@') or not (module_path.startswith('./') or module_path.startswith('../')):
                        continue

                    # Resolve relative path
                    current_dir = os.path.dirname(filepath)
                    abs_path = os.path.normpath(
                        os.path.join(current_dir, module_path))

                    # Try common extensions if none specified
                    if not module_path.endswith(('.js', '.ts', '.jsx', '.tsx', '.mjs')):
                        possible_paths = [
                            f"{abs_path}.js", f"{abs_path}.ts",
                            f"{abs_path}.jsx", f"{abs_path}.tsx",
                            f"{abs_path}/index.js", f"{abs_path}/index.ts"
                        ]
                        for path in possible_paths:
                            if path not in imported_files:
                                imported_files.add(path)
                                await neo4j.add_relationship(
                                    from_type='File',
                                    from_name='',
                                    from_filepath=filepath,
                                    from_line=i + 1,
                                    to_type='File',
                                    to_name='',
                                    to_filepath=path,
                                    to_line=0,
                                    rel_type='IMPORTS'
                                )
                    else:
                        if abs_path not in imported_files:
                            imported_files.add(abs_path)
                            await neo4j.add_relationship(
                                from_type='File',
                                from_name='',
                                from_filepath=filepath,
                                from_line=i + 1,
                                to_type='File',
                                to_name='',
                                to_filepath=abs_path,
                                to_line=0,
                                rel_type='IMPORTS'
                            )

    @staticmethod
    async def _extract_java_imports(filepath: str, content_lines: List[str], neo4j: Neo4jService, imported_files: set) -> None:
        """Extract Java import statements"""
        pattern = r'import\s+([^;]+);'

        for i, line in enumerate(content_lines):
            for match in re.finditer(pattern, line):
                package_path = match.group(1).replace('.', '/') + '.java'

                if package_path not in imported_files:
                    imported_files.add(package_path)
                    await neo4j.add_relationship(
                        from_type='File',
                        from_name='',
                        from_filepath=filepath,
                        from_line=i + 1,
                        to_type='File',
                        to_name='',
                        to_filepath=package_path,
                        to_line=0,
                        rel_type='IMPORTS'
                    )

    @staticmethod
    async def _extract_go_imports(filepath: str, content_lines: List[str], neo4j: Neo4jService, imported_files: set) -> None:
        """Extract Go import statements"""
        in_import_block = False
        import_line = -1

        for i, line in enumerate(content_lines):
            # Check for single line import
            single_match = re.match(r'import\s+[\'"]([^\'"]+)[\'"]', line)
            if single_match:
                package_path = single_match.group(1)
                if package_path not in imported_files:
                    imported_files.add(package_path)
                    await neo4j.add_relationship(
                        from_type='File',
                        from_name='',
                        from_filepath=filepath,
                        from_line=i + 1,
                        to_type='File',
                        to_name='',
                        to_filepath=package_path + '.go',
                        to_line=0,
                        rel_type='IMPORTS'
                    )
                continue

            # Check for multi-line import block
            if re.match(r'import\s+\(', line):
                in_import_block = True
                import_line = i
                continue

            if in_import_block:
                if re.match(r'\)', line):
                    in_import_block = False
                    continue

                pkg_match = re.match(r'\s*[\'"]([^\'"]+)[\'"]', line)
                if pkg_match:
                    package_path = pkg_match.group(1)
                    if package_path not in imported_files:
                        imported_files.add(package_path)
                        await neo4j.add_relationship(
                            from_type='File',
                            from_name='',
                            from_filepath=filepath,
                            from_line=import_line + 1,
                            to_type='File',
                            to_name='',
                            to_filepath=package_path + '.go',
                            to_line=0,
                            rel_type='IMPORTS'
                        )

    @staticmethod
    async def _extract_rust_imports(filepath: str, content_lines: List[str], neo4j: Neo4jService, imported_files: set) -> None:
        """Extract Rust import statements"""
        patterns = [
            r'use\s+([^:;]+)(?:::.*)?;',  # use std::io;
            r'extern\s+crate\s+([^;]+);'   # extern crate rand;
        ]

        for i, line in enumerate(content_lines):
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    module_path = match.group(1).replace('::', '/') + '.rs'

                    if module_path not in imported_files:
                        imported_files.add(module_path)
                        await neo4j.add_relationship(
                            from_type='File',
                            from_name='',
                            from_filepath=filepath,
                            from_line=i + 1,
                            to_type='File',
                            to_name='',
                            to_filepath=module_path,
                            to_line=0,
                            rel_type='IMPORTS'
                        )
