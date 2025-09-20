# Agent Utils Shared Module Knowledge

## Purpose
Provides common code parsing utilities using Tree-sitter for extracting structured information from source code across multiple programming languages.

## Architecture

### Core Class: `AgentUtils`
- **Multi-Language Parsing**: Tree-sitter integration for various languages
- **Symbol Extraction**: Functions, classes, variables, imports
- **Structured Output**: JSON format for agent consumption
- **Language Detection**: Automatic programming language identification

## Core Functions

### Main API
- `parse_code_file_to_json(content, filepath, ignore_dirs=None)`: Primary entry point for code parsing; when `ignore_dirs` contains any directory segment present in `filepath`, parsing is skipped and an empty result is returned immediately.
- `detect_language()`: Identifies programming language from file extension
- `_parse_with_tree_sitter()`: Internal Tree-sitter parsing logic

### Helper Functions
- `_get_file_extension()`: Extracts file extension for language detection
- `_generate_parser_script()`: Creates language-specific parsing scripts

## Supported Languages

### Currently Supported
- **Python**: Functions, classes, methods, variables, imports
- **JavaScript/TypeScript**: Functions, classes, variables, imports
- **Java**: Classes, methods, fields, imports
- **Go**: Functions, types, variables, imports
- **Rust**: Functions, structs, enums, use statements
- **C/C++**: Functions, structs, variables, includes

### Language Detection
```python
LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript", 
    ".ts": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c", 
    ".cpp": "cpp",
    ".h": "c"
}
```

## Output Format

### JSON Structure
```json
{
  "language": "python",
  "symbols": [
    {
      "name": "function_name",
      "type": "function",
      "line_number": 10,
      "end_line_number": 20,
      "docstring": "Function description",
      "scope": "global"
    }
  ],
  "imports": [
    "os",
    "sys", 
    "./relative_module"
  ]
}
```

### Symbol Types
- **function**: Standalone functions
- **class**: Class definitions
- **method**: Class methods
- **variable**: Global and local variables
- **constant**: Constants and configuration

## Tree-sitter Integration

### Parser Installation
- Language parsers loaded dynamically
- Grammar files for syntax tree generation
- Query patterns for symbol extraction

### Query Patterns
```python
# Python function extraction
function_query = """
(function_definition
  name: (identifier) @name
  body: (block) @body
) @function
"""

# Import extraction  
import_query = """
(import_statement
  name: (dotted_name) @import
) @import_stmt
"""
```

## Usage Patterns

### Basic Code Parsing
```python
utils = await dag.agent_utils()
result = await utils.parse_code_file_to_json(
    filepath="src/main.py",
    file_content=code_content
)

# Access parsed data
code_data = json.loads(await result.contents())
symbols = code_data["symbols"]
imports = code_data["imports"]
```

### Language-Specific Processing
```python
language = detect_language("example.py")  # Returns "python"
if language == "python":
    # Python-specific symbol extraction
elif language == "javascript":
    # JavaScript-specific processing
```

## Symbol Extraction Details

### Function Analysis
- **Name**: Function identifier
- **Parameters**: Function arguments and types
- **Return Type**: Return type annotations (when available)
- **Docstring**: Documentation strings
- **Decorators**: Python decorators, annotations

### Class Analysis
- **Name**: Class identifier
- **Inheritance**: Parent classes and interfaces
- **Methods**: Class method definitions
- **Properties**: Class attributes and properties
- **Docstring**: Class documentation

### Import Analysis
- **Module Names**: Imported module identifiers
- **Import Types**: from/import distinctions
- **Relative Imports**: Local module references
- **Alias Handling**: Import aliases and renaming

## Error Handling

### Parse Failures
- Invalid syntax handling
- Partial parsing recovery
- Language detection fallbacks
- Graceful degradation for unsupported languages

### Tree-sitter Issues
- Parser loading failures
- Grammar version compatibility
- Query execution errors

## Performance Considerations

### Memory Management
- Large file streaming
- Parse tree cleanup
- Symbol map optimization

### Processing Speed
- Tree-sitter native performance
- Efficient query execution
- Minimal JSON serialization overhead

## Testing
- Unit tests: `shared/agent-utils/tests/`
- New tests cover:
  - `should_ignore_path`
  - `detect_language`
  - `parse_code_file_to_json` short-circuit when `ignore_dirs` matches
- Markers: `@pytest.mark.utils`, `@pytest.mark.parsing`
- Test files for each supported language
- Edge case handling validation

## Extension Points

### Adding New Languages
1. Install Tree-sitter parser for language
2. Define symbol extraction queries
3. Add language detection mapping
4. Implement language-specific parsing logic
5. Add test cases for validation

### Custom Symbol Types
- Extend symbol type enumeration
- Add parsing queries for new constructs
- Update JSON output format
- Maintain backward compatibility

## Integration Usage

### By Other Modules
- **Index Workflow**: Code structure for embedding generation
- **Graph Workflow**: Symbol extraction for graph building
- **Smell Detection**: Code analysis for smell detection
- **Query Service**: Code parsing for search results

### Common Patterns
```python
# Parse for symbol extraction
symbols = await parse_code_file_to_json(filepath, content)

# Use in graph building
for symbol in symbols["symbols"]:
    await add_symbol_to_graph(symbol)

# Use in indexing
for chunk in create_chunks_from_symbols(symbols):
    await store_embedding(chunk)
```

## Dependencies
- **Tree-sitter**: Core parsing engine
- **Dagger Engine**: Container operations
- **Language Grammars**: Parser definitions for each language

## Troubleshooting

### Parser Issues
- Verify Tree-sitter grammar installation
- Check language support and version compatibility
- Review query syntax for symbol extraction

### Performance Problems
- Monitor memory usage for large files
- Optimize parsing queries
- Consider file size limits

### Output Format
- Validate JSON structure compliance
- Check symbol completeness
- Verify import resolution accuracy