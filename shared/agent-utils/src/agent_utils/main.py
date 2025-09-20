import ast
import json
import os
import re
from enum import Enum
from typing import NamedTuple, Optional, List, Any, Dict

import dagger
from dagger import dag, field, function, object_type
from pydantic import BaseModel

class SymbolType(Enum):
    VARIABLE = "variable"
    FUNCTION = "function"
    CLASS = "class"
    INTERFACE = "interface"
    ENUM = "enum"
    STRUCT = "struct"
    TRAIT = "trait"
    CONSTANT = "constant"
    METHOD = "method"
    PROPERTY = "property"
    MODULE = "module"
    TYPE = "type"
    IMPORT = "import"


class CodeSymbol(BaseModel):
    name: str
    type: str
    line_number: int
    column: int
    end_line_number: Optional[int] = None
    end_column: Optional[int] = None
    scope: Optional[str] = None
    signature: Optional[str] = None
    visibility: Optional[str] = None
    parameters: Optional[List[Dict[str, str]]] = None
    return_type: Optional[str] = None
    docstring: Optional[str] = None


class CodeFile(BaseModel):
    content: str
    filepath: str
    language: str
    symbols: List[CodeSymbol] = []
    imports: List[str] = []


def detect_language(filepath: str) -> str:
    """Detect the programming language from the file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.hpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.cs': 'csharp',
        '.xml': 'xml',
        '.json': 'json',
    }
    return language_map.get(ext, 'unknown')


# TODO: Fix Python parsing with Tree-sitter
@object_type
class AgentUtils:
    """Enhanced utility class using Tree-sitter for accurate code parsing"""

    @function
    async def parse_code_file_to_json(self, content: str, filepath: str) -> dagger.File:
        """Parse a code file using Tree-sitter and return JSON with extracted symbols."""
        if not isinstance(content, str):
            raise TypeError(
                f"Expected content to be str, got {type(content).__name__}")

        language = detect_language(filepath)

        # Use Tree-sitter for supported languages, fallback for others
        if language in ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c', 'cpp']:
            return await self._parse_with_tree_sitter(content, filepath, language)
        # else:
        #     # Fallback to regex-based parsing for unsupported languages
        #     return await self._parse_with_fallback(content, filepath, language)

    @function
    async def _parse_with_tree_sitter(self, content: str, filepath: str, language: str) -> dagger.File:
        """Parse code using Tree-sitter with language-specific query patterns."""

        # Get file extension for tree-sitter
        ext = self._get_file_extension(language)
        filename = f"/tmp/code{ext}"

        # Create parsing script based on language
        parser_script = self._generate_parser_script(language)

        return (
            dag.container()
            .from_("python:3.11-alpine")
            # Install system dependencies for compilation
            .with_exec(["apk", "add", "--no-cache",
                       "build-base",
                        "git",
                        "gcc",
                        "musl-dev",
                        "libffi-dev",
                        "nodejs",
                        "npm"])
            # Upgrade pip and install wheel for better package support
            .with_exec(["pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
            # Install tree-sitter with specific versions that work well
            .with_exec(["pip", "install",
                       "tree-sitter==0.20.4",
                        "setuptools-rust",
                        "tree-sitter-languages==1.8.0"])
            # Write the code file
            .with_new_file(filename, content)
            # Write the parser script
            .with_new_file("/tmp/parser.py", parser_script)
            # Run the parser
            .with_exec(["python", "/tmp/parser.py", filename, filepath, language])
            .file("/tmp/result.json")
        )

    def _get_file_extension(self, language: str) -> str:
        """Get appropriate file extension for the language."""
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'go': '.go',
            'rust': '.rs',
            'c': '.c',
            'cpp': '.cpp'
        }
        return extensions.get(language, '.txt')

    def _generate_parser_script(self, language: str) -> str:
        """Generate a Python script that uses Tree-sitter to parse the code."""
        return '''
import sys
import json
import tree_sitter_languages
from tree_sitter import Language, Parser, Node

def get_node_text(node, source_code):
    """Get the text content of a node."""
    return source_code[node.start_byte:node.end_byte].decode('utf-8')

def extract_symbols_and_imports(source_code, language_name):
    """Extract symbols and imports using Tree-sitter."""
    
    # Get the language and create parser
    try:
        language = tree_sitter_languages.get_language(language_name)
        parser = Parser()
        parser.set_language(language)
    except Exception as e:
        print(f"Error setting up parser for {language_name}: {e}")
        return {"symbols": [], "imports": []}
    
    # Parse the code
    tree = parser.parse(source_code)
    root_node = tree.root_node
    
    symbols = []
    imports = []
    
    def traverse_node(node, scope=""):
        """Recursively traverse the AST and extract symbols."""
        
        # Language-specific symbol extraction
        if language_name == "python":
            symbols.extend(extract_python_symbols(node, source_code, scope))
            imports.extend(extract_python_imports(node, source_code))
        elif language_name in ["javascript", "typescript"]:
            symbols.extend(extract_js_symbols(node, source_code, scope))
            imports.extend(extract_js_imports(node, source_code))
        elif language_name == "java":
            symbols.extend(extract_java_symbols(node, source_code, scope))
            imports.extend(extract_java_imports(node, source_code))
        elif language_name == "go":
            symbols.extend(extract_go_symbols(node, source_code, scope))
            imports.extend(extract_go_imports(node, source_code))
        elif language_name == "rust":
            symbols.extend(extract_rust_symbols(node, source_code, scope))
            imports.extend(extract_rust_imports(node, source_code))
        elif language_name in ["c", "cpp"]:
            symbols.extend(extract_c_symbols(node, source_code, scope))
            imports.extend(extract_c_imports(node, source_code))
        
        # Recursively process children
        for child in node.children:
            new_scope = scope
            if node.type in ["class_definition", "class_declaration", "struct_specifier"]:
                # Update scope for nested definitions
                name_node = next((c for c in node.children if c.type in ["identifier", "type_identifier"]), None)
                if name_node:
                    class_name = get_node_text(name_node, source_code)
                    new_scope = f"{scope}.{class_name}" if scope else class_name
            
            traverse_node(child, new_scope)
    
    # Start traversal
    traverse_node(root_node)
    
    return {"symbols": symbols, "imports": list(set(imports))}

def extract_python_symbols(node, source_code, scope):
    """Extract Python-specific symbols."""
    symbols = []
    
    if node.type == "function_definition":
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            
            # Get parameters
            parameters = []
            params_node = next((c for c in node.children if c.type == "parameters"), None)
            if params_node:
                for param in params_node.children:
                    if param.type == "identifier":
                        parameters.append({"name": get_node_text(param, source_code), "type": "any"})
            
            # Get docstring
            docstring = None
            if len(node.children) > 0:
                body = next((c for c in node.children if c.type == "block"), None)
                if body and len(body.children) > 0:
                    first_stmt = body.children[0]
                    if first_stmt.type == "expression_statement":
                        expr = first_stmt.children[0]
                        if expr.type == "string":
                            docstring = get_node_text(expr, source_code).strip('"').strip("'")
            
            symbols.append({
                "name": name,
                "type": "method" if scope else "function",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "end_line_number": node.end_point[0] + 1,
                "end_column": node.end_point[1],
                "scope": scope,
                "parameters": parameters,
                "docstring": docstring,
                "signature": get_node_text(node.children[0] if node.children else node, source_code)
            })
    
    elif node.type == "class_definition":
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "class",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "end_line_number": node.end_point[0] + 1,
                "end_column": node.end_point[1],
                "scope": scope
            })
    
    elif node.type == "assignment":
        # Handle variable assignments
        target = node.children[0] if node.children else None
        if target and target.type == "identifier":
            name = get_node_text(target, source_code)
            is_constant = name.isupper()
            symbols.append({
                "name": name,
                "type": "constant" if is_constant else "variable",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    return symbols

def extract_python_imports(node, source_code):
    """Extract Python import statements."""
    imports = []
    
    if node.type == "import_statement":
        # import module
        for child in node.children:
            if child.type == "dotted_name" or child.type == "identifier":
                imports.append(get_node_text(child, source_code))
    
    elif node.type == "import_from_statement": 
        # from module import ...
        module_node = next((c for c in node.children if c.type == "dotted_name"), None)
        if module_node:
            imports.append(get_node_text(module_node, source_code))
    
    return imports

def extract_js_symbols(node, source_code, scope):
    """Extract JavaScript/TypeScript symbols."""
    symbols = []
    
    if node.type in ["function_declaration", "function_definition"]:
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            
            # Get parameters
            parameters = []
            params_node = next((c for c in node.children if c.type == "formal_parameters"), None)
            if params_node:
                for param in params_node.children:
                    if param.type == "identifier":
                        parameters.append({"name": get_node_text(param, source_code), "type": "any"})
            
            symbols.append({
                "name": name,
                "type": "function",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "end_line_number": node.end_point[0] + 1,
                "end_column": node.end_point[1],
                "scope": scope,
                "parameters": parameters
            })
    
    elif node.type == "class_declaration":
        name_node = next((c for c in node.children if c.type == "type_identifier" or c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "class",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "end_line_number": node.end_point[0] + 1,
                "end_column": node.end_point[1],
                "scope": scope
            })
    
    elif node.type == "interface_declaration":
        name_node = next((c for c in node.children if c.type == "type_identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "interface",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "end_line_number": node.end_point[0] + 1,
                "end_column": node.end_point[1],
                "scope": scope
            })
    
    elif node.type == "variable_declarator":
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            # Check if it's an arrow function assignment
            init_node = next((c for c in node.children if c.type == "arrow_function"), None)
            symbol_type = "function" if init_node else "variable"
            
            symbols.append({
                "name": name,
                "type": symbol_type,
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    return symbols

def extract_js_imports(node, source_code):
    """Extract JavaScript/TypeScript imports."""
    imports = []
    
    if node.type == "import_statement":
        source_node = next((c for c in node.children if c.type == "string"), None)
        if source_node:
            import_path = get_node_text(source_node, source_code).strip('"').strip("'")
            imports.append(import_path)
    
    return imports

def extract_java_symbols(node, source_code, scope):
    """Extract Java symbols."""
    symbols = []
    
    if node.type == "method_declaration":
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "method",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    elif node.type == "class_declaration":
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "class",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    elif node.type == "interface_declaration":
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "interface",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    return symbols

def extract_java_imports(node, source_code):
    """Extract Java imports."""
    imports = []
    
    if node.type == "import_declaration":
        # Find the scoped_identifier or identifier
        import_node = next((c for c in node.children if c.type in ["scoped_identifier", "identifier"]), None)
        if import_node:
            imports.append(get_node_text(import_node, source_code))
    
    return imports

def extract_go_symbols(node, source_code, scope):
    """Extract Go symbols."""
    symbols = []
    
    if node.type == "function_declaration":
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "function",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    elif node.type == "type_declaration":
        # Look for struct, interface, etc.
        for child in node.children:
            if child.type == "type_spec":
                name_node = next((c for c in child.children if c.type == "type_identifier"), None)
                if name_node:
                    name = get_node_text(name_node, source_code)
                    # Determine if it's a struct, interface, etc.
                    type_node = child.children[-1] if child.children else None
                    symbol_type = "struct" if type_node and type_node.type == "struct_type" else "type"
                    
                    symbols.append({
                        "name": name,
                        "type": symbol_type,
                        "line_number": child.start_point[0] + 1,
                        "column": child.start_point[1],
                        "scope": scope
                    })
    
    return symbols

def extract_go_imports(node, source_code):
    """Extract Go imports."""
    imports = []
    
    if node.type == "import_declaration":
        for child in node.children:
            if child.type == "import_spec":
                path_node = next((c for c in child.children if c.type == "interpreted_string_literal"), None)
                if path_node:
                    import_path = get_node_text(path_node, source_code).strip('"')
                    imports.append(import_path)
    
    return imports

def extract_rust_symbols(node, source_code, scope):
    """Extract Rust symbols."""
    symbols = []
    
    if node.type == "function_item":
        name_node = next((c for c in node.children if c.type == "identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "function",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    elif node.type == "struct_item":
        name_node = next((c for c in node.children if c.type == "type_identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "struct",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    elif node.type == "trait_item":
        name_node = next((c for c in node.children if c.type == "type_identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbols.append({
                "name": name,
                "type": "trait",
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    return symbols

def extract_rust_imports(node, source_code):
    """Extract Rust imports."""
    imports = []
    
    if node.type == "use_declaration":
        # Extract the use path
        use_node = next((c for c in node.children if c.type == "use_list" or c.type == "scoped_identifier"), None)
        if use_node:
            imports.append(get_node_text(use_node, source_code))
    
    return imports

def extract_c_symbols(node, source_code, scope):
    """Extract C/C++ symbols."""
    symbols = []
    
    if node.type == "function_definition":
        # Find function name
        declarator = next((c for c in node.children if c.type == "function_declarator"), None)
        if declarator:
            name_node = next((c for c in declarator.children if c.type == "identifier"), None)
            if name_node:
                name = get_node_text(name_node, source_code)
                symbols.append({
                    "name": name,
                    "type": "function",
                    "line_number": node.start_point[0] + 1,
                    "column": node.start_point[1],
                    "scope": scope
                })
    
    elif node.type in ["struct_specifier", "class_specifier"]:
        name_node = next((c for c in node.children if c.type == "type_identifier"), None)
        if name_node:
            name = get_node_text(name_node, source_code)
            symbol_type = "class" if node.type == "class_specifier" else "struct"
            symbols.append({
                "name": name,
                "type": symbol_type,
                "line_number": node.start_point[0] + 1,
                "column": node.start_point[1],
                "scope": scope
            })
    
    return symbols

def extract_c_imports(node, source_code):
    """Extract C/C++ includes."""
    imports = []
    
    if node.type == "preproc_include":
        # Extract the include path
        path_node = next((c for c in node.children if c.type in ["string_literal", "system_lib_string"]), None)
        if path_node:
            import_path = get_node_text(path_node, source_code).strip('<>').strip('"')
            imports.append(import_path)
    
    return imports

def main():
    if len(sys.argv) != 4:
        print("Usage: python parser.py <code_file> <filepath> <language>")
        sys.exit(1)
    
    code_file = sys.argv[1]
    filepath = sys.argv[2]
    language = sys.argv[3]
    
    # Read the source code
    with open(code_file, 'rb') as f:
        source_code = f.read()
    
    # Extract symbols and imports
    result = extract_symbols_and_imports(source_code, language)
    
    # Create the final result
    code_file_dict = {
        "content": source_code.decode('utf-8'),
        "filepath": filepath,
        "language": language,
        "symbols": result["symbols"],
        "imports": result["imports"]
    }
    
    # Write result to JSON file
    with open('/tmp/result.json', 'w') as f:
        json.dump(code_file_dict, f, indent=2)

if __name__ == "__main__":
    main()
'''
