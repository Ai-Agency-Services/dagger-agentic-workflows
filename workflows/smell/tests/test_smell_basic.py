"""Basic working tests for smell detection workflow."""

import pytest
from unittest.mock import MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

class TestSmellBasic:
    """Basic tests to verify smell detection setup."""
    
    @pytest.mark.unit
    def test_smell_severity_enum(self):
        """Test SmellSeverity enum values."""
        from smell.main import SmellSeverity
        
        assert SmellSeverity.LOW.value == "LOW"
        assert SmellSeverity.MEDIUM.value == "MEDIUM"
        assert SmellSeverity.HIGH.value == "HIGH"
        assert SmellSeverity.CRITICAL.value == "CRITICAL"
    
    @pytest.mark.unit
    def test_code_smell_creation(self):
        """Test CodeSmell creation."""
        from smell.main import CodeSmell, SmellSeverity
        
        smell = CodeSmell(
            name="Test Smell",
            description="Test description",
            severity=SmellSeverity.MEDIUM,
            location="test.py",
            metrics={"test": "value"},
            recommendation="Fix it"
        )
        
        assert smell.name == "Test Smell"
        assert smell.severity == SmellSeverity.MEDIUM
        assert smell.location == "test.py"
        assert "MEDIUM" in str(smell)
    
    @pytest.mark.unit
    def test_detector_classes_exist(self):
        """Test that detector classes can be imported."""
        from smell.main import (
            CircularDependencyDetector,
            LargeClassDetector,
            LongFunctionDetector,
            DeadCodeDetector
        )
        
        # Test instantiation
        circular = CircularDependencyDetector()
        large = LargeClassDetector()
        long_func = LongFunctionDetector()
        dead = DeadCodeDetector()
        
        assert circular.get_name() == "Circular Dependencies"
        assert large.get_name() == "Large Classes/Files"
        assert long_func.get_name() == "Long Functions"
        assert dead.get_name() == "Dead Code"