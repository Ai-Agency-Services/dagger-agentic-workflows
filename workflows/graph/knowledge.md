# Graph Workflow Module Knowledge

## Purpose
Builds comprehensive Neo4j graph representation of codebases, capturing files, symbols, imports, and relationships for structural analysis.

## Architecture

### Core Class: `Graph`
- **Graph Construction**: Transforms code into Neo4j graph database
- **Relationship Extraction**: Captures imports, calls, references between code elements
- **Concurrent Processing**: Handles large codebases efficiently
- **Cypher Generation**: Builds optimized database queries

## Core Workflow

### 1. Repository Processing
```python
graph = await Graph.create(config_file, secrets...)
result = await graph.build_graph_for_repository(
    repository_url="https://github.com/user/repo",
    branch="main"
)
```

### 2. File Processing Pipeline
1. **Parse Code**: Extract symbols, imports, structure via Tree-sitter
2. **Build Cypher**: Generate queries for files, symbols, relationships
3. **Execute Concurrently**: Batch query execution with rate limiting
4. **Extract Relationships**: Analyze symbol references and dependencies

## Key Functions

### Graph Building
- `build_graph_for_repository()`: Main entry point for repository processing
- `_build_graph_data_for_file()`: Processes individual files
- `_safe_build_graph_data_for_file()`: Error-wrapped file processing

### Cypher Query Generation
- `_build_file_cypher()`: Creates File nodes with metadata
- `_build_symbol_cypher()`: Creates symbol nodes (Function, Class, Variable)
- `_build_import_cypher()`: Creates import relationships between files
- `_build_relationship_cypher()`: Creates symbol-to-file relationships
- `_build_symbol_relationship_cypher()`: Creates symbol-to-symbol relationships

### Relationship Extraction
- `_extract_symbol_references()`: Finds function calls, variable usage
- `_resolve_relative_import()`: Resolves relative import paths
- `_find_containing_symbol()`: Determines symbol scope for references

### Concurrency Management
- `_execute_queries_concurrently()`: Parallel query execution
- `_execute_queries_in_concurrent_batches()`: Batched concurrent processing
- `execute_with_limit()`: Semaphore-controlled rate limiting

## Configuration

### Processing Config
```yaml
concurrency:
  max_concurrent: 3
indexing:
  file_extensions: ["py", "js", "ts", "java", "go", "rs"]
  exclude_patterns: ["test", "spec", "__pycache__"]
```

### Performance Settings
- **Concurrency**: 3 concurrent files (default)
- **Batch Size**: 1 query per batch (default)
- **File Filtering**: Extension-based inclusion/exclusion

## Graph Schema

### Node Types
- **File**: `filepath`, `language`, `size` properties
- **Function**: `name`, `start_line`, `end_line`, `docstring`, `signature`
- **Class**: `name`, `start_line`, `end_line`, `docstring`
- **Variable**: `name`, `line_number`, `scope`
- **Method**: Same as Function but within class scope

### Relationship Types
- **IMPORTS**: File-to-file import dependencies
- **DEFINED_IN**: Symbol-to-file containment
- **CALLS**: Function-to-function call relationships
- **REFERENCES**: Symbol-to-symbol references
- **CONTAINS**: Class-to-method containment

## Symbol Reference Detection

### Function Calls
- Regex pattern matching for function invocations
- Context-aware detection within symbol scopes
- Cross-file call relationship mapping

### Variable References
- Variable usage tracking within functions/classes
- Scope-aware reference resolution
- Assignment vs usage differentiation

### Import Resolution
- Relative import path resolution
- Multiple file extension attempts (.js, .ts, .py, etc.)
- Cross-directory import handling

## Query Execution Strategy

### Concurrent Processing
```python
# Process files with semaphore control
async with semaphore:
    result = await process_file(filepath)

# Execute queries in concurrent batches
for batch in query_batches:
    await asyncio.gather(*[execute_query(q) for q in batch])
```

### Error Handling
- Individual file failures don't stop processing
- Parse errors logged and skipped
- Partial success reporting with metrics

## String Escaping

### Cypher Injection Protection
```python
def _escape_cypher_string(text):
    return text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
```

### Property Handling
- All user content escaped before Cypher insertion
- JSON property extraction and application
- Safe handling of special characters

## Testing
- Unit tests: `workflows/graph/tests/`
- Coverage: `make test-workflows/graph-coverage`
- Markers: `@pytest.mark.graph`, `@pytest.mark.neo4j`

## Performance Considerations

### Memory Usage
- Large repositories require careful memory management
- File content streaming when possible
- Symbol map cleanup after processing

### Query Optimization
- Batch similar queries together
- Use MERGE for idempotent operations
- Index Neo4j properties for query performance

### Concurrency Tuning
- Adjust `max_concurrent` based on system resources
- Consider Neo4j connection limits
- Balance throughput vs resource usage

## Common Usage Patterns

### Full Repository Analysis
```python
# Complete graph building
result = await graph.build_graph_for_repository(repo_url, branch)
print(f"Processed {result['files_processed']} files")
print(f"Created {result['symbols_created']} symbols")
```

### Incremental Updates
- Process only changed files
- Update existing graph nodes
- Maintain referential integrity

## Integration Points
- **Neo Service**: Database operations and storage
- **Query Service**: Provides structural data for hybrid search
- **Smell Workflow**: Graph analysis for code smell detection
- **Agent Utils**: Code parsing and symbol extraction

## Troubleshooting

### Parse Failures
- Check Tree-sitter language support
- Verify file encoding and format
- Review file extension configuration

### Performance Issues
- Reduce concurrency limits
- Increase batch sizes for fewer API calls
- Monitor Neo4j memory usage

### Relationship Accuracy
- Review symbol reference patterns
- Check import resolution logic
- Validate cross-file relationships