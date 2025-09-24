import json
import pytest
from unittest.mock import MagicMock

@pytest.mark.unit
@pytest.mark.asyncio
async def test_skip_toml_files(monkeypatch):
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

    import agent_utils.main as mod
    # Make dag.directory() return our FakeDir()
    mock_dag = MagicMock()
    mock_dag.directory = lambda: FakeDir()
    monkeypatch.setattr(mod, 'dag', mock_dag)

    utils = mod.AgentUtils()
    content = "[tool.poetry]\nname='demo'\n"
    filepath = "pyproject.toml"

    f = await utils.parse_code_file_to_json(content, filepath)
    data = json.loads(await f.contents())

    assert data["filepath"] == filepath
    assert data["symbols"] == []
    assert data["imports"] == []
    assert data["language"] == "unknown"

@pytest.mark.unit
@pytest.mark.asyncio
async def test_skip_shell_files(monkeypatch):
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

    import agent_utils.main as mod
    mock_dag = MagicMock()
    mock_dag.directory = lambda: FakeDir()
    monkeypatch.setattr(mod, 'dag', mock_dag)

    utils = mod.AgentUtils()
    content = "#!/usr/bin/env bash\necho hello\n"
    filepath = "script.sh"

    f = await utils.parse_code_file_to_json(content, filepath)
    data = json.loads(await f.contents())

    assert data["filepath"] == filepath
    assert data["symbols"] == []
    assert data["imports"] == []
    assert data["language"] == "unknown"
