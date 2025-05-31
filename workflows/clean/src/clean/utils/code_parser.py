from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import ast
import os
import re
from enum import Enum


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


@dataclass
class CodeSymbol:
    """Represents a symbol (variable, function, class) in code."""
    name: str
    type: str  # Use values from SymbolType enum
    line_number: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    scope: Optional[str] = None
    signature: Optional[str] = None  # For functions/methods
    visibility: Optional[str] = None  # public, private, protected, etc.


@dataclass
class CodeFile:
    """Represents a parsed code file with its symbols."""
    content: str
    filepath: str
    language: str
    symbols: List[CodeSymbol] = field(default_factory=list)
    lines: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.lines = self.content.splitlines()

    def get_context_around_line(self, line_number: int, context_lines: int = 3) -> str:
        """Get a few lines of context around the specified line."""
        start = max(0, line_number - context_lines - 1)
        end = min(len(self.lines), line_number + context_lines)
        context = "\n".join([
            f"{i+1}: {line}" for i, line in enumerate(self.lines[start:end], start)
        ])
        return context


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
        '.cs': 'csharp'
    }
    return language_map.get(ext, 'unknown')


def parse_python_code(content: str) -> List[CodeSymbol]:
    """Parse Python code to extract symbols using AST."""
    symbols = []

    try:
        tree = ast.parse(content)

        # Track scopes for nested definitions
        current_scope = ""

        # Process all nodes in the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Check if it's a method in a class
                symbol_type = "method" if current_scope else "function"

                # Get function arguments
                args_list = []
                for arg in node.args.args:
                    args_list.append(arg.arg)

                # Get default values for arguments
                defaults = [None] * (len(node.args.args) -
                                     len(node.args.defaults)) + node.args.defaults

                # Create argument signatures with defaults when available
                arg_signatures = []
                for i, arg in enumerate(node.args.args):
                    if defaults[i] is None:
                        arg_signatures.append(arg.arg)
                    else:
                        if isinstance(defaults[i], ast.Constant):
                            default_val = defaults[i].value
                            arg_signatures.append(f"{arg.arg}={default_val}")
                        else:
                            arg_signatures.append(f"{arg.arg}=...")

                signature = f"def {node.name}({', '.join(arg_signatures)})"

                full_name = f"{current_scope}.{node.name}" if current_scope else node.name

                symbols.append(CodeSymbol(
                    name=node.name,
                    type=symbol_type,
                    line_number=node.lineno,
                    column=node.col_offset,
                    end_line=node.end_lineno,
                    end_column=node.end_col_offset,
                    scope=current_scope,
                    signature=signature
                ))

            elif isinstance(node, ast.ClassDef):
                old_scope = current_scope
                current_scope = node.name if not current_scope else f"{current_scope}.{node.name}"

                symbols.append(CodeSymbol(
                    name=node.name,
                    type="class",
                    line_number=node.lineno,
                    column=node.col_offset,
                    end_line=node.end_lineno,
                    end_column=node.end_col_offset,
                    scope=old_scope
                ))

                # Reset scope after processing this class's children
                current_scope = old_scope

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Check if this is likely a constant (ALL_CAPS)
                        is_constant = target.id.isupper()

                        symbols.append(CodeSymbol(
                            name=target.id,
                            type="constant" if is_constant else "variable",
                            line_number=target.lineno,
                            column=target.col_offset,
                            scope=current_scope
                        ))
    except SyntaxError as e:
        print(f"Syntax error parsing Python code: {e}")

    return symbols


def parse_javascript_code(content: str) -> List[CodeSymbol]:
    """Parse JavaScript/TypeScript code using regex patterns."""
    symbols = []

    # Regex patterns for JavaScript/TypeScript
    function_patterns = [
        # Regular function declaration
        r'function\s+(\w+)\s*\([^)]*\)',
        # Arrow function with explicit name
        r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]*)\s*=>\s*[{]?',
        # Class method
        r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*[{]',
        # Constructor
        r'constructor\s*\([^)]*\)'
    ]

    class_pattern = r'class\s+(\w+)'
    variable_patterns = [
        # var, let, const declarations
        r'(?:var|let|const)\s+(\w+)(?:\s*=|,|\s*$)',
        # TypeScript interfaces
        r'interface\s+(\w+)',
        # TypeScript types
        r'type\s+(\w+)',
        # TypeScript enum
        r'enum\s+(\w+)'
    ]

    # Process file line by line
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Check for functions
        for pattern in function_patterns:
            for match in re.finditer(pattern, line):
                if pattern == r'constructor\s*\([^)]*\)':
                    name = "constructor"
                else:
                    name = match.group(1)

                symbols.append(CodeSymbol(
                    name=name,
                    type="function",
                    line_number=i+1,
                    column=match.start(),
                    signature=match.group(0)
                ))

        # Check for classes
        for match in re.finditer(class_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="class",
                line_number=i+1,
                column=match.start()
            ))

        # Check for variables and other declarations
        for pattern in variable_patterns:
            for match in re.finditer(pattern, line):
                if "interface" in pattern:
                    symbol_type = "interface"
                elif "type" in pattern:
                    symbol_type = "type"
                elif "enum" in pattern:
                    symbol_type = "enum"
                else:
                    symbol_type = "constant" if match.group(
                        1).isupper() else "variable"

                symbols.append(CodeSymbol(
                    name=match.group(1),
                    type=symbol_type,
                    line_number=i+1,
                    column=match.start()
                ))

    return symbols


