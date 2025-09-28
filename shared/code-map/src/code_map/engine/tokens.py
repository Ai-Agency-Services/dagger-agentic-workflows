"""Token parsing engine using Tree-sitter."""

import re
from typing import Optional, Dict, List

try:
    import tree_sitter_languages as tsl
    from tree_sitter import Parser, Node, Query
except ImportError:
    tsl = None
    Parser = None
    Node = object
    Query = object

import os
from pathlib import Path
from .detect import detect_language, EXTENSION_MAP


def parse_tokens_from_text(
    text: str,
    path: str,
    language_hint: Optional[str] = None,
    overrides: Optional[Dict[str, str]] = None,
    unknown_policy: str = "skip",
    default_language: Optional[str] = None,
) -> dict:
    """Parse tokens from text using Tree-sitter.

    Returns:
        {
            "identifiers": [{"name": str, "kind": str, "start": {"line": int, "col": int}, "end": {"line": int, "col": int}}],
            "calls": [{"callee": str, "location": {"line": int, "col": int}, "file": str}],
            "language": str
        }
    """
    # Detect language
    text_head = text[:8192]  # First 8KB for detection
    detected_lang = language_hint or detect_language(
        path, text_head, overrides)

    if not detected_lang:
        if unknown_policy == "best-effort" and default_language:
            detected_lang = default_language
        else:
            return {
                "identifiers": [],
                "calls": [],
                "language": "unknown"
            }

    # Parse with Tree-sitter if available
    if tsl is None or Parser is None:
        return _parse_fallback(text, path, detected_lang)

    try:
        # Map language to tree-sitter language
        ts_lang_map = {
            "python": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "java": "java",
            "go": "go",
            "rust": "rust",
            "c": "c",
            "cpp": "cpp",
            "c_sharp": "c_sharp",
            "ruby": "ruby",
            "php": "php",
        }
        
        ts_lang = ts_lang_map.get(detected_lang)
        if not ts_lang:
            return _parse_fallback(text, path, detected_lang)
        
        parser = Parser()
        language = tsl.get_language(ts_lang)
        parser.set_language(language)
        tree = parser.parse(text.encode())
        
        # Load custom query for semantic analysis
        query_text = _load_custom_query(detected_lang)
        if query_text:
            query = language.query(query_text)
            identifiers, calls = _extract_with_custom_query(query, tree.root_node, text, path)
        else:
            identifiers = _extract_identifiers(tree.root_node, text, detected_lang)
            calls = _extract_calls(tree.root_node, text, path, detected_lang)
        
        return {
            "identifiers": identifiers,
            "calls": calls,
            "language": detected_lang
        }

    except Exception:
        return _parse_fallback(text, path, detected_lang)


def _extract_identifiers(node: Node, text: str, language: str) -> List[Dict]:
    """Extract identifier definitions from AST."""
    identifiers = []

    def visit(n: Node):
        # Python
        if language == "python":
            if n.type == "function_definition":
                name_node = n.child_by_field_name("name")
                if name_node:
                    identifiers.append({
                        "name": name_node.text.decode(),
                        "kind": "function",
                        "start": {"line": n.start_point[0] + 1, "col": n.start_point[1]},
                        "end": {"line": n.end_point[0] + 1, "col": n.end_point[1]}
                    })
            elif n.type == "class_definition":
                name_node = n.child_by_field_name("name")
                if name_node:
                    identifiers.append({
                        "name": name_node.text.decode(),
                        "kind": "class",
                        "start": {"line": n.start_point[0] + 1, "col": n.start_point[1]},
                        "end": {"line": n.end_point[0] + 1, "col": n.end_point[1]}
                    })

        # JavaScript/TypeScript
        elif language in ["javascript", "typescript"]:
            if n.type in ["function_declaration", "function_expression", "arrow_function"]:
                name_node = n.child_by_field_name("name")
                if name_node:
                    identifiers.append({
                        "name": name_node.text.decode(),
                        "kind": "function",
                        "start": {"line": n.start_point[0] + 1, "col": n.start_point[1]},
                        "end": {"line": n.end_point[0] + 1, "col": n.end_point[1]}
                    })
            elif n.type == "class_declaration":
                name_node = n.child_by_field_name("name")
                if name_node:
                    identifiers.append({
                        "name": name_node.text.decode(),
                        "kind": "class",
                        "start": {"line": n.start_point[0] + 1, "col": n.start_point[1]},
                        "end": {"line": n.end_point[0] + 1, "col": n.end_point[1]}
                    })

        # Recurse
        for child in getattr(n, 'children', []) or []:
            visit(child)

    visit(node)
    return identifiers


