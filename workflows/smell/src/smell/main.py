import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Dict, List, Optional

import anyio  # Added for concurrency
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


# TODO:One of the property names in your query is not available in the database,
# make sure you didn't misspell it or that the label is available when you run this statement in your application
# (the missing property name is: scope)
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


class HighFanOutDetector(CodeSmellDetector):
    """Modules that depend on many files (high efferent coupling)"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (f)-[:IMPORTS]->(dep:File)
        WITH f, count(DISTINCT dep) AS fan_out
        WHERE fan_out > 12
        RETURN f.filepath AS file, fan_out
        ORDER BY fan_out DESC
        LIMIT 20
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                filepath = parts[0].strip('"')
                fan_out = int(parts[1]) if parts[1].isdigit() else 0
                sev = SmellSeverity.HIGH if fan_out >= 20 else SmellSeverity.MEDIUM
                smells.append(CodeSmell(
                    name="High Fan-Out",
                    description=f"Imports {fan_out} files (high efferent coupling)",
                    severity=sev,
                    location=filepath,
                    metrics={"fan_out": fan_out},
                    recommendation="Reduce dependencies via inversion/abstractions or split module"
                ))
        return smells

    def get_name(self) -> str:
        return "High Fan-Out"


class HighFanInDetector(CodeSmellDetector):
    """Modules that many other files depend on (high afferent coupling)"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (imp:File)-[:IMPORTS]->(f)
        WITH f, count(DISTINCT imp) AS fan_in
        WHERE fan_in > 12
        RETURN f.filepath AS file, fan_in
        ORDER BY fan_in DESC
        LIMIT 20
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                filepath = parts[0].strip('"')
                fan_in = int(parts[1]) if parts[1].isdigit() else 0
                sev = SmellSeverity.CRITICAL if fan_in >= 30 else SmellSeverity.HIGH
                smells.append(CodeSmell(
                    name="High Fan-In",
                    description=f"Imported by {fan_in} files (unstable dependency)",
                    severity=sev,
                    location=filepath,
                    metrics={"fan_in": fan_in},
                    recommendation="Introduce a Facade or split responsibilities to reduce inbound deps"
                ))
        return smells

    def get_name(self) -> str:
        return "High Fan-In"


class InstabilityDetector(CodeSmellDetector):
    """Instability metric = fan_out / (fan_in + fan_out)"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (f)-[:IMPORTS]->(o:File)
        WITH f, count(DISTINCT o) AS fan_out
        OPTIONAL MATCH (i:File)-[:IMPORTS]->(f)
        WITH f, fan_out, count(DISTINCT i) AS fan_in
        WITH f, fan_in, fan_out,
             CASE WHEN fan_in + fan_out = 0 THEN 0.0
                  ELSE toFloat(fan_out) / (fan_in + fan_out) END AS instability
        WHERE fan_out > 0 OR fan_in > 0
        RETURN f.filepath AS file, fan_in, fan_out, round(instability, 2) AS instability
        ORDER BY instability DESC, fan_out DESC
        LIMIT 20
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 4:
                filepath = parts[0].strip('"')
                fan_in = int(parts[1]) if parts[1].isdigit() else 0
                fan_out = int(parts[2]) if parts[2].isdigit() else 0
                try:
                    instability = float(parts[3])
                except Exception:
                    instability = 0.0
                sev = SmellSeverity.HIGH if instability >= 0.8 and fan_out >= 8 else SmellSeverity.MEDIUM
                smells.append(CodeSmell(
                    name="High Instability",
                    description=f"Instability={instability} (fan_in={fan_in}, fan_out={fan_out})",
                    severity=sev,
                    location=filepath,
                    metrics={"fan_in": fan_in, "fan_out": fan_out,
                             "instability": instability},
                    recommendation="Reduce outward deps or increase inbound reuse to stabilize"
                ))
        return smells

    def get_name(self) -> str:
        return "Instability"


class LongFunctionDetector(CodeSmellDetector):
    """Functions/methods with large line spans"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        threshold = 120
        query = f"""
        MATCH (fn)-[:DEFINED_IN]->(f:File)
        WHERE (fn:Function OR fn:Method)
        WITH fn, f, coalesce(fn.end_line, -1) - coalesce(fn.start_line, 0) AS span
        WHERE span >= {threshold}
        RETURN f.filepath AS file, fn.name AS symbol, labels(fn)[0] AS kind, span
        ORDER BY span DESC
        LIMIT 50
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 4:
                filepath = parts[0].strip('"')
                symbol = parts[1].strip('"')
                kind = parts[2].strip('"')
                try:
                    span = int(parts[3])
                except Exception:
                    span = threshold
                sev = SmellSeverity.CRITICAL if span >= 300 else SmellSeverity.HIGH if span >= 180 else SmellSeverity.MEDIUM
                smells.append(CodeSmell(
                    name="Long Function/Method",
                    description=f"{kind} '{symbol}' spans {span} lines",
                    severity=sev,
                    location=filepath,
                    metrics={"span": span, "symbol": symbol, "kind": kind},
                    recommendation="Extract smaller functions and reduce complexity"
                ))
        return smells

    def get_name(self) -> str:
        return "Long Functions"


class DeepDependencyChainDetector(CodeSmellDetector):
    """Files with very deep import chains"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        min_depth = 6
        query = f"""
        MATCH p = (a:File)-[:IMPORTS*1..12]->(:File)
        WITH a, max(length(p)) AS max_len
        WHERE max_len >= {min_depth}
        RETURN a.filepath AS file, max_len
        ORDER BY max_len DESC
        LIMIT 20
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                filepath = parts[0].strip('"')
                depth = int(parts[1]) if parts[1].isdigit() else min_depth
                sev = SmellSeverity.HIGH if depth >= 10 else SmellSeverity.MEDIUM
                smells.append(CodeSmell(
                    name="Deep Dependency Chain",
                    description=f"Max import chain depth {depth}",
                    severity=sev,
                    location=filepath,
                    metrics={"max_chain_depth": depth},
                    recommendation="Flatten layers or introduce boundaries to shorten chains"
                ))
        return smells

    def get_name(self) -> str:
        return "Deep Dependency Chains"


class OrphanModuleDetector(CodeSmellDetector):
    """Files with no imports in or out"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        query = """
        MATCH (f:File)
        WHERE NOT (f)-[:IMPORTS]->(:File)
          AND NOT (:File)-[:IMPORTS]->(f)
        RETURN f.filepath AS file
        LIMIT 50
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            filepath = line.split()[0].strip('"')
            smells.append(CodeSmell(
                name="Orphan Module",
                description="No imports in or out; may be unused or a utility missing integration",
                severity=SmellSeverity.MEDIUM,
                location=filepath,
                metrics={},
                recommendation="Delete if unused or integrate via an explicit interface"
            ))
        return smells

    def get_name(self) -> str:
        return "Orphan Modules"


