// BATCH 00001
MATCH (s:Class {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/builder/src/builder/main.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/main.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/index/src/index/operations/import_analyzer.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/import_analyzer.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/smell/src/smell/main.py"}) MATCH (f:File {filepath: "/app/workflows/smell/src/smell/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Function {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/index/src/index/services/neo4j_service.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/services/neo4j_service.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/services/query/src/query/main.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Constant {filepath: "/app/agents/codebuff/src/codebuff/constants.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/constants.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Class {filepath: "/app/workflows/index/src/index/main.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Constant {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MATCH (f:File {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/services/query/src/query/utils/embeddings.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/embeddings.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00006
MATCH (s:Variable {filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/services/query/src/query/utils/embeddings.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/embeddings.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/graph/src/graph/models/code_file.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/models/code_file.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Constant {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/services/query/src/query/main.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00007
MATCH (s:Class {filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00008
MATCH (s:Function {filepath: "/app/simple_chalk/__init__.py"}) MATCH (f:File {filepath: "/app/simple_chalk/__init__.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/pull_request/src/pull_request_agent/template.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/template.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00009
MATCH (s:Method {filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MATCH (f:File {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/builder/src/builder/utils.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/builder/src/builder/template.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/template.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00010
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/simple_chalk/__init__.py"}) MATCH (f:File {filepath: "/app/simple_chalk/__init__.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00011
MATCH (s:Variable {filepath: "/app/agents/builder/src/builder/models/llm_credentials.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/models/llm_credentials.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/builder/src/builder/utils.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/graph/src/graph/main.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/services/query/src/query/main.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Constant {filepath: "/app/workflows/smell/src/smell/main.py"}) MATCH (f:File {filepath: "/app/workflows/smell/src/smell/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00012
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/__init__.py"}) MATCH (f:File {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/__init__.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/graph/src/graph/main.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/builder/src/builder/models/llm_credentials.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/models/llm_credentials.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00013
MATCH (s:Function {filepath: "/app/workflows/index/src/index/utils/llm.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/llm.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/builder/src/builder/utils.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/utils/llm.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/llm.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/workflows/graph/src/graph/utils.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00014
MATCH (s:Variable {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/graph/src/graph/main.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00015
MATCH (s:Method {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MATCH (f:File {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/models.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/models.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/workflows/index/src/index/utils/embeddings.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/embeddings.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00016
MATCH (s:Function {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MATCH (f:File {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/services/neo/src/neo/main.py"}) MATCH (f:File {filepath: "/app/services/neo/src/neo/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/utils/embeddings.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/embeddings.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00017
MATCH (s:Variable {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MATCH (f:File {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MATCH (f:File {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/services/query/src/query/utils/file.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/file.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00018
MATCH (s:Class {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py"}) MATCH (f:File {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/index/src/index/models.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/models.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00019
MATCH (s:Function {filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/scripts/coverage_all.py"}) MATCH (f:File {filepath: "/app/scripts/coverage_all.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/services/query/src/query/utils/file.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/file.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00020
MATCH (s:Method {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/scripts/coverage_all.py"}) MATCH (f:File {filepath: "/app/scripts/coverage_all.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00021
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Constant {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/workflows/index/src/index/utils/file.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/file.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MATCH (f:File {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py"}) MATCH (f:File {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00022
MATCH (s:Variable {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/graph/src/graph/utils.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/scripts/run_tests.py"}) MATCH (f:File {filepath: "/app/scripts/run_tests.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00023
MATCH (s:Method {filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/smell/src/smell/main.py"}) MATCH (f:File {filepath: "/app/workflows/smell/src/smell/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00024
MATCH (s:Method {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MATCH (f:File {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Constant {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/scripts/run_tests.py"}) MATCH (f:File {filepath: "/app/scripts/run_tests.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00025
MATCH (s:Method {filepath: "/app/services/neo/src/neo/main.py"}) MATCH (f:File {filepath: "/app/services/neo/src/neo/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/services/neo4j_service.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/services/neo4j_service.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py"}) MATCH (f:File {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00026
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00027
MATCH (s:Variable {filepath: "/app/services/neo/src/neo/main.py"}) MATCH (f:File {filepath: "/app/services/neo/src/neo/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/graph/src/graph/models/code_file.py"}) MATCH (f:File {filepath: "/app/workflows/graph/src/graph/models/code_file.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00028
MATCH (s:Class {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/workflows/index/src/index/template.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/template.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/operations/import_analyzer.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/import_analyzer.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00029
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/agents/builder/src/builder/main.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00030
MATCH (s:Function {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MATCH (f:File {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/services/neo/src/neo/main.py"}) MATCH (f:File {filepath: "/app/services/neo/src/neo/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00031
MATCH (s:Method {filepath: "/app/workflows/smell/src/smell/main.py"}) MATCH (f:File {filepath: "/app/workflows/smell/src/smell/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py"}) MATCH (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00032
MATCH (s:Variable {filepath: "/app/agents/builder/src/builder/main.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/index/src/index/services/neo4j_service.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/services/neo4j_service.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Variable {filepath: "/app/workflows/index/src/index/utils/file.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/utils/file.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/workflows/index/src/index/operations/import_analyzer.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/operations/import_analyzer.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00033
MATCH (s:Function {filepath: "/app/agents/pull_request/src/pull_request_agent/template.py"}) MATCH (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/template.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Class {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MATCH (f:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Method {filepath: "/app/workflows/index/src/index/main.py"}) MATCH (f:File {filepath: "/app/workflows/index/src/index/main.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/agents/builder/src/builder/template.py"}) MATCH (f:File {filepath: "/app/agents/builder/src/builder/template.py"}) MERGE (s)-[:DEFINED_IN]->(f);
MATCH (s:Function {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MATCH (f:File {filepath: "/app/services/query/src/query/utils/code_parser.py"}) MERGE (s)-[:DEFINED_IN]->(f);
