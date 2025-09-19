"""Comprehensive unit tests for smell detection workflow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))


class TestCodeSmellEnum:
    """Test CodeSmell enumeration."""
    
    @pytest.mark.unit
    def test_smell_severity_values(self):
        """Test SmellSeverity enum values."""
        from smell.main import SmellSeverity
        
        assert SmellSeverity.LOW.value == "LOW"
        assert SmellSeverity.MEDIUM.value == "MEDIUM"
        assert SmellSeverity.HIGH.value == "HIGH"
        assert SmellSeverity.CRITICAL.value == "CRITICAL"

    @pytest.mark.unit
    def test_code_smell_creation(self):
        """Test CodeSmell dataclass creation."""
        from smell.main import CodeSmell, SmellSeverity
        
        smell = CodeSmell(
            name="test_smell",
            description="Test smell description",
            severity=SmellSeverity.HIGH,
            location="test.py:10",
            metrics={"symbol_name": "test_function"},
            recommendation="Fix this test smell"
        )
        
        assert smell.name == "test_smell"
        assert smell.description == "Test smell description"
        assert smell.severity == SmellSeverity.HIGH
        assert smell.location == "test.py:10"
        assert smell.metrics["symbol_name"] == "test_function"
        assert smell.recommendation == "Fix this test smell"

    @pytest.mark.unit
    def test_code_smell_str_representation(self):
        """Test CodeSmell string representation."""
        from smell.main import CodeSmell, SmellSeverity
        
        smell = CodeSmell(
            name="Long Function",
            description="Function is too long",
            severity=SmellSeverity.MEDIUM,
            location="module.py:25",
            metrics={"symbol_name": "very_long_function"},
            recommendation="Break into smaller functions"
        )
        
        str_repr = str(smell)
        assert "Long Function" in str_repr
        assert "MEDIUM" in str_repr
        assert "module.py:25" in str_repr
        assert "Function is too long" in str_repr


class TestCircularDependencyDetector:
    """Test CircularDependencyDetector."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.dag')
    async def test_detect_no_cycles(self, mock_dag):
        """Test detection with no circular dependencies."""
        from smell.main import CircularDependencyDetector
        
        # Mock Neo4j service with no cycles
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query.return_value = ""  # No cycles found
        mock_dag.neo_service.return_value = mock_neo_service
        
        detector = CircularDependencyDetector()
        detector.config_file = MagicMock()
        detector.neo_password = MagicMock()
        detector.github_access_token = MagicMock()
        detector.neo_auth = MagicMock()
        detector.neo_data = MagicMock()
        
        smells = await detector.detect(mock_neo_service)
        
        assert len(smells) == 0
        mock_neo_service.run_query.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.dag')
    async def test_detect_with_cycles(self, mock_dag):
        """Test detection with circular dependencies."""
        from smell.main import CircularDependencyDetector
        
        # Mock Neo4j service with cycles
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query.return_value = "file1.py\nfile2.py\nfile3.py"
        mock_dag.neo_service.return_value = mock_neo_service
        
        detector = CircularDependencyDetector()
        detector.config_file = MagicMock()
        detector.neo_password = MagicMock()
        detector.github_access_token = MagicMock()
        detector.neo_auth = MagicMock()
        detector.neo_data = MagicMock()
        
        smells = await detector.detect(mock_neo_service)
        
        assert len(smells) > 0
        assert smells[0].smell_type == "circular_dependency"
        assert "file1.py" in smells[0].description


class TestLargeClassDetector:
    """Test LargeClassDetector."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.dag')
    async def test_detect_no_large_classes(self, mock_dag):
        """Test detection with no large classes."""
        from smell.main import LargeClassDetector
        
        # Mock Neo4j service with small classes
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query.return_value = "SmallClass 5 small.py"
        mock_dag.neo_service.return_value = mock_neo_service
        
        detector = LargeClassDetector()
        detector.config_file = MagicMock()
        detector.neo_password = MagicMock()
        detector.github_access_token = MagicMock()
        detector.neo_auth = MagicMock()
        detector.neo_data = MagicMock()
        
        smells = await detector.detect(mock_neo_service)
        
        assert len(smells) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.dag')
    async def test_detect_large_classes(self, mock_dag):
        """Test detection with large classes."""
        from smell.main import LargeClassDetector
        
        # Mock Neo4j service with large classes
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query.return_value = "HugeClass 150 huge.py\nMassiveClass 200 massive.py"
        mock_dag.neo_service.return_value = mock_neo_service
        
        detector = LargeClassDetector()
        detector.config_file = MagicMock()
        detector.neo_password = MagicMock()
        detector.github_access_token = MagicMock()
        detector.neo_auth = MagicMock()
        detector.neo_data = MagicMock()
        
        smells = await detector.detect(mock_neo_service)
        
        assert len(smells) == 2
        assert all(smell.smell_type == "large_class" for smell in smells)
        assert "HugeClass" in smells[0].symbol_name
        assert "MassiveClass" in smells[1].symbol_name


class TestLongFunctionDetector:
    """Test LongFunctionDetector."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.dag')
    async def test_detect_long_functions(self, mock_dag):
        """Test detection of long functions."""
        from smell.main import LongFunctionDetector
        
        # Mock Neo4j service with long functions
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query.return_value = "long_function 1 70 long.py"
        mock_dag.neo_service.return_value = mock_neo_service
        
        detector = LongFunctionDetector()
        detector.config_file = MagicMock()
        detector.neo_password = MagicMock()
        detector.github_access_token = MagicMock()
        detector.neo_auth = MagicMock()
        detector.neo_data = MagicMock()
        
        smells = await detector.detect(mock_neo_service)
        
        assert len(smells) == 1
        assert smells[0].smell_type == "long_function"
        assert "long_function" in smells[0].symbol_name
        assert "69 lines" in smells[0].description


