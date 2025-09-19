import re
import os
import logging
from typing import Dict, List, Set, Optional

from dagger.client.gen import NeoService


class ImportAnalyzer:
    """Analyzes source files for import statements using direct regex patterns."""

    @staticmethod
    async def analyze_file_imports(
        filepath: str,
        content: str,
        neo4j: Optional[NeoService] = None
    ) -> Set[str]:
        """
        Analyze a file for imports without using AST parsing.
        Returns the set of imported files and creates relationships in Neo4j.
        """
        logger = logging.getLogger(__name__)
        language = ImportAnalyzer._detect_language(filepath)
        imported_files = set()

        try:
            # Skip binary files and very large content
            if not content or len(content) > 1_000_000:
                return imported_files

            # Process imports based on language
            if language == 'python':
                imported_files = ImportAnalyzer._analyze_python_imports(
                    filepath, content)
            elif language in ('javascript', 'typescript'):
                imported_files = ImportAnalyzer._analyze_js_imports(
                    filepath, content)
            elif language == 'java':
                imported_files = ImportAnalyzer._analyze_java_imports(
                    filepath, content)
            elif language == 'go':
                imported_files = ImportAnalyzer._analyze_go_imports(
                    filepath, content)
            elif language == 'rust':
                imported_files = ImportAnalyzer._analyze_rust_imports(
                    filepath, content)

            # Create relationships in Neo4j if service is provided
            if neo4j and imported_files:
                await ImportAnalyzer._create_import_relationships(
                    filepath, imported_files, neo4j, logger)

            return imported_files

        except Exception as e:
            logger.error(f"Error analyzing imports for {filepath}: {e}")
            return set()

    @staticmethod
    def _detect_language(filepath: str) -> str:
        """Detect programming language from file extension."""
        ext = filepath.split('.')[-1].lower() if '.' in filepath else ''

        language_map = {
            'py': 'python',
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'java': 'java',
            'go': 'go',
            'rs': 'rust',
            'c': 'c',
            'cpp': 'cpp',
            'h': 'c',
            'hpp': 'cpp',
            'rb': 'ruby',
            'php': 'php'
        }

        return language_map.get(ext, 'unknown')

    @staticmethod
    def _analyze_python_imports(filepath: str, content: str) -> Set[str]:
        """Extract Python import statements using regex."""
        imported_files = set()
        current_dir = os.path.dirname(filepath)
        content_lines = content.split('\n')

        # Python import patterns
        patterns = [
            r'import\s+(\w+(?:\.\w+)*)',          # import module[.submodule]
            # from module[.submodule] import ...
            r'from\s+([^\s]+)\s+import',
            # import module[.submodule] as alias
            r'import\s+(\w+(?:\.\w+)*)\s+as\s+\w+'
        ]

        for line_num, line in enumerate(content_lines):
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    module_path = match.group(1).replace('.', '/')

                    # Process relative imports (from . import X)
                    if module_path.startswith('.'):
                        # Count leading dots for relative import level
                        dots = len(module_path) - len(module_path.lstrip('.'))
                        relative_path = module_path[dots:]

                        # Go up by the number of dots
                        parent_path = current_dir
                        for _ in range(dots):
                            parent_path = os.path.dirname(parent_path)

                        if relative_path:
                            module_path = os.path.join(
                                parent_path, relative_path)
                        else:
                            module_path = parent_path

                    # Skip standard library imports
                    if '/' not in module_path:
                        continue

                    # Try to map to actual files with .py extension
                    possible_paths = [
                        f"{module_path}.py",
                        f"{module_path}/__init__.py",
                        # More variations can be added
                    ]

                    for path in possible_paths:
                        # Normalize path
                        norm_path = path
                        if norm_path.startswith('./'):
                            norm_path = norm_path[2:]
                        imported_files.add(norm_path)

        return imported_files

    @staticmethod
    def _analyze_js_imports(filepath: str, content: str) -> Set[str]:
        """Extract JavaScript/TypeScript import statements using regex."""
        imported_files = set()
        current_dir = os.path.dirname(filepath)
        content_lines = content.split('\n')

        # JS/TS import patterns
        patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',  # ES6 import
            r'require\(\s*[\'"]([^\'"]+)[\'"]\s*\)',      # CommonJS require
            r'import\(\s*[\'"]([^\'"]+)[\'"]\s*\)'        # Dynamic import
        ]

        for line in content_lines:
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    module_path = match.group(1)

                    # Skip package imports (not relative)
                    if not module_path.startswith('./') and not module_path.startswith('../'):
                        continue

                    # Resolve relative path
                    abs_path = os.path.normpath(
                        os.path.join(current_dir, module_path))

                    # Try common extensions if none specified
                    if not module_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                        possible_paths = [
                            f"{abs_path}.js", f"{abs_path}.ts",
                            f"{abs_path}.jsx", f"{abs_path}.tsx",
                            f"{abs_path}/index.js", f"{abs_path}/index.ts"
                        ]
                        for path in possible_paths:
                            # Normalize path
                            norm_path = path
                            if norm_path.startswith('./'):
                                norm_path = norm_path[2:]
                            imported_files.add(norm_path)
                    else:
                        # Normalize path
                        norm_path = abs_path
                        if norm_path.startswith('./'):
                            norm_path = norm_path[2:]
                        imported_files.add(norm_path)

        return imported_files

    @staticmethod
    def _analyze_java_imports(filepath: str, content: str) -> Set[str]:
        """Extract Java import statements using regex."""
        imported_files = set()
        content_lines = content.split('\n')

        pattern = r'import\s+([^;]+);'

        for line in content_lines:
            for match in re.finditer(pattern, line):
                package_path = match.group(1).replace('.', '/') + '.java'
                imported_files.add(package_path)

        return imported_files

    @staticmethod
    def _analyze_go_imports(filepath: str, content: str) -> Set[str]:
        """Extract Go import statements using regex."""
        imported_files = set()
        content_lines = content.split('\n')

        in_import_block = False

        for line in content_lines:
            # Check for single line import
            single_match = re.match(r'import\s+[\'"]([^\'"]+)[\'"]', line)
            if single_match:
                package_path = single_match.group(1) + '.go'
                imported_files.add(package_path)
                continue

            # Check for multi-line import block
            if re.match(r'import\s+\(', line):
                in_import_block = True
                continue

            if in_import_block:
                if re.match(r'\)', line):
                    in_import_block = False
                    continue

                pkg_match = re.match(r'\s*[\'"]([^\'"]+)[\'"]', line)
                if pkg_match:
                    package_path = pkg_match.group(1) + '.go'
                    imported_files.add(package_path)

        return imported_files

    @staticmethod
    def _analyze_rust_imports(filepath: str, content: str) -> Set[str]:
        """Extract Rust import statements using regex."""
        imported_files = set()
        content_lines = content.split('\n')

        patterns = [
            r'use\s+([^:;]+)(?:::.*)?;',  # use std::io;
            r'extern\s+crate\s+([^;]+);'   # extern crate rand;
        ]

        for line in content_lines:
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    module_path = match.group(1).replace('::', '/') + '.rs'
                    imported_files.add(module_path)

        return imported_files

    @staticmethod
    async def _create_import_relationships(
        filepath: str,
        imported_files: Set[str],
        neo4j: NeoService,
        logger: logging.Logger
    ) -> None:
        """Create import relationships in Neo4j."""
        for imported_file in imported_files:
            try:
                # First ensure both file nodes exist
                await neo4j.run_query(f"""
                    MERGE (source:File {{filepath: "{filepath}"}})
                    MERGE (target:File {{filepath: "{imported_file}"}})
                    MERGE (source)-[:IMPORTS]->(target)
                """)

                logger.info(
                    f"Created import relationship: {filepath} -> {imported_file}")
            except Exception as e:
                logger.error(f"Error: {e}")