def parse_java_code(content: str) -> List[CodeSymbol]:
    """Parse Java code using regex patterns."""
    symbols = []

    # Regex patterns for Java
    class_pattern = r'(?:public|private|protected)?\s+(?:abstract|final)?\s+class\s+(\w+)'
    interface_pattern = r'(?:public|private|protected)?\s+interface\s+(\w+)'
    enum_pattern = r'(?:public|private|protected)?\s+enum\s+(\w+)'

    method_pattern = r'(?:public|private|protected)?\s+(?:static|final|abstract)?\s+(?:\w+(?:<[^>]*>)?)\s+(\w+)\s*\([^)]*\)'
    field_pattern = r'(?:public|private|protected)?\s+(?:static|final)?\s+(?:\w+(?:<[^>]*>)?)\s+(\w+)\s*[=;]'

    # Process file line by line
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Check for classes
        for match in re.finditer(class_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="class",
                line_number=i+1,
                column=match.start()
            ))

        # Check for interfaces
        for match in re.finditer(interface_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="interface",
                line_number=i+1,
                column=match.start()
            ))

        # Check for enums
        for match in re.finditer(enum_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="enum",
                line_number=i+1,
                column=match.start()
            ))

        # Check for methods
        for match in re.finditer(method_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="method",
                line_number=i+1,
                column=match.start(),
                signature=match.group(0)
            ))

        # Check for fields
        for match in re.finditer(field_pattern, line):
            is_constant = re.search(
                r'\bfinal\b', line) and match.group(1).isupper()
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="constant" if is_constant else "variable",
                line_number=i+1,
                column=match.start()
            ))

    return symbols


def parse_c_cpp_code(content: str) -> List[CodeSymbol]:
    """Parse C/C++ code using regex patterns."""
    symbols = []

    # Regex patterns for C/C++
    function_pattern = r'(?:\w+\s+)+(\w+)\s*\([^;{]*\)\s*[{]'
    class_pattern = r'(?:class|struct)\s+(\w+)'
    variable_pattern = r'(?:int|float|double|char|bool|unsigned|long|short|void\s*\*|[a-zA-Z_]\w*(?:<[^>]*>)?)\s+(\w+)(?:\s*\[|\s*=|\s*;|\s*,)'
    enum_pattern = r'enum\s+(?:class\s+)?(\w+)'
    define_pattern = r'#define\s+(\w+)'

    # Process file line by line
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Strip comments to avoid false positives
        line = re.sub(r'//.*$', '', line)

        # Check for functions
        for match in re.finditer(function_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="function",
                line_number=i+1,
                column=match.start(),
                signature=match.group(0).strip('{')
            ))

        # Check for classes and structs
        for match in re.finditer(class_pattern, line):
            symbol_type = "class" if "class" in line[:match.start(
            )] else "struct"
            symbols.append(CodeSymbol(
                name=match.group(1),
                type=symbol_type,
                line_number=i+1,
                column=match.start()
            ))

        # Check for enums
        for match in re.finditer(enum_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="enum",
                line_number=i+1,
                column=match.start()
            ))

        # Check for #define macros
        for match in re.finditer(define_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="constant",
                line_number=i+1,
                column=match.start()
            ))

        # Check for variables
        for match in re.finditer(variable_pattern, line):
            # Skip if this is part of a function declaration
            if re.search(r'\)\s*$', line):
                continue

            is_constant = match.group(1).isupper(
            ) or "const " in line[:match.start()]
            symbols.append(CodeSymbol(
                name=match.group(2),
                type="constant" if is_constant else "variable",
                line_number=i+1,
                column=match.start()
            ))

    return symbols


