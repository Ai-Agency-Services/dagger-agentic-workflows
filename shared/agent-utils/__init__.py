try:
    # Package-style imports
    from .project_files import ProjectFileContext, FileTreeNode, get_project_file_context, get_project_file_tree
    from .code_tree import (
        print_file_tree,
        print_file_tree_with_tokens,
        truncate_file_tree_based_on_token_budget,
        estimate_token_count,
    )
except Exception:
    # Module-style fallbacks for direct imports (e.g., tests loading by path)
    from project_files import ProjectFileContext, FileTreeNode, get_project_file_context, get_project_file_tree
    from code_tree import (
        print_file_tree,
        print_file_tree_with_tokens,
        truncate_file_tree_based_on_token_budget,
        estimate_token_count,
    )

__all__ = [
    'ProjectFileContext',
    'FileTreeNode',
    'get_project_file_context',
    'get_project_file_tree',
    'print_file_tree',
    'print_file_tree_with_tokens',
    'truncate_file_tree_based_on_token_budget',
    'estimate_token_count',
]
