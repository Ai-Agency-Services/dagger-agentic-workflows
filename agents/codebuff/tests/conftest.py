import sys
from pathlib import Path

# Add project root so `import agents.*` works when running from this module
# Order matters: put src first so Python package 'codebuff' wins over TS folder 'codebuff'
SRC_DIR = Path(__file__).resolve().parents[1] / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Add project root so `import agents.*` works when running from this module
# tests -> codebuff -> agents -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(1, str(PROJECT_ROOT))

# Force 'codebuff' to resolve to our Python package, not the top-level TS folder
try:
    import importlib
    pkg = importlib.import_module('codebuff')
    # If imported package is not from our src dir, re-alias
    pkg_file = getattr(pkg, '__file__', '') or ''
    if str(SRC_DIR) not in pkg_file:
        py_pkg = importlib.import_module('agents.codebuff.src.codebuff')
        sys.modules['codebuff'] = py_pkg
except Exception:
    try:
        py_pkg = importlib.import_module('agents.codebuff.src.codebuff')
        sys.modules['codebuff'] = py_pkg
    except Exception:
        pass
