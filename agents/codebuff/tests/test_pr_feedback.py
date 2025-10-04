import pytest

from codebuff.orchestrator.pr_feedback import parse_orchestrator_commands


def test_parse_approve():
    comments = [
        {"body": "Looks good"},
        {"body": "@orchestrator approve"},
    ]
    cmd = parse_orchestrator_commands(comments)
    assert cmd is not None
    assert cmd["action"] == "approve"
    assert cmd["args"] == ""


def test_parse_modify_with_args():
    comments = [
        {"body": "@orchestrator modify tighten error handling in start_task"}
    ]
    cmd = parse_orchestrator_commands(comments)
    assert cmd is not None
    assert cmd["action"] == "modify"
    assert "tighten error handling" in cmd["args"]


def test_parse_add_files():
    comments = [
        {"body": "@orchestrator add-files src/auth.py src/utils/helpers.py"}
    ]
    cmd = parse_orchestrator_commands(comments)
    assert cmd is not None
    assert cmd["action"] == "add-files"
    assert "src/auth.py" in cmd["args"]


def test_ignores_non_orchestrator():
    comments = [
        {"body": "this is not a command"},
        {"body": "@other something"},
    ]
    cmd = parse_orchestrator_commands(comments)
    assert cmd is None