class BarrelFileDetector(CodeSmellDetector):
    """Barrel files: many re-exports/imports but few symbols defined locally"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        query = """
        MATCH (f:File)
        OPTIONAL MATCH (f)-[:IMPORTS]->(dep:File)
        WITH f, count(DISTINCT dep) AS fan_out
        OPTIONAL MATCH (s)-[:DEFINED_IN]->(f)
        WHERE s:Function OR s:Class OR s:Variable OR s:Interface OR s:Method
        WITH f, fan_out, count(DISTINCT s) AS symbols
        WHERE fan_out >= 10 AND symbols <= 1
        RETURN f.filepath AS file, fan_out, symbols
        ORDER BY fan_out DESC
        LIMIT 20
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 3:
                filepath = parts[0].strip('"')
                fan_out = int(parts[1]) if parts[1].isdigit() else 0
                symbols = int(parts[2]) if parts[2].isdigit() else 0
                sev = SmellSeverity.MEDIUM if fan_out >= 10 else SmellSeverity.LOW
                smells.append(CodeSmell(
                    name="Barrel File",
                    description=f"Re-exports/imports {fan_out} files but defines {symbols} symbols",
                    severity=sev,
                    location=filepath,
                    metrics={"fan_out": fan_out, "symbols": symbols},
                    recommendation="Keep barrels tiny; avoid adding logic or many indirections"
                ))
        return smells

    def get_name(self) -> str:
        return "Barrel Files"


class DuplicateSymbolDetector(CodeSmellDetector):
    """Colliding symbol names across files"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        query = """
        MATCH (s)-[:DEFINED_IN]->(f:File)
        WITH s.name AS name, head(labels(s)) AS kind, collect(DISTINCT f.filepath) AS files
        WHERE size(files) > 1 AND name IS NOT NULL AND name <> ""
        RETURN name, kind, size(files) AS occurrences
        ORDER BY occurrences DESC
        LIMIT 25
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 3:
                name = parts[0].strip('"')
                kind = parts[1].strip('"')
                occ = int(parts[2]) if parts[2].isdigit() else 2
                sev = SmellSeverity.HIGH if occ >= 4 else SmellSeverity.MEDIUM
                smells.append(CodeSmell(
                    name="Duplicate Symbol",
                    description=f"Symbol '{name}' ({kind}) appears in {occ} files",
                    severity=sev,
                    location="Multiple files",
                    metrics={"occurrences": occ, "symbol": name, "kind": kind},
                    recommendation="Rename or consolidate to avoid ambiguity and shadowing"
                ))
        return smells

    def get_name(self) -> str:
        return "Duplicate Symbols"


