import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Dict, List, Optional

import dagger
import yaml
from ais_dagger_agents_config.models import YAMLConfig
from dagger import Doc, dag, function, object_type
from dagger.client.gen import NeoService


class SmellSeverity(Enum):
    """Code smell severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class CodeSmell:
    """Represents a detected code smell"""
    name: str
    description: str
    severity: SmellSeverity
    location: str
    metrics: Dict[str, any]
    recommendation: str

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.name} in {self.location}: {self.description}"


class CodeSmellDetector(ABC):
    """Abstract base class for code smell detectors"""

    @abstractmethod
    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        """Detect code smells using Neo4j service"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the detector name"""
        pass


class CircularDependencyDetector(CodeSmellDetector):
    """Detects circular dependencies between modules"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        """Clean Code Principle: Avoid circular dependencies (Dependency Inversion Principle)"""
        query = """
        MATCH path = (a:File)-[:IMPORTS*2..4]->(a)
        WITH path, length(path) as cycle_length
        WHERE cycle_length <= 4
        RETURN 
            [n in nodes(path) | n.filepath] as cycle_files,
            cycle_length
        ORDER BY cycle_length ASC
        LIMIT 10
        """

        result = await neo_service.run_query(query)
        smells = []

        # Parse the cypher-shell output
        lines = [line.strip()
                 for line in result.strip().split('\n') if line.strip()]

        if len(lines) > 1:  # Has header + data
            for line in lines[1:]:  # Skip header
                if line and not line.startswith('cycle_files'):
                    smells.append(CodeSmell(
                        name="Circular Dependency",
                        description="Files form a circular import dependency",
                        severity=SmellSeverity.HIGH,
                        location="Multiple files",
                        metrics={"cycle_detected": True},
                        recommendation="Extract common interfaces or use dependency injection"
                    ))

        return smells

    def get_name(self) -> str:
        return "Circular Dependencies"


class LargeClassDetector(CodeSmellDetector):
    """Detects classes/files that violate Single Responsibility Principle"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        """Clean Code Principle: Single Responsibility Principle"""
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (symbol:Function|Class|Interface|Variable)-[:DEFINED_IN]->(f)
        
        WITH f, count(DISTINCT symbol) as symbol_count
        WHERE symbol_count > 20
        
        RETURN 
            f.filepath as file,
            f.language,
            symbol_count
        ORDER BY symbol_count DESC
        LIMIT 10
        """

        result = await neo_service.run_query(query)
        smells = []

        lines = [line.strip()
                 for line in result.strip().split('\n') if line.strip()]

        if len(lines) > 1:
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    filepath = parts[0].strip('"')
                    symbol_count = int(parts[2]) if parts[2].isdigit() else 0

                    severity = SmellSeverity.CRITICAL if symbol_count > 50 else SmellSeverity.HIGH if symbol_count > 35 else SmellSeverity.MEDIUM

                    smells.append(CodeSmell(
                        name="Large Class/File",
                        description=f"File contains {symbol_count} symbols, violating SRP",
                        severity=severity,
                        location=filepath,
                        metrics={"symbol_count": symbol_count},
                        recommendation="Split into smaller, focused modules"
                    ))

        return smells

    def get_name(self) -> str:
        return "Large Classes/Files"


class FeatureEnvyDetector(CodeSmellDetector):
    """Detects modules that depend heavily on other modules (Feature Envy)"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        """Clean Code Principle: Tell, Don't Ask"""
        query = """
        MATCH (f:File)-[:IMPORTS]->(external:File)
        WITH f, count(DISTINCT external) as external_deps
        WHERE external_deps > 8
        RETURN 
            f.filepath as envious_file,
            external_deps
        ORDER BY external_deps DESC
        LIMIT 8
        """

        result = await neo_service.run_query(query)
        smells = []

        lines = [line.strip()
                 for line in result.strip().split('\n') if line.strip()]

        if len(lines) > 1:
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    filepath = parts[0].strip('"')
                    external_deps = int(parts[1]) if parts[1].isdigit() else 0

                    severity = SmellSeverity.HIGH if external_deps > 15 else SmellSeverity.MEDIUM

                    smells.append(CodeSmell(
                        name="Feature Envy",
                        description=f"Module depends on {external_deps} external modules",
                        severity=severity,
                        location=filepath,
                        metrics={"external_dependencies": external_deps},
                        recommendation="Move functionality closer to the data it uses"
                    ))

        return smells

    def get_name(self) -> str:
        return "Feature Envy"


