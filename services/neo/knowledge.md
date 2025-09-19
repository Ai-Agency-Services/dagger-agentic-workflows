# Neo4j Service Module Knowledge

## Purpose
Provides Neo4j graph database integration for storing and querying code structure, symbols, and relationships.

## Architecture

### Core Class: `NeoService`
- **Database Operations**: Connection management, query execution, database clearing
- **Code Graph Building**: Adding files, symbols, and relationships to Neo4j
- **Cypher Shell Integration**: Direct Neo4j interaction via cypher-shell container

### Key Data Models
- **`SymbolProperties`**: Stores symbol metadata (docstring, signature, scope, parent) with overflow JSON
- **`RelationshipProperties`**: Defines relationship metadata (type, name, value, weight)

## Core Functions

### Database Management
- `create()`: Factory method for service creation with config and secrets
- `connect()`: Establishes cypher-shell client connection
- `clear_database()`: Removes all nodes and relationships
- `test_connection()`: Validates database connectivity

### Graph Population
- `add_file_node()`: Creates File nodes with language metadata
- `add_symbol()`: Creates symbol nodes (Function, Class, Variable) with properties
- `add_relationship()`: Creates relationships between files/symbols

### Query Interface
- `run_query()`: Executes Cypher queries with result parsing
- `run_batch_queries()`: Combines multiple queries for efficiency
- `improved_simple_parse()`: Parses single values from query results
- `improved_parse_list()`: Parses lists from query results

## Configuration

### Required Config (`agencyservices.yaml`)
```yaml
neo4j:
  uri: neo4j://localhost:7687
  username: neo4j
  database: neo4j
```

### Docker Setup
- Uses `neo4j:2025.05` image
- Exposes ports 7474 (browser) and 7687 (bolt)
- Includes APOC plugin for advanced procedures
- Configures auth and initial setup

## Usage Patterns

### Basic Service Creation
```python
service = await dag.neo_service(
    config_file=config_file,
    password=neo_password,
    neo_auth=neo_auth,
    neo_data=neo_data
)
```

### Adding Code Elements
```python
# Add file
await service.add_file_node("src/main.py", "python")

# Add symbol with properties
props = SymbolProperties(
    docstring="Main function",
    signature="def main()",
    scope="global"
)
await service.add_symbol("Function", "main", "src/main.py", 1, 10, props)

# Add relationship
await service.add_relationship("src/main.py", "IMPORTS", "src/utils.py")
```

### Query Execution
```python
result = await service.run_query("MATCH (n:Function) RETURN n.name")
files = service.improved_parse_list(result)
```

## Dependencies
- **Neo4j Database**: Running Neo4j instance with proper auth
- **Cypher Shell**: Container-based cypher-shell for query execution
- **YAML Config**: Configuration via `YAMLConfig` from shared config

## Testing
- Unit tests: `services/neo/tests/`
- Coverage: `make test-services/neo-coverage`
- Markers: `@pytest.mark.neo4j` for database-dependent tests

## Key Implementation Notes

### String Escaping
- All user input is escaped for Cypher injection protection
- Quotes and backslashes properly handled in graph data

### Property Handling
- Known fields stored as direct node properties
- Extra fields serialized to `json_data` property
- JSON data parsed and applied as individual properties

### Error Handling
- Database operations return boolean success indicators
- Exceptions logged but don't crash the service
- Connection state tracked and validated

### Performance
- Batch query support for multiple operations
- Simple result parsing optimized for common patterns
- Connection reuse across operations

## Integration Points
- **Query Service**: Provides structural data via Neo4j queries
- **Graph Workflow**: Populates graph database with code structure
- **Smell Workflow**: Queries graph for code smell detection
- **Index Workflow**: Uses Neo4j for symbol relationships