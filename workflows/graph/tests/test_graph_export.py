import os
import sys
import json
import pytest
from unittest.mock import MagicMock

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


def test_join_batches_uses_cypher_comments():
    from graph.main import Graph

    g = MagicMock(spec=Graph)
    g._join_batches = Graph._join_batches.__get__(g, Graph)

    out = g._join_batches(["CREATE (n) RETURN n;", "MATCH (m) RETURN m;"])
    lines = out.splitlines()

    # First line should be a Cypher comment header
    assert lines[0].startswith("// BATCH 00001")
    # Should contain the statements too
    assert "CREATE (n) RETURN n;" in out
    assert "MATCH (m) RETURN m;" in out


def test_build_chunked_export_files_semicolons_and_summary():
    from graph.main import Graph

    g = MagicMock(spec=Graph)
    g._join_batches = Graph._join_batches.__get__(g, Graph)
    g._build_chunked_export_files = Graph._build_chunked_export_files.__get__(g, Graph)

    # Prepare export accumulator large enough to require chunking (<=20 chunks/type)
    export_acc = {
        "node-symbol": [f"MERGE (n:Test {{i:{i}}});" for i in range(55)],
        "defined-in": [f"MATCH (a) MATCH (b) MERGE (a)-[:DEFINED_IN]->(b);" for _ in range(7)],
        "import": ["MERGE (:File {filepath:'a'})-[:IMPORTS]->(:File {filepath:'b'});"] * 3,
    }
    summary = {"processed_files": 1, "failed_files": 0, "batch_counts": {k: len(v) for k, v in export_acc.items()}}

    files = g._build_chunked_export_files("batches", export_acc, summary)

    # Should include a summary.json
    assert any(path.endswith("summary.json") for path, _ in files)

    # Node-symbol should be chunked into at most 20 files
    ns_files = [p for p, _ in files if "/node-symbol_" in p]
    assert 1 <= len(ns_files) <= 20

    # Each cypher file should contain a // BATCH header
    cypher_files = [(p, c) for p, c in files if p.endswith('.cypher')]
    assert len(cypher_files) > 0
    assert all("// BATCH" in c for _, c in cypher_files)
