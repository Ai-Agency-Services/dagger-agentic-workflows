# Cover Workflow Module Knowledge

## Purpose
Analyzes test coverage reports, extracts coverage data, and provides insights into code testing completeness using pluggable reporter architecture.

## Architecture

### Core Class: `Reporter`
- **Coverage Analysis**: Processes HTML coverage reports
- **Plugin System**: Supports Jest and Pytest reporters
- **Code Extraction**: Identifies code under test
- **Report Generation**: Creates structured coverage insights

### Plugin Architecture
- **Reporter Base**: Common interface for coverage analysis
- **Jest Plugin**: Handles Jest coverage reports
- **Pytest Plugin**: Processes Pytest coverage reports
- **Extensible**: Easy to add new testing framework support

## Core Functions

### Main Operations
- `get_coverage_reports()`: Finds and lists coverage report files
- `parse_test_results()`: Extracts test execution results
- `get_code_under_test()`: Identifies tested code files
- `get_coverage_html()`: Retrieves coverage report content

### Plugin-Specific Methods
- `create_coverage_reports()`: Generates coverage analysis
- `extract_and_process_report()`: Processes framework-specific reports

## Workflow Process

### 1. Coverage Report Discovery
```python
reporter = await dag.reporter(config_file)
reports = await reporter.get_coverage_reports(container)
```

### 2. Report Processing
- Locates HTML coverage files (`index.html`, `lcov-report/index.html`)
- Extracts coverage percentages and metrics
- Identifies uncovered code sections
- Maps coverage to source files

### 3. Code Analysis
- Scans tested code files
- Analyzes coverage patterns
- Identifies testing gaps
- Generates improvement recommendations

## Plugin Implementations

### Jest Reporter Plugin
- **Coverage Files**: `coverage/lcov-report/index.html`
- **Test Results**: `test-results.json`, `jest-results.json`
- **Metrics**: Line, branch, function, statement coverage

### Pytest Reporter Plugin
- **Coverage Files**: `htmlcov/index.html`
- **Test Results**: `pytest-results.xml`, `.coverage`
- **Metrics**: Line and branch coverage analysis

## Configuration

### Reporter Config
```yaml
reporter:
  framework: "jest"  # or "pytest"
  coverage_threshold: 80
  output_format: "detailed"
```

### Plugin Selection
- Automatic framework detection
- Manual override via configuration
- Support for mixed testing environments

## Coverage Data Extraction

### HTML Parsing
```python
# Extract coverage data from HTML tables
def extract_coverage_data_from_table(html_content):
    # Parse coverage percentages
    # Extract file paths and metrics
    # Return structured coverage data
```

### Metrics Collected
- **Line Coverage**: Percentage of lines executed
- **Branch Coverage**: Conditional branch execution
- **Function Coverage**: Function call coverage
- **Statement Coverage**: Statement execution rates

## File Analysis

### Code Under Test Discovery
```python
# Find source files being tested
code_files = await get_code_under_test(container)

# Analyze file structure and organization
for file_path in code_files:
    content = await parse_code(file_path)
    # Extract functions, classes, complexity
```

### Test File Identification
- Distinguishes test files from source code
- Maps test files to their target source files
- Analyzes test coverage distribution

## Report Generation

### Coverage Insights
- Overall coverage percentage
- Per-file coverage breakdown
- Uncovered code identification
- Testing gap analysis

### Recommendations
- Priority areas for additional testing
- Complex code requiring more coverage
- Untested critical functionality

## Utility Functions

### File Operations
```python
# Find coverage report files
index_files = find_index_html_files(container)

# Parse code structure
code_structure = parse_code(file_content, language)
```

### Data Processing
- Coverage percentage calculation
- Report format standardization
- Metric aggregation across files

## Testing
- Unit tests: `workflows/cover/tests/`
- Plugin tests: `workflows/cover/plugins/reporter/*/tests/`
- Markers: `@pytest.mark.coverage`
- Mock HTML reports for testing

## Dependencies

### External Tools
- **Testing Frameworks**: Jest, Pytest, etc.
- **Coverage Tools**: Built-in framework coverage
- **HTML Parsing**: BeautifulSoup or similar

### Internal Dependencies
- **Agent Utils**: Code parsing utilities
- **YAML Config**: Configuration management
- **Dagger Engine**: Container operations

## Plugin Development

### Creating New Plugins
1. Inherit from base reporter interface
2. Implement framework-specific parsing logic
3. Handle coverage file format variations
4. Add plugin to reporter dispatcher

### Plugin Interface
```python
class CustomReporterPlugin:
    async def create_coverage_reports(self, container):
        # Implementation specific to framework
        pass
    
    async def get_coverage_html(self, container):
        # Return coverage HTML content
        pass
```

## Integration Points
- **CI/CD Pipelines**: Automated coverage analysis
- **Quality Gates**: Coverage threshold enforcement
- **Development Workflows**: Coverage-driven development
- **Code Review**: Coverage impact analysis

## Common Issues

### Report Location
- Different frameworks use different output paths
- Configuration affects report generation location
- Container path mapping considerations

### Format Variations
- HTML structure differences between versions
- Metric calculation variations
- Parser robustness requirements

### Performance
- Large coverage reports may require streaming
- HTML parsing memory usage
- Container resource limitations