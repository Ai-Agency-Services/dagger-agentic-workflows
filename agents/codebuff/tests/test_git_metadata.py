from codebuff.utils.git_metadata import embed_state_metadata, extract_state_metadata


def test_embed_and_extract_footer():
    header = "feat: add cool thing\n\nAutomated commit: changes"
    msg = embed_state_metadata(header, task_id="abc123", phase="planning", status="success")

    assert "---\n{" in msg
    meta = extract_state_metadata(msg)
    assert meta is not None
    assert meta.get("task_id") == "abc123"
    assert meta.get("phase") == "planning"
    assert meta.get("status") == "success"


def test_extract_handles_no_footer():
    meta = extract_state_metadata("just a simple commit")
    assert meta is None