class TestHighFanOutDetector:
    """Test HighFanOutDetector."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.dag')
    async def test_detect_high_fan_out(self, mock_dag):
        """Test detection of high fan-out."""
        from smell.main import HighFanOutDetector
        
        # Mock Neo4j service with high fan-out
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query.return_value = "hub_function 25 hub.py"
        mock_dag.neo_service.return_value = mock_neo_service
        
        detector = HighFanOutDetector()
        detector.config_file = MagicMock()
        detector.neo_password = MagicMock()
        detector.github_access_token = MagicMock()
        detector.neo_auth = MagicMock()
        detector.neo_data = MagicMock()
        
        smells = await detector.detect(mock_neo_service)
        
        assert len(smells) == 1
        assert smells[0].smell_type == "high_fan_out"
        assert "hub_function" in smells[0].symbol_name
        assert "25 dependencies" in smells[0].description


class TestDeadCodeDetector:
    """Test DeadCodeDetector."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.dag')
    async def test_detect_dead_code(self, mock_dag):
        """Test detection of dead code."""
        from smell.main import DeadCodeDetector
        
        # Mock Neo4j service with unreferenced symbols
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query.return_value = "unused_function function 1 unused.py"
        mock_dag.neo_service.return_value = mock_neo_service
        
        detector = DeadCodeDetector()
        detector.config_file = MagicMock()
        detector.neo_password = MagicMock()
        detector.github_access_token = MagicMock()
        detector.neo_auth = MagicMock()
        detector.neo_data = MagicMock()
        
        smells = await detector.detect(mock_neo_service)
        
        assert len(smells) == 1
        assert smells[0].smell_type == "dead_code"
        assert "unused_function" in smells[0].symbol_name
        assert "never referenced" in smells[0].description


