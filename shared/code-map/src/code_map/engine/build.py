# Code map building using Tree-sitter.

import json
import time
from pathlib import Path
from typing import Dict, List

try:
    import tree_sitter_languages as tsl  # optional
    from tree_sitter import Parser, Node  # type: ignore
except Exception:  # pragma: no cover
    tsl = None
    Parser = None  # type: ignore
    Node = object  # type: ignore

from ..types import BuildOptions, FileEntry, SymbolEntry, ChunkEntry, CodeMapSummary, RelationEntry

LANGUAGE_MAPPING = {
    "python": "python",
    "javascript": "javascript", 
    "typescript": "typescript",
    "java": "java",
    "go": "go",
    "rust": "rust",
}

EXTENSION_MAPPING = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript", 
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
}


def detect_language(file_path: str) -> str:
    # Detect language from file extension.
    suffix = Path(file_path).suffix.lower()
    return EXTENSION_MAPPING.get(suffix, "unknown")


def estimate_tokens(text: str) -> int:
    # Rough token estimate: char count / 3.
    return max(1, len(text) // 3)


def _load_query_text(language: str) -> str | None:
    try:
        qpath = Path(__file__).resolve().parent.parent / "queries" / f"{language}.scm"
        if qpath.exists():
            return qpath.read_text(encoding="utf-8")
    except Exception:
        return None
    return None


def _extract_symbols_with_query(lang_obj, tree, content: str, language: str, rel_path: str) -> List[SymbolEntry]:
    qtext = _load_query_text(language)
    if not qtext:
        return []
    try:
        query = lang_obj.query(qtext)
        captures = query.captures(tree.root_node)
        symbols: List[SymbolEntry] = []
        type_map = {
            "function": "function",
            "class": "class",
            "method": "method",
            "var": "variable",
        }
        for node, cap_name in captures:
            if cap_name in type_map:
                name_node = node.child_by_field_name("name") if hasattr(node, "child_by_field_name") else None
                try:
                    name = (name_node.text.decode() if name_node else node.text.decode())[:200]
                except Exception:
                    name = "<unknown>"
                symbols.append(SymbolEntry(
                    file=rel_path,
                    name=name,
                    type=type_map[cap_name],
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                ))
        return symbols
    except Exception:
        return []


def _extract_imports_with_query(lang_obj, tree, language: str, rel_path: str, content: str) -> List[RelationEntry]:
    qtext = _load_query_text(language)
    if not qtext:
        return []
    try:
        query = lang_obj.query(qtext)
        captures = query.captures(tree.root_node)
        rels: List[RelationEntry] = []
        for node, cap_name in captures:
            if cap_name in ("import", "import_from") and language == "python":
                # Best-effort: dotted_name already captured, use node.text
                try:
                    mod = node.child_by_field_name("module_name") or node.child_by_field_name("name")
                    target = (mod.text.decode() if mod else node.text.decode()).strip().strip("\"'")
                except Exception:
                    target = ""
                if target:
                    rels.append(RelationEntry(source=rel_path, target=target, relation_type="import"))
            elif cap_name == "import" and language in ("javascript", "typescript"):
                try:
                    s = node.child_by_field_name("source")
                    target = (s.text.decode() if s else node.text.decode()).strip().strip("\"'")
                except Exception:
                    target = ""
                if target:
                    rels.append(RelationEntry(source=rel_path, target=target, relation_type="import"))
        return rels
    except Exception:
        return []


def _extract_imports_fallback(language: str, rel_path: str, content: str) -> List[RelationEntry]:
    import re
    rels: List[RelationEntry] = []
    if language == "python":
        for line in content.splitlines():
            m1 = re.match(r"^\s*import\s+([a-zA-Z0-9_\.]+)", line)
            m2 = re.match(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+", line)
            mod = (m1.group(1) if m1 else (m2.group(1) if m2 else None))
            if mod:
                rels.append(RelationEntry(source=rel_path, target=mod, relation_type="import"))
    elif language in ("javascript", "typescript"):
        for line in content.splitlines():
            # import x from 'mod'; import {x} from "mod";
            m = re.search(r"import\b.*from\s+['\"]([^'\"]+)['\"]", line)
            if m:
                rels.append(RelationEntry(source=rel_path, target=m.group(1), relation_type="import"))
    return rels


def _extract_python_docstrings(root: Node, content: str, rel_path: str) -> List[SymbolEntry]:
    # Heuristic: capture leading string literals in module/class/function bodies as docstrings.
    symbols: List[SymbolEntry] = []
    try:
        # Use a simple textual heuristic to find triple-quoted strings in early lines
        import re
        doc_matches = list(re.finditer(r"^[\t ]*[\"\']{3}([\s\S]*?)[\"\']{3}", content, re.M))
        for m in doc_matches[:3]:  # cap at a few
            snippet = m.group(1).strip().splitlines()[0] if m.group(1) else ""
            name = (snippet[:80] + "…") if len(snippet) > 80 else snippet
            if name:
                # Approximate line numbers
                start_line = content[:m.start()].count("\n") + 1
                end_line = content[:m.end()].count("\n") + 1
                symbols.append(SymbolEntry(
                    file=rel_path,
                    name=name or "docstring",
                    type="docstring",
                    start_line=start_line,
                    end_line=end_line,
                ))
    except Exception:
        pass
    return symbols


def parse_file_symbols(file_path: str, content: str, language: str) -> List[SymbolEntry]:
    # Extract symbols from file using Tree-sitter (optional).
    if language not in LANGUAGE_MAPPING or tsl is None or Parser is None:
        # fallback: minimal docstring heuristic for python
        if language == "python":
            return _extract_python_docstrings(None, content, file_path)
        return []
    
    try:
        parser = Parser()
        lang = tsl.get_language(LANGUAGE_MAPPING[language])
        parser.set_language(lang)
        tree = parser.parse(content.encode())

        # First try query-based symbol extraction
        q_symbols = _extract_symbols_with_query(lang, tree, content, language, file_path)
        if language == "python":
            q_symbols.extend(_extract_python_docstrings(tree.root_node, content, file_path))
        if q_symbols:
            return q_symbols

        # Fallback to AST visitors
        symbols: list[SymbolEntry] = []
        if language == "python":
            symbols.extend(_extract_python_symbols(tree.root_node, content))
            symbols.extend(_extract_python_docstrings(tree.root_node, content, file_path))
        elif language in ["javascript", "typescript"]:
            symbols.extend(_extract_js_symbols(tree.root_node, content))

        for s in symbols:
            s.file = file_path
        return symbols
    except Exception:
        # Fallback docstrings for python only
        if language == "python":
            return _extract_python_docstrings(None, content, file_path)
        return []


def _extract_python_symbols(node: Node, content: str) -> List[SymbolEntry]:
    # Extract Python symbols.
    symbols = []
    
    def visit(n: Node) -> None:
        if n.type == "function_definition":
            name_node = n.child_by_field_name("name")
            if name_node:
                symbols.append(SymbolEntry(
                    file="",  # filled by caller
                    name=name_node.text.decode(),
                    type="function",
                    start_line=n.start_point[0] + 1,
                    end_line=n.end_point[0] + 1,
                ))
        elif n.type == "class_definition":
            name_node = n.child_by_field_name("name")
            if name_node:
                symbols.append(SymbolEntry(
                    file="",
                    name=name_node.text.decode(),
                    type="class",
                    start_line=n.start_point[0] + 1,
                    end_line=n.end_point[0] + 1,
                ))
        for child in getattr(n, 'children', []) or []:
            visit(child)
    
    visit(node)
    return symbols


def _extract_js_symbols(node: Node, content: str) -> List[SymbolEntry]:
    # Extract JavaScript/TypeScript symbols.
    symbols = []
    
    def visit(n: Node) -> None:
        if n.type in ["function_declaration", "function_expression"]:
            name_node = n.child_by_field_name("name")
            if name_node:
                symbols.append(SymbolEntry(
                    file="",
                    name=name_node.text.decode(),
                    type="function",
                    start_line=n.start_point[0] + 1,
                    end_line=n.end_point[0] + 1,
                ))
        elif n.type == "class_declaration":
            name_node = n.child_by_field_name("name")
            if name_node:
                symbols.append(SymbolEntry(
                    file="",
                    name=name_node.text.decode(),
                    type="class",
                    start_line=n.start_point[0] + 1,
                    end_line=n.end_point[0] + 1,
                ))
        for child in getattr(n, 'children', []) or []:
            visit(child)
    
    visit(node)
    return symbols


def build_code_map(source_dir: str, options: BuildOptions) -> None:
    # Build complete code map from source directory (incremental).
    start_time = time.time()
    source_path = Path(source_dir)
    out_path = source_path / options.out_dir
    out_path.mkdir(exist_ok=True)

    # Incremental: load previous outputs (if any)
    prev_files: Dict[str, FileEntry] = {}
    prev_symbols_by_file: Dict[str, List[SymbolEntry]] = {}
    prev_chunks_by_file: Dict[str, List[ChunkEntry]] = {}

    files_jsonl = out_path / "files.jsonl"
    symbols_jsonl = out_path / "symbols.jsonl"
    chunks_jsonl = out_path / "chunks.jsonl"

    if options.incremental:
        if files_jsonl.exists():
            for line in files_jsonl.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                fe = FileEntry.model_validate_json(line)
                prev_files[fe.path] = fe
        if symbols_jsonl.exists():
            for line in symbols_jsonl.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                se = SymbolEntry.model_validate_json(line)
                prev_symbols_by_file.setdefault(se.file, []).append(se)
        if chunks_jsonl.exists():
            for line in chunks_jsonl.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                ce = ChunkEntry.model_validate_json(line)
                prev_chunks_by_file.setdefault(ce.file, []).append(ce)

    new_files: List[FileEntry] = []
    new_symbols: List[SymbolEntry] = []
    new_chunks: List[ChunkEntry] = []
    languages: Dict[str, int] = {}
    relations: List[RelationEntry] = []

    # Walk directory and process files
    for file_path in source_path.rglob("*"):
        # Skip generated output directory
        if str(file_path).startswith(str(out_path)):
            continue
        if not file_path.is_file():
            continue
        # Skip ignored directories (by part match)
        if any(part in options.ignore_dirs for part in file_path.parts):
            continue
        # Skip large files
        stat = file_path.stat()
        if stat.st_size > options.max_file_size:
            continue

        relative_path = file_path.relative_to(source_path)
        rel_str = str(relative_path)
        language = detect_language(rel_str)
        # Skip if language not in our target list (allow unknown to still index file metadata)
        if language != "unknown" and language not in options.languages:
            pass

        # Determine if unchanged (size + mtime match)
        prev = prev_files.get(rel_str)
        unchanged = False
        if options.incremental and prev is not None:
            try:
                unchanged = (int(prev.size) == int(stat.st_size)) and (float(prev.mtime) == float(stat.st_mtime))
            except Exception:
                unchanged = False

        if unchanged:
            # Reuse previous FileEntry; ensure language stays detected here for consistency
            fe = FileEntry(
                path=rel_str,
                size=stat.st_size,
                language=language,
                tokens_estimate=prev.tokens_estimate,
                mtime=stat.st_mtime,
            )
            new_files.append(fe)
            languages[language] = languages.get(language, 0) + 1
            # Reuse previous symbols/chunks
            for se in prev_symbols_by_file.get(rel_str, []):
                new_symbols.append(se)
            for ce in prev_chunks_by_file.get(rel_str, []):
                new_chunks.append(ce)
            # Skip imports for unchanged files
            continue

        # Changed or new file: parse fresh
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        fe = FileEntry(
            path=rel_str,
            size=stat.st_size,
            language=language,
            tokens_estimate=estimate_tokens(content),
            mtime=stat.st_mtime,
        )
        new_files.append(fe)
        languages[language] = languages.get(language, 0) + 1

        # Compute imports via query or fallback
        rels_q: List[RelationEntry] = []
        if tsl is not None and Parser is not None and language in LANGUAGE_MAPPING:
            try:
                parser = Parser()
                lang_obj = tsl.get_language(LANGUAGE_MAPPING[language])
                parser.set_language(lang_obj)
                tree = parser.parse(content.encode())
                rels_q = _extract_imports_with_query(lang_obj, tree, language, rel_str, content)
            except Exception:
                rels_q = []
        rels_fallback = _extract_imports_fallback(language, rel_str, content)
        relations.extend(rels_q or rels_fallback)

        # Extract symbols if supported language
        if language in options.languages:
            file_symbols = parse_file_symbols(rel_str, content, language)
            for symbol in file_symbols:
                symbol.file = rel_str
            new_symbols.extend(file_symbols)

            # Create chunks (simple line-based for now)
            lines = content.split('\n')
            chunk_size = max(1, getattr(options, "chunk_lines", 100))  # lines per chunk
            for i in range(0, len(lines), chunk_size):
                chunk_lines = lines[i:i + chunk_size]
                chunk_content = '\n'.join(chunk_lines)
                new_chunks.append(ChunkEntry(
                    file=rel_str,
                    start_line=i + 1,
                    end_line=min(i + chunk_size, len(lines)),
                    tokens_estimate=estimate_tokens(chunk_content),
                    content_hash=str(hash(chunk_content)),
                ))

    # Write outputs
    summary = CodeMapSummary(
        total_files=len(new_files),
        total_symbols=len(new_symbols),
        total_chunks=len(new_chunks),
        languages=languages,
        build_time=time.time() - start_time,
    )

    (out_path / "map.json").write_text(summary.model_dump_json(indent=2))

    with open(out_path / "files.jsonl", "w", encoding="utf-8") as f:
        for fe in sorted(new_files, key=lambda x: x.path):
            f.write(fe.model_dump_json() + "\n")

    with open(out_path / "symbols.jsonl", "w", encoding="utf-8") as f:
        for se in sorted(new_symbols, key=lambda s: (s.file, s.start_line, s.end_line, s.name)):
            f.write(se.model_dump_json() + "\n")

    with open(out_path / "chunks.jsonl", "w", encoding="utf-8") as f:
        for ce in sorted(new_chunks, key=lambda c: (c.file, c.start_line, c.end_line)):
            f.write(ce.model_dump_json() + "\n")

    # Write relations
    rel_path = out_path / "relations.jsonl"
    with open(rel_path, "w", encoding="utf-8") as f:
        for r in relations:
            f.write(r.model_dump_json() + "\n")

