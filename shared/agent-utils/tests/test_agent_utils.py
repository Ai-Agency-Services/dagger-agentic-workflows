import os
import sys
import json
import pytest
from unittest.mock import MagicMock

# Ensure module src is on sys.path when running tests locally
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from agent_utils.main import should_ignore_path, detect_language, AgentUtils


@pytest.mark.unit
@pytest.mark.utils
def test_should_ignore_path_basic():
    assert should_ignore_path('src/node_modules/pkg/foo.py', ['node_modules']) is True
    assert should_ignore_path('src/.venv/pkg/bar.py', ['.venv']) is True
    assert should_ignore_path('src/app/foo.py', ['node_modules', '.venv']) is False
    assert should_ignore_path('src/app/build/foo.py', ['dist', 'build']) is True


@pytest.mark.unit
@pytest.mark.parsing
def test_detect_language_common():
    assert detect_language('file.py') == 'python'
    assert detect_language('file.tsx') == 'typescript'
    assert detect_language('file.rs') == 'rust'
    assert detect_language('file.unknown') == 'unknown'


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_code_file_to_json_respects_ignore_dirs(monkeypatch):
    # Patch dag.directory() chain so we don't need a Dagger engine
    class FakeFile:
        def __init__(self, content):
            self._content = content
        async def contents(self):
            return self._content

    class FakeDir:
        def __init__(self):
            self._content = None
        def with_new_file(self, _path, content):
            self._content = content
            return self
        def file(self, _path):
            return FakeFile(self._content)

    fake_dag = MagicMock()
    fake_dag.directory.return_value = FakeDir()

    # Patch the dag module used inside agent_utils.main
    import agent_utils.main as mod
    monkeypatch.setattr(mod, 'dag', fake_dag)

    utils = AgentUtils()
    content = 'def foo(x):\n    return x\n'
    filepath = 'lib/node_modules/foo.py'

    result_file = await utils.parse_code_file_to_json(
        content=content,
        filepath=filepath,
        ignore_dirs=['node_modules', '.venv']
    )

    text = await result_file.contents()
    data = json.loads(text)

    assert data['filepath'] == filepath
    assert data['language'] == 'python'
    assert data['symbols'] == []
    assert data['imports'] == []