class TestGodComponentDetector:
    """Test GodComponentDetector."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.dag')
    async def test_detect_god_components(self, mock_dag):
        """Test detection of god components."""
        from smell.main import GodComponentDetector
        
        # Mock Neo4j service with god components
        mock_neo_service = AsyncMock()
        mock_neo_service.run_query.return_value = "god_module.py 15 50"  # 15 imports, 50 symbols
        mock_dag.neo_service.return_value = mock_neo_service
        
        detector = GodComponentDetector()
        detector.config_file = MagicMock()
        detector.neo_password = MagicMock()
        detector.github_access_token = MagicMock()
        detector.neo_auth = MagicMock()
        detector.neo_data = MagicMock()
        
        smells = await detector.detect(mock_neo_service)
        
        assert len(smells) == 1
        assert smells[0].smell_type == "god_component"
        assert "god_module.py" in smells[0].filepath
        assert "15 imports, 50 symbols" in smells[0].description


class TestSmellServiceIntegration:
    """Test Smell service integration."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('smell.main.yaml.safe_load')
    async def test_smell_service_creation(self, mock_yaml_load):
        """Test Smell service creation."""
        from smell.main import Smell
        
        mock_config = {
            "concurrency": {
                "max_concurrent": 5
            }
        }
        mock_yaml_load.return_value = mock_config
        
        mock_file = AsyncMock()
        mock_file.contents = AsyncMock(return_value="config content")
        
        service = await Smell.create(
            config_file=mock_file,
            neo_password=MagicMock(),
            github_access_token=MagicMock(),
            neo_auth=MagicMock(),
            neo_data=MagicMock()
        )
        
        assert service.config == mock_config

    @pytest.mark.unit
    def test_get_all_detectors(self):
        """Test getting all detector classes."""
        from smell.main import Smell
        
        service = MagicMock(spec=Smell)
        service._get_all_detectors = Smell._get_all_detectors.__get__(service, Smell)
        
        detectors = service._get_all_detectors()
        
        assert len(detectors) > 0
        # Check for some known detectors
        detector_names = [detector.__class__.__name__ for detector in detectors]
        assert "CircularDependencyDetector" in detector_names
        assert "LargeClassDetector" in detector_names
        assert "LongFunctionDetector" in detector_names

    @pytest.mark.unit
    def test_get_concurrency_config_with_config(self):
        """Test concurrency config extraction with config present."""
        from smell.main import Smell
        
        service = MagicMock(spec=Smell)
        service.config = {
            "container": {"work_dir": "/app"},
            "git": {"user_name": "test", "user_email": "test@test.com"},
            "concurrency": {
                "max_concurrent": 8
            }
        }
        service._get_concurrency_config = Smell._get_concurrency_config.__get__(service, Smell)
        
        config = service._get_concurrency_config()
        
        assert config["max_concurrent"] == 8

    @pytest.mark.unit
    def test_get_concurrency_config_defaults(self):
        """Test concurrency config with defaults."""
        from smell.main import Smell
        
        service = MagicMock(spec=Smell)
        service.config = {
            "container": {"work_dir": "/app"},
            "git": {"user_name": "test", "user_email": "test@test.com"}
        }  # No concurrency config
        service._get_concurrency_config = Smell._get_concurrency_config.__get__(service, Smell)
        
        config = service._get_concurrency_config()
        
        assert config["max_concurrent"] == 3  # Default value

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_detectors_concurrently_success(self):
        """Test running detectors concurrently with all successes."""
        from smell.main import Smell, CodeSmell, SmellSeverity
        
        # Mock detector that returns smells
        mock_detector1 = AsyncMock()
        mock_detector1.detect = AsyncMock(return_value=[
            CodeSmell("Detector1", "smell1", SmellSeverity.LOW, "desc1", "file1.py", 1)
        ])
        
        mock_detector2 = AsyncMock()
        mock_detector2.detect = AsyncMock(return_value=[
            CodeSmell("Detector2", "smell2", SmellSeverity.HIGH, "desc2", "file2.py", 2)
        ])
        
        service = MagicMock(spec=Smell)
        service.config_file = MagicMock()
        service.neo_password = MagicMock()
        service.github_access_token = MagicMock()
        service.neo_auth = MagicMock()
        service.neo_data = MagicMock()
        service._run_detectors_concurrently = Smell._run_detectors_concurrently.__get__(service, Smell)
        
        mock_logger = MagicMock()
        
        all_smells = await service._run_detectors_concurrently(
            [mock_detector1, mock_detector2], mock_logger, max_concurrent=2
        )
        
        assert len(all_smells) == 2
        assert all_smells[0].detector_name == "Detector1"
        assert all_smells[1].detector_name == "Detector2"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_detectors_concurrently_with_failure(self):
        """Test running detectors with one failure."""
        from smell.main import Smell, CodeSmell, SmellSeverity
        
        # Mock detector that succeeds
        mock_detector1 = AsyncMock()
        mock_detector1.detect = AsyncMock(return_value=[
            CodeSmell("Detector1", "smell1", SmellSeverity.LOW, "desc1", "file1.py", 1)
        ])
        
        # Mock detector that fails
        mock_detector2 = AsyncMock()
        mock_detector2.detect = AsyncMock(side_effect=Exception("Detector failed"))
        
        service = MagicMock(spec=Smell)
        service.config_file = MagicMock()
        service.neo_password = MagicMock()
        service.github_access_token = MagicMock()
        service.neo_auth = MagicMock()
        service.neo_data = MagicMock()
        service._run_detectors_concurrently = Smell._run_detectors_concurrently.__get__(service, Smell)
        
        mock_logger = MagicMock()
        
        all_smells = await service._run_detectors_concurrently(
            [mock_detector1, mock_detector2], mock_logger, max_concurrent=2
        )
        
        # Should only have results from successful detector
        assert len(all_smells) == 1
        assert all_smells[0].detector_name == "Detector1"
        
        # Should log the error
        mock_logger.error.assert_called()

    @pytest.mark.unit
    def test_generate_report_with_smells(self):
        """Test report generation with detected smells."""
        from smell.main import Smell, CodeSmell, SmellSeverity
        
        results = {
            "TestDetector": [
                CodeSmell("test_smell", "High severity smell", SmellSeverity.HIGH, "test.py:10", {"symbol": "test_func"}, "Fix this")
            ],
            "AnotherDetector": [
                CodeSmell("another_smell", "Medium severity smell", SmellSeverity.MEDIUM, "another.py:20", {}, "Fix that")
            ]
        }
        
        service = MagicMock(spec=Smell)
        service._generate_report = Smell._generate_report.__get__(service, Smell)
        
        report = service._generate_report(results)
        
        assert "=== CODE SMELL ANALYSIS REPORT ===" in report
        assert "Total smells detected: 2" in report
        assert "HIGH: 1" in report
        assert "MEDIUM: 1" in report
        assert "test.py:10" in report
        assert "test_func" in report
        assert "High severity smell" in report

    @pytest.mark.unit
    def test_generate_report_no_smells(self):
        """Test report generation with no smells detected."""
        from smell.main import Smell
        
        service = MagicMock(spec=Smell)
        service._generate_report = Smell._generate_report.__get__(service, Smell)
        
        report = service._generate_report({})
        
        assert "No code smells detected" in report
        assert "🎉" in report  # Celebration emoji