class DeadCodeDetector(CodeSmellDetector):
    """Detects potentially unused code"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        """Clean Code Principle: Delete dead code, don't comment it out"""
        query = """
        MATCH (symbol:Function|Class|Interface)-[:DEFINED_IN]->(f:File)
        WHERE symbol.scope = "public"
        AND NOT EXISTS {
            MATCH (other:File)-[:IMPORTS]->(f)
            WHERE other <> f
        }
        AND NOT f.filepath CONTAINS "test"
        RETURN 
            symbol.name as unused_symbol,
            labels(symbol)[0] as symbol_type,
            f.filepath as file
        LIMIT 15
        """

        result = await neo_service.run_query(query)
        smells = []

        lines = [line.strip()
                 for line in result.strip().split('\n') if line.strip()]

        if len(lines) > 1:
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    symbol_name = parts[0].strip('"')
                    symbol_type = parts[1].strip('"')
                    filepath = parts[2].strip('"')

                    smells.append(CodeSmell(
                        name="Dead Code",
                        description=f"Public {symbol_type.lower()} '{symbol_name}' appears to be unused",
                        severity=SmellSeverity.LOW,
                        location=filepath,
                        metrics={"unused_symbol": symbol_name,
                                 "symbol_type": symbol_type},
                        recommendation="Remove unused code or make it private if needed internally"
                    ))

        return smells

    def get_name(self) -> str:
        return "Dead Code"


class ShotgunSurgeryDetector(CodeSmellDetector):
    """Detects changes that affect many files (Shotgun Surgery)"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        """Clean Code Principle: Minimize coupling"""
        query = """
        MATCH (f1:File)-[:IMPORTS]->(shared:File)<-[:IMPORTS]-(f2:File)
        WHERE f1 <> f2
        WITH shared, count(DISTINCT f1) + count(DISTINCT f2) as dependent_count
        WHERE dependent_count > 10
        RETURN 
            shared.filepath as shared_dependency,
            dependent_count
        ORDER BY dependent_count DESC
        LIMIT 5
        """

        result = await neo_service.run_query(query)
        smells = []

        lines = [line.strip()
                 for line in result.strip().split('\n') if line.strip()]

        if len(lines) > 1:
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    filepath = parts[0].strip('"')
                    dependent_count = int(
                        parts[1]) if parts[1].isdigit() else 0

                    severity = SmellSeverity.CRITICAL if dependent_count > 20 else SmellSeverity.HIGH

                    smells.append(CodeSmell(
                        name="Shotgun Surgery",
                        description=f"Changes to this file will affect {dependent_count} other files",
                        severity=severity,
                        location=filepath,
                        metrics={"affected_files": dependent_count},
                        recommendation="Use Facade pattern or extract stable interfaces"
                    ))

        return smells

    def get_name(self) -> str:
        return "Shotgun Surgery"


@object_type
class Smell:
    """Code smell detection service using Clean Code principles"""
    config: dict
    config_file: dagger.File
    neo_data: Optional[dagger.CacheVolume] = None

    @classmethod
    async def create(cls,
                     config_file: Annotated[dagger.File, Doc("Path to the YAML config file")],
                     neo_data: Annotated[dagger.CacheVolume, Doc("Neo4j data cache volume")]) -> "Smell":
        """Create a Smell object from a YAML config file."""
        config_str = await config_file.contents()
        config_dict = yaml.safe_load(config_str)
        return cls(config=config_dict, config_file=config_file, neo_data=neo_data)

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("smell.main")

    def _get_all_detectors(self) -> List[CodeSmellDetector]:
        """Get all available code smell detectors"""
        return [
            CircularDependencyDetector(),
            LargeClassDetector(),
            FeatureEnvyDetector(),
            DeadCodeDetector(),
            ShotgunSurgeryDetector(),
        ]

    def _generate_report(self, results: Dict[str, List[CodeSmell]]) -> str:
        """Generate a clean, actionable report"""
        total_smells = sum(len(smells) for smells in results.values())

        if total_smells == 0:
            return """