class GodComponentDetector(CodeSmellDetector):
    """TSX/JSX components with many functions (likely too much responsibility)"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        threshold = 6
        query = """
        MATCH (f:File)
        WHERE f.filepath ENDS WITH ".tsx" OR f.filepath ENDS WITH ".jsx"
        OPTIONAL MATCH (fn:Function)-[:DEFINED_IN]->(f)
        WITH f, count(fn) AS functions
        WHERE functions >= 6
        RETURN f.filepath AS file, functions
        ORDER BY functions DESC
        LIMIT 20
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                filepath = parts[0].strip('"')
                fcount = int(parts[1]) if parts[1].isdigit() else threshold
                sev = SmellSeverity.HIGH if fcount >= 10 else SmellSeverity.MEDIUM
                smells.append(CodeSmell(
                    name="God Component",
                    description=f"Contains {fcount} functions; likely multiple responsibilities",
                    severity=sev,
                    location=filepath,
                    metrics={"function_count": fcount},
                    recommendation="Extract smaller components/hooks for clearer responsibilities"
                ))
        return smells

    def get_name(self) -> str:
        return "God Components"


class CrossDirectoryCouplingDetector(CodeSmellDetector):
    """Files importing broadly across many feature folders"""

    async def detect(self, neo_service: NeoService) -> List[CodeSmell]:
        query = """
        MATCH (a:File)-[:IMPORTS]->(b:File)
        WITH a, b, split(a.filepath,"/") AS ap, split(b.filepath,"/") AS bp
        WITH a,
             (CASE WHEN size(ap) > 3 THEN ap[3] ELSE ap[size(ap)-2] END) AS a_dir,
             (CASE WHEN size(bp) > 3 THEN bp[3] ELSE bp[size(bp)-2] END) AS b_dir
        WHERE a_dir IS NOT NULL AND b_dir IS NOT NULL AND a_dir <> b_dir
        WITH a, collect(DISTINCT b_dir) AS dirs
        WITH a, size(dirs) AS distinct_dirs
        WHERE distinct_dirs >= 3
        RETURN a.filepath AS file, distinct_dirs
        ORDER BY distinct_dirs DESC
        LIMIT 20
        """
        result = await neo_service.run_query(query)
        smells: List[CodeSmell] = []
        lines = [l.strip() for l in result.strip().split("\n") if l.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                filepath = parts[0].strip('"')
                dirs = int(parts[1]) if parts[1].isdigit() else 3
                sev = SmellSeverity.MEDIUM if dirs >= 3 else SmellSeverity.LOW
                smells.append(CodeSmell(
                    name="Cross-Directory Coupling",
                    description=f"Imports from {dirs} distinct directories",
                    severity=sev,
                    location=filepath,
                    metrics={"distinct_dirs": dirs},
                    recommendation="Align imports to a stable boundary or reduce cross-feature coupling"
                ))
        return smells

    def get_name(self) -> str:
        return "Cross-Directory Coupling"


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

    def _get_concurrency_config(self) -> dict:
        """Extract concurrency configuration from YAML config."""
        config_obj = YAMLConfig(
            **self.config) if isinstance(self.config, dict) else self.config

        # Check for concurrency config first, fall back to defaults
        concurrency_config = getattr(config_obj, 'concurrency', None)

        return {
            'max_concurrent': getattr(concurrency_config, 'max_concurrent', 3) if concurrency_config else 3,
        }

    def _get_all_detectors(self) -> List[CodeSmellDetector]:
        """Get all available code smell detectors"""
        return [
            CircularDependencyDetector(),
            LargeClassDetector(),
            FeatureEnvyDetector(),
            DeadCodeDetector(),
            ShotgunSurgeryDetector(),
            HighFanOutDetector(),
            HighFanInDetector(),
            InstabilityDetector(),
            LongFunctionDetector(),
            DeepDependencyChainDetector(),
            OrphanModuleDetector(),
            BarrelFileDetector(),
            DuplicateSymbolDetector(),
            GodComponentDetector(),
            CrossDirectoryCouplingDetector(),
        ]

    async def _run_detectors_concurrently(
        self,
        detectors: List[CodeSmellDetector],
        neo_service: NeoService,
        logger: logging.Logger,
        max_concurrent: int = 3
    ) -> Dict[str, List[CodeSmell]]:
        """Run all detectors concurrently with controlled concurrency."""
        if not detectors:
            return {}

        semaphore = anyio.Semaphore(max_concurrent)
        results = {}

        async def run_detector_with_limit(detector: CodeSmellDetector):
            async with semaphore:
                detector_name = detector.get_name()
                try:
                    logger.info(f"🔍 Running {detector_name} detector...")
                    smells = await detector.detect(neo_service)
                    logger.info(
                        f"✅ {detector_name}: {len(smells)} smells detected")
                    return detector_name, smells
                except Exception as e:
                    logger.error(f"❌ {detector_name} failed: {e}")
                    return detector_name, []

        # Use anyio task group for concurrent execution
        async with anyio.create_task_group() as tg:
            detector_tasks = []

            async def collect_result(detector: CodeSmellDetector):
                result = await run_detector_with_limit(detector)
                results[result[0]] = result[1]

            for detector in detectors:
                tg.start_soon(collect_result, detector)

        logger.info(f"Completed all {len(detectors)} detectors concurrently")
        return results

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
        """Analyze codebase for code smells using Clean Code principles with concurrent execution."""
        logger = self._setup_logging()
        concurrency_config = self._get_concurrency_config()
        logger.info("Starting concurrent code smell analysis")

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

            # Get all detectors
            detectors = self._get_all_detectors()
            logger.info(
                f"Running {len(detectors)} detectors concurrently with max_concurrent={concurrency_config['max_concurrent']}")

            # Run all detectors concurrently
            results = await self._run_detectors_concurrently(
                detectors=detectors,
                neo_service=neo_service,
                logger=logger,
                max_concurrent=concurrency_config['max_concurrent']
            )

            # Generate report
            report = self._generate_report(results)
            logger.info("✅ Concurrent code smell analysis complete")

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

    @function
    async def analyze_multiple_detectors(
        self,
        detector_names: Annotated[List[str], Doc("List of detectors to run: 'circular', 'large', 'envy', 'dead', 'shotgun'")],
        github_access_token: Annotated[dagger.Secret, Doc("GitHub access token")],
        neo_password: Annotated[dagger.Secret, Doc("Neo4j password")],
        neo_auth: Annotated[dagger.Secret, Doc("Neo4j auth token")],
    ) -> str:
        """Run multiple specific detectors concurrently."""
        logger = self._setup_logging()
        concurrency_config = self._get_concurrency_config()

        # Map detector names to classes
        detector_map = {
            'circular': CircularDependencyDetector(),
            'large': LargeClassDetector(),
            'envy': FeatureEnvyDetector(),
            'dead': DeadCodeDetector(),
            'shotgun': ShotgunSurgeryDetector(),
        }

        # Validate detector names
        invalid_detectors = [
            name for name in detector_names if name not in detector_map]
        if invalid_detectors:
            return f"❌ Unknown detectors: {invalid_detectors}. Available: {list(detector_map.keys())}"

        try:
            # Create Neo4j service
            neo_service: NeoService = dag.neo_service(
                self.config_file,
                password=neo_password,
                github_access_token=github_access_token,
                neo_auth=neo_auth,
                neo_data=self.neo_data
            )

            # Get selected detectors
            selected_detectors = [detector_map[name]
                                  for name in detector_names]
            logger.info(
                f"Running {len(selected_detectors)} selected detectors concurrently")

            # Run detectors concurrently
            results = await self._run_detectors_concurrently(
                detectors=selected_detectors,
                neo_service=neo_service,
                logger=logger,
                max_concurrent=concurrency_config['max_concurrent']
            )

            # Generate focused report
            total_smells = sum(len(smells) for smells in results.values())

            if total_smells == 0:
                return f"✅ No code smells detected by selected detectors: {', '.join(detector_names)}"

            result_lines = [
                f"🔍 === SELECTED DETECTORS ANALYSIS ===",
                f"📊 Detectors: {', '.join(detector_names)}",
                f"📊 Total Issues Found: {total_smells}",
                ""
            ]

            for category, smells in results.items():
                if smells:
                    result_lines.extend([
                        f"=== {category.upper()} ===",
                        f"Found {len(smells)} issues:",
                        ""
                    ])

                    for smell in smells:
                        result_lines.extend([
                            f"⚠️  {smell}",
                            f"   💡 Recommendation: {smell.recommendation}",
                            ""
                        ])

            return "\n".join(result_lines)

        except Exception as e:
            error_msg = f"❌ Error running selected detectors: {e}"
            logger.error(error_msg)
            return error_msg
