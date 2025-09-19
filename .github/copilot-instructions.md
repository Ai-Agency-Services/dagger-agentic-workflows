# Copilot Instructions for this Repository

Use these focused rules when proposing or editing code in this repo. Keep changes minimal, safe, and aligned with existing patterns.

## Context & high-level
- This repo hosts Dagger-based agentic workflows: Cover (tests/coverage), Graph (code graph/Neo4j), Index (pgvector/Supabase), services (Neo4j), and shared config/models.
- Key entry points:
  - workflows/cover/src/coverage/main.py: Dagger object with functions like setup_environment, process_report(s), generate_unit_tests.
  - workflows/graph/src/graph/main.py: Graph builder (files, symbols, IMPORTS/DEFINED_IN/EXPORTS/CALLS/REFERENCES).
  - services/neo/src/neo/main.py: Neo4j service wrapper and utilities.
  - shared/dagger-agents-config/src/ais_dagger_agents_config/models.py: YAMLConfig + AgentsConfig.

## Editing rules (do/don't)
- Do keep Dagger @object_type fields serializable only; create runtime objects (agents, clients) locally inside @function methods.
- Do use Pydantic v2 (model_validate, BaseModel) and existing models; extend YAMLConfig via the shared package.
- Do prefer ImportAnalyzer and shared parsing utilities; don't duplicate simple import scanners.
- Don't add heavy dependencies to runtime containers unless necessary; prefer native/standard libs and existing images.
- Don't break function signatures or public module APIs without updating all call sites.

## Dagger patterns
- Split responsibilities: environment setup → per-report processing → batch orchestration → test generation.
- Always use anyio for concurrency, not asyncio. Use anyio.TaskGroup and anyio.move_on_after for timeouts.
- Never use asyncio.create_task or CancelScope directly. Prefer anyio for better Dagger compatibility.
- Return primitive data, dagger.Files/Dirs, or JSON via helpers; avoid passing custom classes across boundaries.

## Configuration
- YAMLConfig lives in shared/dagger-agents-config; use its AgentsConfig (builder_agent_model, unit_test_agent_model, pull_request_agent_model).
- Treat config.agents as structured (not dict). Validate with Pydantic; fail fast with clear messages.

## Graph + Vector
- Prefer vector-first retrieval (Supabase match_code_embeddings) then enrich with Neo4j structure (files, symbols, imports, calls, references).
- Preserve existing relationships; don't drop IMPORTS/DEFINED_IN/EXPORTS when adding new ones.
- Keep relative import resolution logic intact; reuse helper methods where present.

## Neo4j service
- Use cypher-shell with explicit auth and db: -u/-p and -d neo4j. Ensure APOC/plugin env via NEO4J_PLUGINS JSON.
- Create indexes/constraints idempotently. Provide raw output on failures for diagnostics.

## Testing, coverage, reporters
- Reporter interface methods to honor: get-code-under-test, get-coverage-html, get-coverage-reports, parse-test-results.
- For Jest/Pytest, verify imports exist and TS types are literal/strict when generating tests; use ImportAnalyzer results.
- Keep test location behavior aligned with config (save_next_to_code_under_test vs test_directory).

## Pull Requests behavior
- Use gh to create/update PRs. Guard for missing labels; create or continue gracefully.
- Commit identity comes from config.git (user_name/user_email). Don't hardcode.

## Style & quality gates
- Python: black/ruff conventions (see SDK docs). Type hints required for public functions.
- Prefer small, isolated diffs, with minimal new files. Add light tests/docs where safe.
- Before finish: Build/Lint/Unit tests smoke checks, keep logs concise, fail with actionable errors.