def parse_go_code(content: str) -> List[CodeSymbol]:
    """Parse Go code using regex patterns."""
    symbols = []

    # Regex patterns for Go
    function_pattern = r'func\s+(\w+)'
    method_pattern = r'func\s+\([^)]*\)\s+(\w+)'
    struct_pattern = r'type\s+(\w+)\s+struct'
    interface_pattern = r'type\s+(\w+)\s+interface'
    const_pattern = r'const\s+(\w+)'
    var_pattern = r'var\s+(\w+)'

    # Process file line by line
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Check for functions
        for match in re.finditer(function_pattern, line):
            # Skip methods (handled separately)
            if re.search(r'func\s+\(', line[:match.start()]):
                continue

            symbols.append(CodeSymbol(
                name=match.group(1),
                type="function",
                line_number=i+1,
                column=match.start(),
                signature=line.strip()
            ))

        # Check for methods
        for match in re.finditer(method_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="method",
                line_number=i+1,
                column=match.start(),
                signature=line.strip()
            ))

        # Check for structs
        for match in re.finditer(struct_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="struct",
                line_number=i+1,
                column=match.start()
            ))

        # Check for interfaces
        for match in re.finditer(interface_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="interface",
                line_number=i+1,
                column=match.start()
            ))

        # Check for constants
        for match in re.finditer(const_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="constant",
                line_number=i+1,
                column=match.start()
            ))

        # Check for variables
        for match in re.finditer(var_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="variable",
                line_number=i+1,
                column=match.start()
            ))

    return symbols


def parse_rust_code(content: str) -> List[CodeSymbol]:
    """Parse Rust code using regex patterns."""
    symbols = []

    # Regex patterns for Rust
    function_pattern = r'fn\s+(\w+)'
    struct_pattern = r'struct\s+(\w+)'
    trait_pattern = r'trait\s+(\w+)'
    enum_pattern = r'enum\s+(\w+)'
    impl_pattern = r'impl\s+(?:<[^>]*>\s+)?(?:\w+\s+for\s+)?(\w+)'
    const_pattern = r'const\s+(\w+)'
    let_pattern = r'let\s+(?:mut\s+)?(\w+)'

    # Process file line by line
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Strip comments
        line = re.sub(r'//.*$', '', line)

        # Check for functions
        for match in re.finditer(function_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="function",
                line_number=i+1,
                column=match.start(),
                signature=line.strip()
            ))

        # Check for structs
        for match in re.finditer(struct_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="struct",
                line_number=i+1,
                column=match.start()
            ))

        # Check for traits
        for match in re.finditer(trait_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="trait",
                line_number=i+1,
                column=match.start()
            ))

        # Check for enums
        for match in re.finditer(enum_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="enum",
                line_number=i+1,
                column=match.start()
            ))

        # Check for impl blocks (implementation)
        for match in re.finditer(impl_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="implementation",
                line_number=i+1,
                column=match.start()
            ))

        # Check for constants
        for match in re.finditer(const_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="constant",
                line_number=i+1,
                column=match.start()
            ))

        # Check for variables (let statements)
        for match in re.finditer(let_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="variable",
                line_number=i+1,
                column=match.start()
            ))

    return symbols


def parse_ruby_code(content: str) -> List[CodeSymbol]:
    """Parse Ruby code using regex patterns."""
    symbols = []

    # Regex patterns for Ruby
    class_pattern = r'class\s+(\w+)'
    module_pattern = r'module\s+(\w+)'
    method_pattern = r'def\s+(\w+[!?]?)'
    constant_pattern = r'([A-Z][A-Z0-9_]*)\s*='
    attr_pattern = r'(?:attr_reader|attr_writer|attr_accessor)\s+:(\w+)'
    var_pattern = r'(?:@{1,2}|\$)(\w+)'  # Instance, class and global variables

    # Process file line by line
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Strip comments
        line = re.sub(r'#.*$', '', line)

        # Check for classes
        for match in re.finditer(class_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="class",
                line_number=i+1,
                column=match.start()
            ))

        # Check for modules
        for match in re.finditer(module_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="module",
                line_number=i+1,
                column=match.start()
            ))

        # Check for methods
        for match in re.finditer(method_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="method",
                line_number=i+1,
                column=match.start()
            ))

        # Check for constants
        for match in re.finditer(constant_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="constant",
                line_number=i+1,
                column=match.start()
            ))

        # Check for attributes
        for match in re.finditer(attr_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="property",
                line_number=i+1,
                column=match.start()
            ))

        # Check for instance/class/global variables
        for match in re.finditer(var_pattern, line):
            var_type = "variable"
            if match.group(0).startswith("@@"):
                var_type = "class_variable"
            elif match.group(0).startswith("@"):
                var_type = "instance_variable"
            elif match.group(0).startswith("$"):
                var_type = "global_variable"

            symbols.append(CodeSymbol(
                name=match.group(1),
                type=var_type,
                line_number=i+1,
                column=match.start()
            ))

    return symbols


