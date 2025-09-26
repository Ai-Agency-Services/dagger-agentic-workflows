import os
import sys
import tempfile
import importlib.util


def load_project_files_module():
    # Dynamically load shared/agent-utils/project_files.py without relying on package import
    here = os.path.dirname(__file__)
    proj_root = os.path.abspath(os.path.join(here, '..'))
    module_path = os.path.join(proj_root, 'project_files.py')
    spec = importlib.util.spec_from_file_location('agent_utils_project_files', module_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules['agent_utils_project_files'] = mod
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def test_get_project_file_tree_smoke():
    project_files = load_project_files_module()

    with tempfile.TemporaryDirectory() as tmpd:
        # Create a tiny repo structure
        os.makedirs(os.path.join(tmpd, 'src'), exist_ok=True)
        # Source file
        with open(os.path.join(tmpd, 'src', 'a.py'), 'w', encoding='utf-8') as f:
            f.write('def foo():\n    return 42\n')
        # Binary file (contains a null byte)
        with open(os.path.join(tmpd, 'src', 'bin.dat'), 'wb') as f:
            f.write(b'\x00\x01\x02')
        # Large file (>1MB) to trigger size skip
        big_path = os.path.join(tmpd, 'src', 'big.txt')
        with open(big_path, 'wb') as f:
            f.write(b'A' * (project_files.MAX_FILE_SIZE_BYTES + 10))

        tree = project_files.get_project_file_tree(tmpd, max_files=100)
        assert isinstance(tree, list)
        # Flatten and collect paths
        flat = project_files.flatten_tree(tree)
        file_paths = {n.filePath for n in flat if getattr(n, 'type', '') == 'file'}

        # We should see src/a.py included
        assert 'src/a.py' in file_paths
        # Binary and large files should be excluded
        assert 'src/bin.dat' not in file_paths
        assert 'src/big.txt' not in file_paths

        # Basic shape validations
        assert all(hasattr(n, 'name') and hasattr(n, 'filePath') for n in flat)