🎉 === CLEAN CODE ANALYSIS RESULTS ===
✅ No major code smells detected!
Your codebase follows Clean Code principles well.
"""

        report_lines = [
            "🔍 === CLEAN CODE ANALYSIS RESULTS ===",
            f"📊 Total Code Smells Found: {total_smells}",
            f"🕒 Analysis Time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📋 === SUMMARY BY CATEGORY ===",
        ]

        # Summary section
        for category, smells in results.items():
            if smells:
                severity_counts = {}
                for smell in smells:
                    severity_counts[smell.severity.value] = severity_counts.get(
                        smell.severity.value, 0) + 1

                report_lines.append(
                    f"• {category}: {len(smells)} issues {severity_counts}")

        report_lines.extend([
            "",
            "🚨 === CRITICAL & HIGH PRIORITY ISSUES ===",
        ])

        # Critical issues first
        critical_found = False
        for category, smells in results.items():
            for smell in smells:
                if smell.severity in [SmellSeverity.CRITICAL, SmellSeverity.HIGH]:
                    critical_found = True
                    report_lines.extend([
                        f"⚠️  {smell}",
                        f"   💡 Recommendation: {smell.recommendation}",
                        ""
                    ])

        if not critical_found:
            report_lines.append("✅ No critical issues found!")

        report_lines.extend([
            "",
            "📖 === CLEAN CODE PRINCIPLES VIOLATED ===",
            "• Single Responsibility Principle (SRP)",
            "• Dependency Inversion Principle (DIP)",
            "• Tell, Don't Ask",
            "• Minimize Coupling",
            "• Delete Dead Code",
            "",
            "🎯 === NEXT STEPS ===",
            "1. Address CRITICAL issues first",
            "2. Focus on HIGH severity items",
            "3. Refactor large classes/files",
            "4. Break circular dependencies",
            "5. Remove or document dead code",
        ])

        return "\n".join(report_lines)

    @function
    async def analyze_codebase(
        self,
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
    ) -> str:
        """Analyze codebase for code smells using Clean Code principles."""
        logger = self._setup_logging()
        logger.info("Starting code smell analysis")

        try:
            # Create Neo4j service
            neo_service: NeoService = dag.neo_service(
                self.config_file,
                password=neo_password,
                github_access_token=github_access_token,
                neo_auth=neo_auth,
                neo_data=self.neo_data
            )

            # Test connection
            connection_test = await neo_service.simple_test()
            logger.info(f"Neo4j connection: {connection_test}")

            # Run all detectors
            detectors = self._get_all_detectors()
            results = {}

            for detector in detectors:
                logger.info(f"🔍 Running {detector.get_name()} detector...")
                try:
                    smells = await detector.detect(neo_service)
                    results[detector.get_name()] = smells
                    logger.info(
                        f"✅ {detector.get_name()}: {len(smells)} smells detected")
                except Exception as e:
                    logger.error(f"❌ {detector.get_name()} failed: {e}")
                    results[detector.get_name()] = []

            # Generate report
            report = self._generate_report(results)
            logger.info("✅ Code smell analysis complete")

            return report

        except Exception as e:
            error_msg = f"❌ Error analyzing code smells: {e}"
            logger.error(error_msg)
            return error_msg

    @function
    async def analyze_specific_detector(
        self,
        detector_name: Annotated[str, Doc("Detector to run: 'circular', 'large', 'envy', 'dead', or 'shotgun'")],
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
    ) -> str:
        """Run a specific code smell detector."""
        logger = self._setup_logging()

        # Map detector names to classes
        detector_map = {
            'circular': CircularDependencyDetector(),
            'large': LargeClassDetector(),
            'envy': FeatureEnvyDetector(),
            'dead': DeadCodeDetector(),
            'shotgun': ShotgunSurgeryDetector(),
        }

        if detector_name not in detector_map:
            return f"❌ Unknown detector: {detector_name}. Available: {list(detector_map.keys())}"

        try:
            # Create Neo4j service
            neo_service: NeoService = dag.neo_service(
                self.config_file,
                password=neo_password,
                github_access_token=github_access_token,
                neo_auth=neo_auth,
                neo_data=self.neo_data
            )

            # Run specific detector
            detector = detector_map[detector_name]
            logger.info(f"🔍 Running {detector.get_name()} detector...")

            smells = await detector.detect(neo_service)

            if not smells:
                return f"✅ {detector.get_name()}: No code smells detected!"

            # Format results
            result_lines = [
                f"🔍 === {detector.get_name().upper()} ANALYSIS ===",
                f"📊 Found {len(smells)} issues:",
                ""
            ]

            for smell in smells:
                result_lines.extend([
                    f"⚠️  {smell}",
                    f"   💡 Recommendation: {smell.recommendation}",
                    ""
                ])

            return "\n".join(result_lines)

        except Exception as e:
            error_msg = f"❌ Error running {detector_name} detector: {e}"
            logger.error(error_msg)
            return error_msg
