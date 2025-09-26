from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Set

from .project_files import FileTreeNode

TRUNCATION_NONE = 'none'
TRUNCATION_UNIMPORTANT = 'unimportant-files'
TRUNCATION_TOKENS = 'tokens'
TRUNCATION_DEPTH = 'depth-based'

UNIMPORTANT_EXTS_OR_DIRS = [
    '.min.js', '.min.css', '.map', '.d.ts',
    '.pyc', '.pyo', '__pycache__', '.pyd', '.so', '.egg-info', '.whl',
    '.class', '.jar', '.war',
    '.gem', '.rbc',
    '/dist/', '/build/', '/out/', '/target/',
    '/node_modules/', '/.venv/', '/vendor/',
    '.log', '.tmp', '.temp', '.swp', '.bak', '.cache',
    '.docx', '.pdf', '.chm',
    '.zip', '.tar', '.gz', '.rar', '.7z', '.iso', '.dmg', '.pkg', '.deb', '.rpm', '.exe', '.dll', '.lib', '.so',
    '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.mp3', '.mp4', '.mov', '.avi', '.bmp', '.tiff', '.tif', '.webp',
]


def estimate_token_count(text: str) -> int:
    return max(0, (len(text) + 2) // 3)


def _print_file_tree(nodes: List[FileTreeNode], depth: int = 0) -> str:
    result: List[str] = []
    indent = ' ' * depth
    for n in nodes:
        if n.type == 'directory':
            if not n.children:
                continue
            result.append(f"{indent}{n.name}/\n")
            result.append(_print_file_tree(n.children or [], depth + 1))
        else:
            result.append(f"{indent}{n.name}\n")
    return ''.join(result)


def print_file_tree(nodes: List[FileTreeNode]) -> str:
    return _print_file_tree(nodes, 0)


def _print_file_tree_with_tokens(
    nodes: List[FileTreeNode],
    file_token_scores: Dict[str, Dict[str, float]],
    path_stack: List[str],
) -> str:
    out: List[str] = []
    indent = ' ' * len(path_stack)
    extra_indent = ' ' * (len(path_stack) + 1)

    for n in nodes:
        if n.type == 'directory' and (not n.children or len(n.children) == 0):
            continue

        out.append(f"{indent}{n.name}{'/' if n.type == 'directory' else ''}")
        path_stack.append(n.name)
        rel = '/'.join(path_stack)

        if n.type == 'file':
            tokens = file_token_scores.get(rel)
            if tokens:
                token_names = list(tokens.keys())
                if token_names:
                    out.append("\n")
                    out.append(f"{extra_indent}{' '.join(token_names)}")
        out.append("\n")

        if n.type == 'directory' and n.children:
            out.append(_print_file_tree_with_tokens(n.children, file_token_scores, path_stack))
        path_stack.pop()
    return ''.join(out)


def print_file_tree_with_tokens(
    nodes: List[FileTreeNode],
    file_token_scores: Dict[str, Dict[str, float]],
) -> str:
    return _print_file_tree_with_tokens(nodes, file_token_scores, [])


def _filter_removed_files(node: FileTreeNode, removed: Set[str], prefix: str = '') -> Optional[FileTreeNode]:
    full_path = f"{prefix}/{node.name}" if prefix else node.name
    if node.type == 'file':
        return None if full_path in removed else node
    new_children: List[FileTreeNode] = []
    for c in node.children or []:
        kept = _filter_removed_files(c, removed, full_path)
        if kept is not None:
            new_children.append(kept)
    return FileTreeNode(name=node.name, type='directory', filePath=node.filePath, children=new_children) if new_children else None


def _remove_unimportant_files(nodes: List[FileTreeNode]) -> List[FileTreeNode]:
    def should_keep_file(node: FileTreeNode) -> bool:
        if node.type == 'directory':
            dir_path = node.filePath.lower()
            for ext in UNIMPORTANT_EXTS_OR_DIRS:
                if ext.startswith('/') and ext.endswith('/') and ext.strip('/') in dir_path:
                    return False
            kept_children = [c for c in (node.children or []) if should_keep_file(c)]
            node.children = kept_children
            return len(kept_children) > 0
        fp = node.filePath.lower()
        for ext in UNIMPORTANT_EXTS_OR_DIRS:
            if not ext.startswith('/') and fp.endswith(ext):
                return False
        return True

    return [n for n in nodes if should_keep_file(n)]


def _flatten_files_with_depth(nodes: List[FileTreeNode], parent_depth: int = 0) -> List[Tuple[str, int]]:
    out: List[Tuple[str, int]] = []
    for n in nodes:
        if n.type == 'file':
            out.append((n.filePath, parent_depth))
        else:
            for c in (n.children or []):
                out.extend(_flatten_files_with_depth([c], parent_depth + 1))
    return out


def _rebuild_tree_excluding(nodes: List[FileTreeNode], removed_paths: Set[str]) -> List[FileTreeNode]:
    out: List[FileTreeNode] = []
    for n in nodes:
        kept = _filter_removed_files(n, removed_paths, '')
        if kept is not None:
            out.append(kept)
    return out


def _prune_file_token_scores(
    file_tree: List[FileTreeNode],
    file_token_scores: Dict[str, Dict[str, float]],
    token_budget: int,
) -> Tuple[str, int]:
    all_tokens: List[Tuple[str, str, float]] = []
    for f, tokens in file_token_scores.items():
        for t, s in tokens.items():
            all_tokens.append((f, t, s))
    all_tokens.sort(key=lambda x: x[2])

    current_scores: Dict[str, Dict[str, float]] = {f: dict(ts) for f, ts in file_token_scores.items()}

    def current_print_and_count() -> Tuple[str, int]:
        printed = print_file_tree_with_tokens(file_tree, current_scores)
        return printed, estimate_token_count(printed)

    printed, count = current_print_and_count()
    if count <= token_budget:
        return printed, count

    idx = 0
    while count > token_budget and idx < len(all_tokens):
        batch_size = min(1000, len(all_tokens) - idx)
        for j in range(idx, idx + batch_size):
            f, t, _ = all_tokens[j]
            if f in current_scores and t in current_scores[f]:
                try:
                    del current_scores[f][t]
                    if not current_scores[f]:
                        del current_scores[f]
                except Exception:
                    pass
        idx += batch_size
        printed, count = current_print_and_count()

    return printed, count


def truncate_file_tree_based_on_token_budget(
    file_tree: List[FileTreeNode],
    file_token_scores: Dict[str, Dict[str, float]],
    token_budget: int,
) -> Tuple[str, int, str]:
    tree_with_tokens = print_file_tree_with_tokens(file_tree, file_token_scores)
    tree_tokens = estimate_token_count(tree_with_tokens)
    if tree_tokens <= token_budget:
        return tree_with_tokens, tree_tokens, TRUNCATION_NONE

    filtered_tree = _remove_unimportant_files([n for n in file_tree])
    printed_filtered = print_file_tree(filtered_tree)
    filtered_tokens = estimate_token_count(printed_filtered)
    if filtered_tokens <= token_budget:
        printed_with_tokens = print_file_tree_with_tokens(filtered_tree, file_token_scores)
        with_tokens_count = estimate_token_count(printed_with_tokens)
        if with_tokens_count <= token_budget:
            return printed_with_tokens, with_tokens_count, TRUNCATION_UNIMPORTANT
        pr_printed, pr_count = _prune_file_token_scores(filtered_tree, file_token_scores, token_budget)
        if pr_count <= token_budget:
            return pr_printed, pr_count, TRUNCATION_TOKENS

    current_tree = filtered_tree
    flattened = sorted(_flatten_files_with_depth(current_tree), key=lambda x: x[1], reverse=True)

    sample = flattened[: min(30, len(flattened))]
    sample_text = ' '.join([p for p, _ in sample])
    avg_tokens_per_file = max(1, estimate_token_count(sample_text) // max(1, len(sample)))

    removed: Set[str] = set()
    prev_count = 10**12
    iteration = 0

    def print_and_count() -> Tuple[str, int]:
        printed = print_file_tree(_rebuild_tree_excluding(current_tree, removed))
        return printed, estimate_token_count(printed)

    printed, count = print_and_count()
    while count > token_budget and iteration < 10 and flattened:
        tokens_to_remove = count - token_budget
        est_files = (tokens_to_remove // max(1, avg_tokens_per_file)) // 2 + 100
        batch = min(est_files, len(flattened))
        for i in range(batch):
            removed.add(flattened[i][0])
        flattened = flattened[batch:]
        printed, count = print_and_count()
        if count >= prev_count:
            break
        prev_count = count
        iteration += 1

    return printed, count, TRUNCATION_DEPTH
