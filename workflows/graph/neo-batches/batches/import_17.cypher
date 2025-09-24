// BATCH 00001
MERGE (from:File {filepath: "/app/services/neo/src/neo/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.orchestrator.agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MERGE (to:File {filepath: "index.utils.file"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00002
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) MERGE (to:File {filepath: "codebuff.constants"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/builder/src/builder/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/builder/src/builder/main.py"}) MERGE (to:File {filepath: "builder.core.builder_agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/services/query/src/query/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00003
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.thinker.agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/main.py"}) MERGE (to:File {filepath: "index.utils.file"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.orchestrator.models"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00004
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/smell/src/smell/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MERGE (to:File {filepath: "index.models"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/graph/src/graph/main.py"}) MERGE (to:File {filepath: "ais_dagger_agents_config.models"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) MERGE (to:File {filepath: "index.utils.code_parser"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00005
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.implementation.agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/main.py"}) MERGE (to:File {filepath: "index.models"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/smell/src/smell/main.py"}) MERGE (to:File {filepath: "urllib.parse"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) MERGE (to:File {filepath: "pull_request_agent.core.pull_request_agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/operations/import_analyzer.py"}) MERGE (to:File {filepath: "dagger.client.gen"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00006
MERGE (from:File {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py"}) MERGE (to:File {filepath: "jest_reporter_plugin.models.coverage_report"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) MERGE (to:File {filepath: "pull_request_agent.template"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/utils/llm.py"}) MERGE (to:File {filepath: "index.models.llm_credentials"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/pull_request/src/pull_request_agent/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00007
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) MERGE (to:File {filepath: "codebuff.constants"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) MERGE (to:File {filepath: "index.models"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) MERGE (to:File {filepath: "pydantic_ai.providers.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) MERGE (to:File {filepath: "pull_request_agent.utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00008
MERGE (from:File {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) MERGE (to:File {filepath: "index.utils.embeddings"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py"}) MERGE (to:File {filepath: "pytest_reporter_plugin.models.coverage_report"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/smell/src/smell/main.py"}) MERGE (to:File {filepath: "dagger.client.gen"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00009
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.file_explorer.agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/builder/src/builder/utils.py"}) MERGE (to:File {filepath: "pydantic_ai.providers.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/builder/src/builder/main.py"}) MERGE (to:File {filepath: "builder.utils"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/services/query/src/query/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/main.py"}) MERGE (to:File {filepath: "index.operations.embedding_handler"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00010
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.utils"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/smell/src/smell/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py"}) MERGE (to:File {filepath: "dagger.client.gen"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/graph/src/graph/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00011
MERGE (from:File {filepath: "/app/workflows/index/src/index/utils/llm.py"}) MERGE (to:File {filepath: "pydantic_ai.providers.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py"}) MERGE (to:File {filepath: "jest_reporter_plugin.models.coverage_report"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.file_picker.agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/builder/src/builder/main.py"}) MERGE (to:File {filepath: "builder.models.llm_credentials"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00012
MERGE (from:File {filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py"}) MERGE (to:File {filepath: "dagger.client.gen"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/shared/agent-utils/src/agent_utils/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) MERGE (to:File {filepath: "pydantic_ai.providers.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/services/neo/src/neo/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py"}) MERGE (to:File {filepath: "index.services.neo4j_service"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00013
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "dagger.mod"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "dagger._exceptions"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00014
MERGE (from:File {filepath: "/app/agents/builder/src/builder/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) MERGE (to:File {filepath: "builder.template"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/builder/src/builder/utils.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/main.py"}) MERGE (to:File {filepath: "index.operations.file_processor"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00015
MERGE (from:File {filepath: "/app/workflows/graph/src/graph/main.py"}) MERGE (to:File {filepath: "dagger.client.gen"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/smell/src/smell/main.py"}) MERGE (to:File {filepath: "ais_dagger_agents_config.models"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.reviewer.agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/shared/pytest_plugins/fixtures.py"}) MERGE (to:File {filepath: "unittest.mock"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/main.py"}) MERGE (to:File {filepath: "ais_dagger_agents_config.models"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00016
MERGE (from:File {filepath: "/app/workflows/graph/src/graph/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/index/src/index/utils/llm.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) MERGE (to:File {filepath: "codebuff.context_pruner.agent"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00017
MERGE (from:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/shared/agent-utils/src/agent_utils/__init__.py"}) MERGE (to:File {filepath: "/main.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/pull_request/src/pull_request_agent/__init__.py"}) MERGE (to:File {filepath: "/main/__init__.py"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
MERGE (from:File {filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py"}) MERGE (to:File {filepath: "pydantic_ai.models.openai"}) MERGE (from)-[:IMPORTS]->(to);
