# Smell Detection Workflow Module Knowledge

## Purpose
Detects code smells and anti-patterns using Neo4j graph analysis, providing automated code quality assessment and improvement recommendations.

## Architecture

### Core Class: `Smell`
- **Detector Orchestration**: Manages multiple code smell detectors
- **Concurrent Analysis**: Runs detectors in parallel for efficiency
- **Report Generation**: Formats results with severity and recommendations

### Code Smell Framework
- **SmellSeverity**: Enum for LOW, MEDIUM, HIGH, CRITICAL levels
- **CodeSmell**: Dataclass with name, description, severity, location, metrics, recommendation
- **BaseDetector**: Abstract base for all smell detectors

## Available Detectors

### Structural Smells
- **CircularDependencyDetector**: Finds circular import chains
- **LargeClassDetector**: Files with many symbols (SRP risk)
- **LargeClassByLinesDetector**: Classes exceeding lines of code threshold (true Large Class)
- **LongFunctionDetector**: Functions exceeding length limits (>50 lines)
- **LongParameterListDetector**: Functions/methods with many parameters (>=6)
- **DeepDependencyChainDetector**: Long dependency chains
- **MutualDependencyDetector**: Bidirectional imports between files (A imports B and B imports A)

### Coupling Smells
- **HighFanOutDetector**: Symbols with too many outgoing dependencies (>15)
- **HighFanInDetector**: Symbols with too many incoming dependencies (>10)
- **FeatureEnvyDetector**: Classes accessing external data excessively
- **FeatureEnvyAdvancedDetector**: Methods calling external files more than their own (uses cross-file CALLS/REFERENCES)
- **ShotgunSurgeryDetector**: Changes requiring modifications across many files
- **HubModuleDetector**: High afferent and efferent coupling on the same file (hub risk)

### Design Smells
- **GodComponentDetector**: Files with excessive complexity (>10 imports + >30 symbols)
- **GodClassByMethodsDetector**: Classes with too many methods (uses Method.parent and filepath)
- **DeadCodeDetector**: Unreferenced functions/classes/interfaces/methods (no incoming CALLS/REFERENCES)
- **OrphanModuleDetector**: Files with no relationships
- **DuplicateSymbolDetector**: Multiple symbols with same name
- **MessageChainDetector**: Methods with long CALLS chains across functions (3+ length)
- **LawOfDemeterDetector**: Methods that talk to many distinct external files/modules (>=3)

### Architectural Smells
- **CrossDirectoryCouplingDetector**: Excessive cross-directory dependencies
- **BarrelFileDetector**: Files that only re-export other modules
- **InstabilityDetector**: Unstable modules (high efferent coupling)

## Detector Implementation

### Base Pattern
```python
class CustomDetector(CodeSmellDetector):
    def get_name(self) -> str:
        ...
    async def detect(self, neo_service) -> List[CodeSmell]:
        result = await neo_service.run_query(cypher_query)
        return smells
```

### Query Patterns
- Prefer graph relationships over raw properties for robustness
- Use IMPORTS for coupling; CALLS/REFERENCES for usage
- Aggregate with counts and thresholds; limit results

## Notable Query Improvements

### Dead Code (revised)
- Rationale: Property `scope` may be missing; use relationships
- Query core (avoid label alternation and use relationship alternation):
```cypher
MATCH (symbol)-[:DEFINED_IN]->(f:File)
WHERE any(l IN labels(symbol) WHERE l IN ['Function','Class','Interface','Method'])
AND NOT EXISTS {
  MATCH (caller)-[:CALLS|REFERENCES]->(symbol)
  WHERE any(l IN labels(caller) WHERE l IN ['Function','Method','Class','Variable'])
}
AND NOT f.filepath CONTAINS "test"
RETURN symbol.name, labels(symbol)[0], f.filepath
LIMIT 25
```

### Mutual Dependencies
```cypher
MATCH (a:File)-[:IMPORTS]->(b:File)
MATCH (b)-[:IMPORTS]->(a)
WHERE a <> b
RETURN a.filepath, b.filepath
LIMIT 30
```

### Hub Modules
```cypher
MATCH (f:File)
OPTIONAL MATCH (f)-[:IMPORTS]->(dep:File)
WITH f, count(DISTINCT dep) AS fan_out
OPTIONAL MATCH (imp:File)-[:IMPORTS]->(f)
WITH f, fan_out, count(DISTINCT imp) AS fan_in
WHERE fan_in >= 15 AND fan_out >= 15
RETURN f.filepath, fan_in, fan_out
ORDER BY (fan_in + fan_out) DESC
LIMIT 20
```

## Usage Examples

### Full Analysis
```python
smell = await Smell.create(config_file, secrets...)
report = await smell.analyze_codebase()
```

### Specific Detector
```python
report = await smell.analyze_specific_detector("circular")
```

### Multiple Detectors
```python
report = await smell.analyze_multiple_detectors(["large", "long", "dead"])
```

## Configuration

### Concurrency Settings
```yaml
concurrency:
  max_concurrent: 3
```

### Threshold Customization
- Large class: >100 lines
- Long function: >50 lines
- High fan-out: >15 dependencies
- High fan-in: >10 dependents
- Hub module: fan_in >= 15 and fan_out >= 15

## Report Format
- Summary with totals and severity mix
- Critical/High section prioritized
- Per-issue recommendation tips
- GitHub file links when git.repo_url is configured
- Detailed findings are included by default

### GitHub Links and Detailed Findings
- Add this to your smell YAML config to enable links:
```yaml
git:
  repo_url: https://github.com/org/repo
  branch: main
```
- Reports always include detailed findings when links are available.
```python
# Standard usage
report = await smell.analyze_codebase()
# Specific detector
report = await smell.analyze_specific_detector("circular")
# Multiple detectors
report = await smell.analyze_multiple_detectors(["large", "dead"])
```
- Link pattern: https://github.com/org/repo/blob/<branch>/<filepath>

## Performance Considerations
- Ensure indexes/constraints exist (File.filepath unique, Function/Class/Variable/Method unique keys)
- Prefer DISTINCT for counts
- Limit result sets

## Integration Points
- Built on Graph workflow’s File/Function/Class/Variable/Method nodes; IMPORTS, DEFINED_IN, CALLS, REFERENCES
- Cross-file symbol resolution enabled (imports -> cross-file CALLS/REFERENCES)
- Neo Service runs Cypher; smell workflow orchestrates and reports
