import os
import sys
import importlib.util


def load_module(relative_path: str, name: str):
    here = os.path.dirname(__file__)
    proj_root = os.path.abspath(os.path.join(here, '..'))
    module_path = os.path.join(proj_root, relative_path)
    spec = importlib.util.spec_from_file_location(name, module_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def test_truncate_file_tree_based_on_token_budget_smoke():
    # Load modules dynamically so tests don't depend on packaging
    project_files = load_module('project_files.py', 'agent_utils_project_files')
    code_tree = load_module('code_tree.py', 'agent_utils_code_tree')

    # Build a tiny fake tree structure
    FileTreeNode = project_files.FileTreeNode
    tree = [
        FileTreeNode(
            name='src', type='directory', filePath='src', children=[
                FileTreeNode(name='a.py', type='file', filePath='src/a.py', lastReadTime=0.0),
                FileTreeNode(name='b.py', type='file', filePath='src/b.py', lastReadTime=0.0),
            ]
        )
    ]

    # Token scores with many tokens to force pruning
    token_scores = {
        'src/a.py': {f'tok{i}': 1.0 for i in range(200)},
        'src/b.py': {f'var{i}': 0.5 for i in range(150)},
    }

    # Large budget: should be none or unimportant/tokens fit
    printed_big, count_big, level_big = code_tree.truncate_file_tree_based_on_token_budget(
        tree, token_scores, token_budget=100000
    )
    assert isinstance(printed_big, str)
    assert count_big <= 100000
    assert level_big in {'none', 'unimportant-files', 'tokens', 'depth-based'}

    # Tiny budget: should trigger pruning and/or depth trimming
    printed_small, count_small, level_small = code_tree.truncate_file_tree_based_on_token_budget(
        tree, token_scores, token_budget=200
    )
    assert isinstance(printed_small, str)
    assert count_small <= 200
    assert level_small in {'unimportant-files', 'tokens', 'depth-based'}
