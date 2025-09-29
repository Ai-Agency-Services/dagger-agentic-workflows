"""Tests for new snake_case API."""

import json
import tempfile
from pathlib import Path

import pytest

from code_map.engine.detect import detect_language
from code_map.engine.tokens import parse_tokens_from_text
from code_map.engine.scores import accumulate_token_scores


def test_detect_language():
    """Test language detection utility."""
    # Extension-based
    assert detect_language("test.py", "") == "python"
    assert detect_language("test.js", "") == "javascript"
    assert detect_language("test.ts", "") == "typescript"
    assert detect_language("test.unknown", "") is None
    
    # Shebang-based
    assert detect_language("script", "#!/usr/bin/env python3\n") == "python"
    assert detect_language("script", "#!/usr/bin/node\n") == "javascript"
    
    # Override
    overrides = {".custom": "python"}
    assert detect_language("test.custom", "", overrides) == "python"


def test_parse_tokens_python():
    """Test parsing tokens from Python code."""
    code = '''
def hello_world():
    print("Hello")
    return 42

class MyClass:
    def method(self):
        hello_world()
'''
    
    result = parse_tokens_from_text(code, "test.py", language_hint="python")
    
    assert result["language"] == "python"
    
    # Check identifiers
    identifiers = result["identifiers"]
    names = [i["name"] for i in identifiers]
    assert "hello_world" in names
    assert "MyClass" in names
    assert "method" in names
    
    # Check calls
    calls = result["calls"]
    callees = [c["callee"] for c in calls]
    assert "print" in callees or "hello_world" in callees


def test_accumulate_token_scores():
    """Test token score accumulation."""
    file_data = [
        ("file1.py", {
            "identifiers": [
                {"name": "foo", "kind": "function", "start": {"line": 1, "col": 0}}
            ],
            "calls": [
                {"callee": "bar", "location": {"line": 2, "col": 4}, "file": "file1.py"}
            ]
        }),
        ("file2.py", {
            "identifiers": [
                {"name": "foo", "kind": "function", "start": {"line": 1, "col": 0}}
            ],
            "calls": []
        })
    ]
    
    file_scores, token_callers = accumulate_token_scores(file_data)
    
    # Check file scores
    assert "file1.py" in file_scores
    assert "file2.py" in file_scores
    assert file_scores["file1.py"]["foo"] == 2.0  # function weight
    assert file_scores["file1.py"]["bar"] == 0.5   # call weight
    
    # Check token callers
    assert "foo" in token_callers
    assert len(token_callers["foo"]) == 2  # defined in both files
    assert "bar" in token_callers
    assert len(token_callers["bar"]) == 1  # called in file1


def test_parse_tokens_fallback():
    """Test fallback parsing when Tree-sitter is unavailable."""
    code = '''
def test_function():
    some_call()
    return True

class TestClass:
    pass
'''
    
    # Mock Tree-sitter being unavailable
    import code_map.engine.tokens as tokens_module
    original_tsl = tokens_module.tsl
    tokens_module.tsl = None
    
    try:
        result = parse_tokens_from_text(code, "test.py", language_hint="python")
        
        assert result["language"] == "python"
        
        # Check fallback parsing found some identifiers
        identifiers = result["identifiers"]
        names = [i["name"] for i in identifiers]
        assert "test_function" in names
        assert "TestClass" in names
        
        # Check calls
        calls = result["calls"]
        callees = [c["callee"] for c in calls]
        assert "some_call" in callees
        
    finally:
        tokens_module.tsl = original_tsl
