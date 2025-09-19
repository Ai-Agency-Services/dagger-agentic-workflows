# Index Workflow Module Knowledge

## Purpose
Indexes codebases by processing files, extracting code structure, generating embeddings, and storing them in Supabase for semantic search.

## Architecture

### Core Class: `Index`
- **File Processing**: Concurrent file analysis and chunking
- **Embedding Generation**: OpenAI embeddings for semantic search
- **Database Storage**: Supabase integration for vector search
- **Symbol Extraction**: Code parsing and symbol relationship mapping

### Key Components
- **FileProcessor**: File filtering, validation, and chunking
- **EmbeddingHandler**: Batch embedding generation and storage
- **Neo4jService**: Graph database integration for relationships
- **ImportAnalyzer**: Analyzes file import dependencies

## Core Workflow

### 1. Repository Setup
```python
index = await Index.create(config_file, secrets...)
await index.index_codebase(
    repository_url="https://github.com/user/repo",
    branch="main",
    provider="openai"
)
```

### 2. File Processing Pipeline
1. **Filter Files**: Get processable files based on extensions
2. **Parse Code**: Extract symbols, imports, and structure
3. **Create Chunks**: Semantic or fixed-size chunks for embeddings
4. **Generate Embeddings**: OpenAI text-embedding-ada-002
5. **Store Data**: Insert chunks and embeddings into Supabase

### 3. Concurrent Processing
- Configurable concurrency limits via `ConcurrencyConfig`
- Semaphore-based rate limiting
- Batch processing for efficiency

## Configuration

### Required Config (`agencyservices.yaml`)
```yaml
indexing:
  batch_size: 50
  max_concurrent: 5
  embedding_batch_size: 100
  file_extensions: ["py", "js", "ts", "java", "go", "rs"]

supabase:
  url: https://your-project.supabase.co
```

### Processing Limits
- Default max concurrent: 5 files
- Batch size: 50 chunks per embedding request
- File size limits configurable
- Extension filtering with inclusion/exclusion lists

## File Processing Details

### Supported Languages
- Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, Ruby, PHP
- Language detection via file extension and content analysis
- Tree-sitter parsing for symbol extraction

### Chunking Strategies
1. **Semantic Chunking**: Symbol-based chunks with context
2. **Fixed-Size Chunking**: Fallback for unparseable files
3. **Symbol Sub-chunking**: Large symbols split with overlap

### Symbol Types
- Functions, Classes, Methods, Variables
- Import statements and dependencies
- Symbol relationships and references

## Database Schema

### Supabase Tables
- **`code_chunks`**: Stores text chunks with embeddings
- **Schema**: `id`, `filepath`, `content`, `language`, `start_line`, `end_line`, `embedding`

### Neo4j Integration
- Stores symbol relationships in graph database
- File imports and dependencies
- Symbol definitions and references

## Key Operations

### File Validation
```python
# Checks file size, extension, content
is_processable = _is_file_processable(filepath, content, config)
```

### Chunk Creation
```python
# Creates semantic chunks from symbols
chunks = _create_semantic_chunks(symbols, content, filepath)

# Fallback to fixed-size chunks
chunks = _create_fallback_chunks(content, filepath, chunk_size=1000)
```

### Embedding Storage
```python
# Batch generate embeddings
embeddings = await generate_embeddings_batch(chunk_texts)

# Store in Supabase with metadata
await store_chunks_with_embeddings(chunks, embeddings)
```

## Performance Optimizations

### Concurrency
- Semaphore-controlled concurrent file processing
- Async/await throughout for non-blocking operations
- Configurable limits prevent resource exhaustion

### Batching
- Embedding API calls batched for efficiency
- Database inserts optimized with bulk operations
- Chunk processing in configurable batch sizes

### Memory Management
- Large files processed in chunks
- Streaming file content when possible
- Cleanup of temporary data structures

## Error Handling

### File Processing Errors
- Parse failures logged but don't stop processing
- Malformed files skipped with warnings
- Partial success reporting

### API Failures
- Embedding generation retries
- Database connection resilience
- Graceful degradation when services unavailable

## Testing
- Unit tests: `workflows/index/tests/`
- Markers: `@pytest.mark.indexing`, `@pytest.mark.embedding`
- Mock embeddings and database clients for isolation

## Dependencies
- **Agent Utils**: Code parsing via Tree-sitter
- **Neo4j Service**: Graph database for relationships
- **OpenAI**: Embedding generation
- **Supabase**: Vector database storage

## Common Issues

### Rate Limiting
- OpenAI API rate limits may require backoff
- Adjust batch sizes and concurrency limits
- Monitor API usage and costs

### Memory Usage
- Large repositories may require chunking adjustments
- Monitor embedding storage size
- Consider file size limits

### Database Performance
- Supabase connection limits
- Bulk insert optimization
- Index performance on vector searches

## Integration Usage
- **Query Service**: Searches indexed embeddings
- **Research Agents**: Uses for codebase understanding
- **Code Analysis**: Foundation for semantic code queries