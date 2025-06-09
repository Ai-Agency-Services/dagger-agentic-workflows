import re
from typing import Optional

from index.utils.neo4j_connector import Neo4jConnector


class RelationshipExtractor:
    """Extracts relationships between code elements."""

    @staticmethod
    async def extract_relationships(filepath, code_file, neo4j: Optional[Neo4jConnector]):
        """Extract relationships between code symbols"""
        if not neo4j or not hasattr(code_file, 'symbols') or not code_file.symbols:
            return

        # Map symbols by name for quick lookup
        symbol_map = {}
        for symbol in code_file.symbols:
            if hasattr(symbol, 'name') and symbol.name:
                symbol_map[symbol.name] = symbol

        # Process for import relationships
        if hasattr(code_file, 'language') and code_file.language in ('python', 'javascript', 'typescript'):
            # Find import statements and create relationships
            import_pattern = r'import\s+(\w+)(?:\s*,\s*\{([^}]+)\})?\s+from\s+[\'"]([^\'"]+)[\'"]'
            for i, line in enumerate(code_file.content.split('\n')):
                for match in re.finditer(import_pattern, line):
                    module_name = match.group(3)
                    imported_name = match.group(1)
                    if imported_name in symbol_map:
                        await neo4j.add_relationship(
                            from_type='File',
                            from_name='',
                            from_filepath=filepath,
                            from_line=0,
                            to_type='Module',
                            to_name=module_name,
                            to_filepath=module_name,
                            to_line=0,
                            rel_type='IMPORTS'
                        )

        # Process function calls
        if hasattr(code_file, 'language') and code_file.language in ('python', 'javascript', 'typescript'):
            function_call_pattern = r'(\w+)\s*\('
            for symbol in code_file.symbols:
                if not hasattr(symbol, 'line_number') or not symbol.name:
                    continue

                # Find function calls within this symbol
                if hasattr(symbol, 'body') and symbol.body:
                    for match in re.finditer(function_call_pattern, symbol.body):
                        called_func = match.group(1)
                        if called_func in symbol_map and called_func != symbol.name:
                            called_symbol = symbol_map[called_func]
                            await neo4j.add_relationship(
                                from_type=symbol.type.capitalize(),
                                from_name=symbol.name,
                                from_filepath=filepath,
                                from_line=symbol.line_number,
                                to_type=called_symbol.type.capitalize(),
                                to_name=called_symbol.name,
                                to_filepath=filepath,
                                to_line=called_symbol.line_number,
                                rel_type='CALLS'
                            )