def parse_php_code(content: str) -> List[CodeSymbol]:
    """Parse PHP code using regex patterns."""
    symbols = []

    # Regex patterns for PHP
    class_pattern = r'class\s+(\w+)'
    interface_pattern = r'interface\s+(\w+)'
    trait_pattern = r'trait\s+(\w+)'
    function_pattern = r'function\s+(\w+)'
    method_pattern = r'(?:public|private|protected)(?:\s+static)?\s+function\s+(\w+)'
    property_pattern = r'(?:public|private|protected)(?:\s+static)?\s+\$(\w+)'
    const_pattern = r'const\s+(\w+)'
    var_pattern = r'\$(\w+)\s*='

    # Process file line by line
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # Strip comments
        line = re.sub(r'(?://.*$|/\*.*?\*/)', '', line)

        # Check for classes
        for match in re.finditer(class_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="class",
                line_number=i+1,
                column=match.start()
            ))

        # Check for interfaces
        for match in re.finditer(interface_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="interface",
                line_number=i+1,
                column=match.start()
            ))

        # Check for traits
        for match in re.finditer(trait_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="trait",
                line_number=i+1,
                column=match.start()
            ))

        # Check for standalone functions (not methods)
        if not re.search(r'(?:public|private|protected)', line):
            for match in re.finditer(function_pattern, line):
                symbols.append(CodeSymbol(
                    name=match.group(1),
                    type="function",
                    line_number=i+1,
                    column=match.start()
                ))

        # Check for methods
        for match in re.finditer(method_pattern, line):
            visibility = "public"
            if "private" in line[:match.start()]:
                visibility = "private"
            elif "protected" in line[:match.start()]:
                visibility = "protected"

            symbols.append(CodeSymbol(
                name=match.group(1),
                type="method",
                line_number=i+1,
                column=match.start(),
                visibility=visibility
            ))

        # Check for class properties
        for match in re.finditer(property_pattern, line):
            visibility = "public"
            if "private" in line[:match.start()]:
                visibility = "private"
            elif "protected" in line[:match.start()]:
                visibility = "protected"

            symbols.append(CodeSymbol(
                name=match.group(1),
                type="property",
                line_number=i+1,
                column=match.start(),
                visibility=visibility
            ))

        # Check for constants
        for match in re.finditer(const_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="constant",
                line_number=i+1,
                column=match.start()
            ))

        # Check for regular variables
        for match in re.finditer(var_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="variable",
                line_number=i+1,
                column=match.start()
            ))

    return symbols


def parse_generic_code(content: str) -> List[CodeSymbol]:
    """Parse code generically using regex patterns for common symbols."""
    symbols = []

    # Simple regex patterns for functions, classes and variables
    function_pattern = r'(?:function|def|func|fn)\s+(\w+)'
    class_pattern = r'(?:class|struct|interface|trait|enum)\s+(\w+)'
    variable_pattern = r'(?:var|let|const|int|float|string|bool|char)\s+(\w+)'

    # Process file line by line
    for i, line in enumerate(content.splitlines()):
        # Look for functions
        for match in re.finditer(function_pattern, line):
            symbols.append(CodeSymbol(
                name=match.group(1),
                type="function",
                line_number=i+1,
                column=match.start()
            ))

        # Look for classes
        for match in re.finditer(class_pattern, line):
            # Determine type based on what appears in the line
            if "struct" in line[:match.start()]:
                symbol_type = "struct"
            elif "interface" in line[:match.start()]:
                symbol_type = "interface"
            elif "trait" in line[:match.start()]:
                symbol_type = "trait"
            elif "enum" in line[:match.start()]:
                symbol_type = "enum"
            else:
                symbol_type = "class"

            symbols.append(CodeSymbol(
                name=match.group(1),
                type=symbol_type,
                line_number=i+1,
                column=match.start()
            ))

        # Look for variables
        for match in re.finditer(variable_pattern, line):
            # Determine type based on what appears in the line
            if "const" in line[:match.start()] or match.group(1).isupper():
                symbol_type = "constant"
            else:
                symbol_type = "variable"

            symbols.append(CodeSymbol(
                name=match.group(1),
                type=symbol_type,
                line_number=i+1,
                column=match.start()
            ))

    return symbols


def parse_code_file(content: str, filepath: str) -> CodeFile:
    """Parse a code file to extract symbols based on the language."""
    language = detect_language(filepath)
    symbols = []

    # Select the appropriate parser based on language
    if language == 'python':
        symbols = parse_python_code(content)
    elif language in ['javascript', 'typescript']:
        symbols = parse_javascript_code(content)
    elif language == 'java':
        symbols = parse_java_code(content)
    elif language in ['c', 'cpp']:
        symbols = parse_c_cpp_code(content)
    elif language == 'go':
        symbols = parse_go_code(content)
    elif language == 'rust':
        symbols = parse_rust_code(content)
    elif language == 'ruby':
        symbols = parse_ruby_code(content)
    elif language == 'php':
        symbols = parse_php_code(content)
    else:
        symbols = parse_generic_code(content)

    return CodeFile(
        content=content,
        filepath=filepath,
        language=language,
        symbols=symbols
    )
