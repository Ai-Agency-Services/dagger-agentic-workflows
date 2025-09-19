"""Unit tests for newly added smell detectors leveraging graph data."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_large_class_by_lines_detector():
    from smell.main import LargeClassByLinesDetector, CodeSmell, SmellSeverity

    # Mock Neo4j service output with header and two rows
    mock_neo = AsyncMock()
    mock_neo.run_query = AsyncMock(return_value=(
        "file class lines\n"
        "src/models/user.py User 520\n"
        "src/models/big.py BigClass 820\n"
    ))

    detector = LargeClassByLinesDetector()
    smells = await detector.detect(mock_neo)

    assert len(smells) == 2
    assert smells[0].name == "Large Class (by LOC)"
    assert smells[0].severity in (SmellSeverity.HIGH, SmellSeverity.CRITICAL)
    assert smells[0].metrics["lines"] == 520
    assert smells[1].severity == SmellSeverity.CRITICAL


@pytest.mark.unit
@pytest.mark.asyncio
async def test_long_parameter_list_detector():
    from smell.main import LongParameterListDetector, SmellSeverity

    mock_neo = AsyncMock()
    # file name kind param_count
    mock_neo.run_query = AsyncMock(return_value=(
        "file name kind param_count\n"
        "src/api/user.py create_user Function 7\n"
        "src/core/service.py process Method 10\n"
    ))

    detector = LongParameterListDetector()
    smells = await detector.detect(mock_neo)

    assert len(smells) == 2
    assert smells[0].name == "Long Parameter List"
    assert smells[0].metrics["parameters"] == 7
    assert smells[0].severity == SmellSeverity.MEDIUM
    assert smells[1].severity == SmellSeverity.HIGH


@pytest.mark.unit
@pytest.mark.asyncio
async def test_god_class_by_methods_detector():
    from smell.main import GodClassByMethodsDetector, SmellSeverity

    mock_neo = AsyncMock()
    # file class methods
    mock_neo.run_query = AsyncMock(return_value=(
        "file class methods\n"
        "src/ui/view.py View 22\n"
        "src/ui/mega_view.py MegaView 45\n"
    ))

    detector = GodClassByMethodsDetector()
    smells = await detector.detect(mock_neo)

    assert len(smells) == 2
    assert smells[0].name == "God Class (by methods)"
    assert smells[0].metrics["methods"] == 22
    assert smells[0].severity == SmellSeverity.HIGH
    assert smells[1].severity == SmellSeverity.CRITICAL


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dead_code_detector_revised():
    from smell.main import DeadCodeDetector

    mock_neo = AsyncMock()
    # unused_symbol symbol_type file
    mock_neo.run_query = AsyncMock(return_value=(
        "unused_symbol symbol_type file\n"
        "do_stuff Function src/utils/helpers.py\n"
    ))

    detector = DeadCodeDetector()
    smells = await detector.detect(mock_neo)

    assert len(smells) == 1
    s = smells[0]
    assert s.name == "Dead Code"
    assert s.metrics["unused_symbol"] == "do_stuff"
    assert s.location == "src/utils/helpers.py"
