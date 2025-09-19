# Query Service Module Knowledge

## Purpose
Unified interface combining semantic search (vector embeddings) with structural code queries (Neo4j graph) for comprehensive code understanding.

## Architecture

### Hybrid Search Approach
- **Semantic Search**: Supabase + OpenAI embeddings for meaning-based queries
- **Structural Queries**: Neo4j graph for code structure and relationships
- **Unified Results**: Combines both approaches for comprehensive answers

### Core Class: `QueryService`
- **Configuration**: Cache settings, parallel processing, embedding dimensions
- **Database Clients**: Supabase and OpenAI client management
- **Result Processing**: Formatting and combining multi-source results

## Core Functions

### Public API
- `query()`: Main entry point - combines semantic + structural search
- `search()`: Semantic-only search using vector embeddings
- `get_structural()`: Structure-only queries via Neo4j
- `debug_query()`: Detailed debugging with timing and intermediate results

### Internal Methods
- `_semantic_search()`: Supabase vector search with OpenAI embeddings
- `_get_structural_data()`: Neo4j queries for symbols, imports, references
- `_parse_cypher_result()`: Parses Neo4j query results into structured data
- `_format_result()`: Combines and formats final results

### Utility Functions
- `invalidate_cache()`: Cache management for specific files or global
- `get_file_details()`: Basic file information
- `log_last_query()`: Query logging for debugging

## Configuration

### Required Config (`agencyservices.yaml`)
```yaml
integration:
  cache_enabled: true
  cache_ttl: 3600
  parallel_processing: true
  embedding_dimension: 1536
supabase:
  url: https://your-project.supabase.co
```

### Default Values
- Cache TTL: 3600 seconds
- Embedding dimension: 1536 (OpenAI default)
- Parallel processing: enabled
- Cache: enabled

## Query Workflow

### 1. Semantic Search Phase
```python
# Generate embedding for query
embedding = await openai.embeddings.create(
    input=query_text,
    model="text-embedding-ada-002"
)

# Search Supabase vector database
results = supabase.rpc("semantic_search", {
    "query_embedding": embedding,
    "match_threshold": threshold,
    "match_count": limit
})
```

### 2. Structural Query Phase
```python
# Extract relevant files from semantic results
file_paths = [r["filepath"] for r in semantic_results]

# Query Neo4j for structural data
symbols = await neo_service.run_query(symbol_query)
imports = await neo_service.run_query(import_query)
references = await neo_service.run_query(reference_query)
```

### 3. Result Combination
- Merges semantic and structural results
- Provides context from both meaning and structure
- Formats for human-readable output

## Dependencies

### External Services
- **Supabase**: Vector database with `semantic_search` RPC function
- **OpenAI API**: Embedding generation via `text-embedding-ada-002`
- **Neo4j**: Graph database via `NeoService`

### Internal Dependencies
- **Neo Service**: For structural queries
- **Agent Utils**: Code parsing utilities
- **YAML Config**: Configuration management

## Performance Features

### Caching
- Query result caching with configurable TTL
- File-specific cache invalidation
- Global cache clearing capability

### Parallel Processing
- Concurrent semantic and structural queries
- Configurable via `parallel_processing` flag
- Timing measurement for performance monitoring

### Error Handling
- Graceful fallback when services unavailable
- Detailed error logging
- Partial results returned when possible

## Testing
- Unit tests: `services/query/tests/`
- Markers: `@pytest.mark.llm` for API-dependent tests
- Mocking: Supabase and OpenAI clients mocked for isolation

## Usage Examples

### Basic Query
```python
result = await query_service.query(
    "find authentication functions",
    threshold=0.7,
    limit=10,
    include_structure=True
)
```

### Semantic Search Only
```python
result = await query_service.search(
    "error handling patterns",
    threshold=0.8,
    limit=5
)
```

### Debug Query
```python
debug_info = await query_service.debug_query(
    "database connections",
    threshold=0.6,
    limit=15,
    include_structure=True,
    format="json"
)
```

## Integration Points
- **Index Workflow**: Provides embeddings for semantic search
- **Graph Workflow**: Provides structural data via Neo4j
- **Codebuff Agents**: Uses for code understanding and context
- **Research Agents**: Leverages for codebase exploration

## Key Implementation Notes

### Result Format
- Semantic results include similarity scores and file context
- Structural data includes symbols, imports, and references
- Combined format provides comprehensive code understanding

### API Key Management
- Supports both OpenAI and OpenRouter for embeddings
- Secure handling via Dagger secrets
- Provider selection based on available keys

### Query Optimization
- File path filtering for relevant structural queries
- Threshold-based result filtering
- Configurable result limits