def _extract_calls(node: Node, text: str, file_path: str, language: str) -> List[Dict]:
    """Extract function/method calls from AST."""
    calls = []

    def visit(n: Node):
        if language == "python":
            if n.type == "call":
                func_node = n.child_by_field_name("function")
                if func_node:
                    try:
                        callee = func_node.text.decode()
                        calls.append({
                            "callee": callee,
                            "location": {"line": n.start_point[0] + 1, "col": n.start_point[1]},
                            "file": file_path
                        })
                    except Exception:
                        pass

        elif language in ["javascript", "typescript"]:
            if n.type == "call_expression":
                func_node = n.child_by_field_name("function")
                if func_node:
                    try:
                        callee = func_node.text.decode()
                        calls.append({
                            "callee": callee,
                            "location": {"line": n.start_point[0] + 1, "col": n.start_point[1]},
                            "file": file_path
                        })
                    except Exception:
                        pass

        # Recurse
        for child in getattr(n, 'children', []) or []:
            visit(child)

    visit(node)
    return calls


def _load_custom_query(language: str) -> str:
    """Load custom tree-sitter query for semantic analysis."""
    try:
        # Map language to query file
        query_map = {
            "python": "tree-sitter-python-tags.scm",
            "javascript": "tree-sitter-javascript-tags.scm", 
            "typescript": "tree-sitter-typescript-tags.scm",
            "java": "tree-sitter-java-tags.scm",
            "go": "tree-sitter-go-tags.scm",
            "rust": "tree-sitter-rust-tags.scm",
            "c": "tree-sitter-c-tags.scm",
            "cpp": "tree-sitter-cpp-tags.scm",
            "c_sharp": "tree-sitter-c_sharp-tags.scm",
            "ruby": "tree-sitter-ruby-tags.scm",
            "php": "tree-sitter-php-tags.scm",
        }
        
        query_file = query_map.get(language)
        if not query_file:
            return ""
        
        # Load query from queries directory
        current_dir = Path(__file__).parent.parent
        query_path = current_dir / "queries" / query_file
        
        if query_path.exists():
            return query_path.read_text(encoding="utf-8")
        return ""
    except Exception:
        return ""


def _extract_with_custom_query(query: Query, root_node: Node, text: str, file_path: str) -> tuple:
    """Extract identifiers and calls using custom semantic queries."""
    identifiers = []
    calls = []
    
    try:
        captures = query.captures(root_node)
        
        for node, capture_name in captures:
            try:
                name = node.text.decode('utf-8')
                start_point = node.start_point
                end_point = node.end_point
                
                if capture_name == "identifier":
                    # Determine kind from parent node type
                    parent = node.parent
                    kind = "variable"  # default
                    if parent:
                        if "function" in parent.type:
                            kind = "function"
                        elif "class" in parent.type:
                            kind = "class"
                        elif "method" in parent.type:
                            kind = "method"
                        elif "interface" in parent.type:
                            kind = "interface"
                    
                    identifiers.append({
                        "name": name,
                        "kind": kind,
                        "start": {"line": start_point[0] + 1, "col": start_point[1]},
                        "end": {"line": end_point[0] + 1, "col": end_point[1]}
                    })
                
                elif capture_name == "call.identifier":
                    calls.append({
                        "callee": name,
                        "location": {"line": start_point[0] + 1, "col": start_point[1]},
                        "file": file_path
                    })
                    
            except Exception:
                continue
                
    except Exception:
        # Fallback to basic extraction if query fails
        pass
    
    return identifiers, calls


def _parse_fallback(text: str, path: str, language: str) -> dict:
    """Fallback parsing using regex when Tree-sitter is unavailable."""
    identifiers = []
    calls = []

    lines = text.split("\n")

    if language == "python":
        for i, line in enumerate(lines):
            # Function definitions
            func_match = re.match(r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if func_match:
                identifiers.append({
                    "name": func_match.group(1),
                    "kind": "function",
                    "start": {"line": i + 1, "col": 0},
                    "end": {"line": i + 1, "col": len(line)}
                })

            # Class definitions
            class_match = re.match(
                r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if class_match:
                identifiers.append({
                    "name": class_match.group(1),
                    "kind": "class",
                    "start": {"line": i + 1, "col": 0},
                    "end": {"line": i + 1, "col": len(line)}
                })

            # Function calls
            call_matches = re.finditer(r"([a-zA-Z_][a-zA-Z0-9_.]*)\s*\(", line)
            for match in call_matches:
                calls.append({
                    "callee": match.group(1),
                    "location": {"line": i + 1, "col": match.start()},
                    "file": path
                })

    elif language in ["javascript", "typescript"]:
        for i, line in enumerate(lines):
            # Function declarations
            func_match = re.match(
                r"^\s*(?:function|const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if func_match:
                identifiers.append({
                    "name": func_match.group(1),
                    "kind": "function",
                    "start": {"line": i + 1, "col": 0},
                    "end": {"line": i + 1, "col": len(line)}
                })

            # Class declarations
            class_match = re.match(
                r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
            if class_match:
                identifiers.append({
                    "name": class_match.group(1),
                    "kind": "class",
                    "start": {"line": i + 1, "col": 0},
                    "end": {"line": i + 1, "col": len(line)}
                })

            # Function calls
            call_matches = re.finditer(r"([a-zA-Z_][a-zA-Z0-9_.]*)\s*\(", line)
            for match in call_matches:
                calls.append({
                    "callee": match.group(1),
                    "location": {"line": i + 1, "col": match.start()},
                    "file": path
                })

    return {
        "identifiers": identifiers,
        "calls": calls,
        "language": language
    }
