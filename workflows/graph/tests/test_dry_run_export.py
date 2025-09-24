import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dry_run_captures_export_without_execution():
    from graph.main import Graph

    g = MagicMock(spec=Graph)
    g.neo_service = AsyncMock()
    g.neo_service.run_query = AsyncMock()

    g._execute_queries_in_concurrent_batches = Graph._execute_queries_in_concurrent_batches.__get__(g, Graph)
    export_acc = {}
    queries = ["Q1;", "Q2;", "Q3;"]

    successful, failed = await g._execute_queries_in_concurrent_batches(
        queries,
        "test",
        MagicMock(),
        batch_size=2,
        max_concurrent_batches=1,
        export_accumulator=export_acc,
        execute=False,
        throttle_ms=None,
    )

    # All queries are counted as successful (captured), none failed
    assert successful == 3
    assert failed == 0

    # Export accumulator has two batches: ["Q1;\nQ2;", "Q3;"]
    assert "test" in export_acc
    assert len(export_acc["test"]) == 2
    assert "Q1;" in export_acc["test"][0] and "Q2;" in export_acc["test"][0]
    assert "Q3;" in export_acc["test"][1]

    # Ensure no DB execution happened
    g.neo_service.run_query.assert_not_called()