class TestSmellPublicAPI:
    """Test Smell service public API methods."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_analyze_codebase_full_workflow(self):
        """Test complete codebase analysis workflow."""
        from smell.main import Smell, CodeSmell, SmellSeverity
        
        service = MagicMock(spec=Smell)
        service._get_all_detectors = MagicMock(return_value=[MagicMock()])
        service._get_concurrency_config = MagicMock(return_value={"max_concurrent": 3})
        service._setup_logging = MagicMock(return_value=MagicMock())
        service._run_detectors_concurrently = AsyncMock(return_value=[
            CodeSmell("TestDetector", "test_smell", SmellSeverity.LOW, "Test smell", "test.py", 1)
        ])
        service._generate_report = MagicMock(return_value="Test report")
        
        service.analyze_codebase = Smell.analyze_codebase.__get__(service, Smell)
        
        result = await service.analyze_codebase()
        
        assert result == "Test report"
        service._get_all_detectors.assert_called_once()
        service._run_detectors_concurrently.assert_called_once()
        service._generate_report.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_specific_detector_valid(self):
        """Test analyzing with a specific valid detector."""
        from smell.main import Smell, CircularDependencyDetector
        
        service = MagicMock(spec=Smell)
        service.config_file = MagicMock()
        service.neo_password = MagicMock()
        service.github_access_token = MagicMock()
        service.neo_auth = MagicMock()
        service.neo_data = MagicMock()
        service._setup_logging = MagicMock(return_value=MagicMock())
        service._generate_report = MagicMock(return_value="Specific detector report")
        
        service.analyze_specific_detector = Smell.analyze_specific_detector.__get__(service, Smell)
        
        with patch.object(CircularDependencyDetector, 'detect', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = []
            
            result = await service.analyze_specific_detector("CircularDependencyDetector")
            
            assert result == "Specific detector report"
            mock_detect.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_specific_detector_invalid(self):
        """Test analyzing with an invalid detector name."""
        from smell.main import Smell
        
        service = MagicMock(spec=Smell)
        service.analyze_specific_detector = Smell.analyze_specific_detector.__get__(service, Smell)
        
        result = await service.analyze_specific_detector("NonExistentDetector")
        
        assert "Error: Detector 'NonExistentDetector' not found" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_multiple_detectors_valid(self):
        """Test analyzing with multiple valid detectors."""
        from smell.main import Smell
        
        service = MagicMock(spec=Smell)
        service._get_concurrency_config = MagicMock(return_value={"max_concurrent": 2})
        service._setup_logging = MagicMock(return_value=MagicMock())
        service._run_detectors_concurrently = AsyncMock(return_value=[])
        service._generate_report = MagicMock(return_value="Multiple detectors report")
        
        service.analyze_multiple_detectors = Smell.analyze_multiple_detectors.__get__(service, Smell)
        
        result = await service.analyze_multiple_detectors(["CircularDependencyDetector", "LargeClassDetector"])
        
        assert result == "Multiple detectors report"
        service._run_detectors_concurrently.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_multiple_detectors_with_invalid(self):
        """Test analyzing with some invalid detector names."""
        from smell.main import Smell
        
        service = MagicMock(spec=Smell)
        service.analyze_multiple_detectors = Smell.analyze_multiple_detectors.__get__(service, Smell)
        
        result = await service.analyze_multiple_detectors(["CircularDependencyDetector", "InvalidDetector"])
        
        assert "Invalid detector names: InvalidDetector" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_multiple_detectors_all_invalid(self):
        """Test analyzing with all invalid detector names."""
        from smell.main import Smell
        
        service = MagicMock(spec=Smell)
        service.analyze_multiple_detectors = Smell.analyze_multiple_detectors.__get__(service, Smell)
        
        result = await service.analyze_multiple_detectors(["Invalid1", "Invalid2"])
        
        assert "Invalid detector names: Invalid1, Invalid2" in result