import asyncio
import types
import pytest

# We import the helpers directly
from agents.codebuff.src.codebuff.utils.container_state import write_json, write_text, append_log, STATE_DIR

class FakeFile:
    def __init__(self, files, path):
        self._files = files
        self._path = path
    async def contents(self):
        return self._files.get(self._path, "")

class FakeContainer:
    def __init__(self):
        self.files = {}
    def with_new_file(self, path, content):
        self.files[path] = content
        return self
    def file(self, path):
        return FakeFile(self.files, path)

@pytest.mark.asyncio
async def test_write_json_and_log():
    c = FakeContainer()
    # Write JSON
    c = await write_json(c, "task.json", {"id": "123", "goal": "add feature"})
    assert f"{STATE_DIR}/task.json" in c.files
    assert "add feature" in c.files[f"{STATE_DIR}/task.json"]
    # Append logs (twice)
    c = await append_log(c, "start_task: 123 add feature")
    c = await append_log(c, "explore_codebase: completed")
    log_path = f"{STATE_DIR}/log.txt"
    assert log_path in c.files
    assert "start_task: 123 add feature" in c.files[log_path]
    assert "explore_codebase: completed" in c.files[log_path]

@pytest.mark.asyncio
async def test_write_text_overwrite():
    c = FakeContainer()
    c = await write_text(c, "implementation/diffs/commit.diff", "diff --git a b")
    path = f"{STATE_DIR}/implementation/diffs/commit.diff"
    assert path in c.files
    assert c.files[path].startswith("diff --git")
