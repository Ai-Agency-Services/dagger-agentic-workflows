// BATCH 00001
MERGE (f:File {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py"}) ON CREATE SET f.language = "python", f.path = "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "LLMCredentials", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 10}) SET s.end_line = 13;
MERGE (s:Variable {name: "base_url", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 12}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Variable {name: "api_key", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 13}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Class {name: "SymbolProperties", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 17}) SET s.end_line = 43;

// BATCH 00002
MERGE (s:Variable {name: "docstring", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 20}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Variable {name: "signature", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 21}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Variable {name: "scope", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 22}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Variable {name: "parent", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 23}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Variable {name: "json_data", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 27}) SET s.end_line = -1, s.scope = "SymbolProperties";

// BATCH 00003
MERGE (s:Method {name: "from_dict", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 30}) SET s.end_line = 43, s.scope = "SymbolProperties", s.docstring = "Create a SymbolProperties from a dictionary", s.signature = "def";
MERGE (s:Variable {name: "props", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 33}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Class {name: "ContainerConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 46}) SET s.end_line = 51;
MERGE (s:Variable {name: "work_dir", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 48}) SET s.end_line = -1, s.scope = "ContainerConfig";
MERGE (s:Variable {name: "docker_file_path", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 50}) SET s.end_line = -1, s.scope = "ContainerConfig";

// BATCH 00004
MERGE (s:Class {name: "GitConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 54}) SET s.end_line = 59;
MERGE (s:Variable {name: "user_name", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 56}) SET s.end_line = -1, s.scope = "GitConfig";
MERGE (s:Variable {name: "user_email", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 57}) SET s.end_line = -1, s.scope = "GitConfig";
MERGE (s:Variable {name: "base_pull_request_branch", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 58}) SET s.end_line = -1, s.scope = "GitConfig";
MERGE (s:Class {name: "ConcurrencyConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 62}) SET s.end_line = 68;

// BATCH 00005
MERGE (s:Variable {name: "batch_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 64}) SET s.end_line = -1, s.scope = "ConcurrencyConfig";
MERGE (s:Variable {name: "max_concurrent", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 65}) SET s.end_line = -1, s.scope = "ConcurrencyConfig";
MERGE (s:Variable {name: "embedding_batch_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 67}) SET s.end_line = -1, s.scope = "ConcurrencyConfig";
MERGE (s:Class {name: "IndexingConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 71}) SET s.end_line = 109;
MERGE (s:Variable {name: "clear_on_start", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 73}) SET s.end_line = -1, s.scope = "IndexingConfig";

// BATCH 00006
MERGE (s:Variable {name: "max_semantic_chunk_lines", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 75}) SET s.end_line = -1, s.scope = "IndexingConfig";
MERGE (s:Variable {name: "chunk_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 77}) SET s.end_line = -1, s.scope = "IndexingConfig";
MERGE (s:Variable {name: "max_file_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 78}) SET s.end_line = -1, s.scope = "IndexingConfig";
MERGE (s:Variable {name: "embedding_model", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 80}) SET s.end_line = -1, s.scope = "IndexingConfig";
MERGE (s:Variable {name: "file_extensions", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 82}) SET s.end_line = -1, s.scope = "IndexingConfig";

// BATCH 00007
MERGE (s:Variable {name: "max_files", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 86}) SET s.end_line = -1, s.scope = "IndexingConfig";
MERGE (s:Variable {name: "skip_indexing", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 87}) SET s.end_line = -1, s.scope = "IndexingConfig";
MERGE (s:Variable {name: "concurrency", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 90}) SET s.end_line = -1, s.scope = "IndexingConfig";
MERGE (s:Method {name: "batch_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 97}) SET s.end_line = 99, s.scope = "IndexingConfig", s.docstring = "Returns batch size from concurrency config.", s.signature = "def";
MERGE (s:Method {name: "max_concurrent", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 102}) SET s.end_line = 104, s.scope = "IndexingConfig", s.docstring = "Returns max concurrent from concurrency config.", s.signature = "def";

// BATCH 00008
MERGE (s:Method {name: "embedding_batch_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 107}) SET s.end_line = 109, s.scope = "IndexingConfig", s.docstring = "Returns embedding batch size from concurrency config.", s.signature = "def";
MERGE (s:Class {name: "TestGenerationConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 112}) SET s.end_line = 123;
MERGE (s:Variable {name: "limit", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 114}) SET s.end_line = -1, s.scope = "TestGenerationConfig";
MERGE (s:Variable {name: "test_directory", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 116}) SET s.end_line = -1, s.scope = "TestGenerationConfig";
MERGE (s:Variable {name: "test_suffix", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 119}) SET s.end_line = -1, s.scope = "TestGenerationConfig";

// BATCH 00009
MERGE (s:Variable {name: "save_next_to_code_under_test", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 121}) SET s.end_line = -1, s.scope = "TestGenerationConfig";
MERGE (s:Class {name: "ReporterConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 126}) SET s.end_line = 144;
MERGE (s:Variable {name: "name", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 128}) SET s.end_line = -1, s.scope = "ReporterConfig";
MERGE (s:Variable {name: "command", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 130}) SET s.end_line = -1, s.scope = "ReporterConfig";
MERGE (s:Variable {name: "report_directory", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 132}) SET s.end_line = -1, s.scope = "ReporterConfig";

// BATCH 00010
MERGE (s:Variable {name: "output_file_path", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 135}) SET s.end_line = -1, s.scope = "ReporterConfig";
MERGE (s:Variable {name: "file_test_command_template", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 139}) SET s.end_line = -1, s.scope = "ReporterConfig";
MERGE (s:Variable {name: "test_timeout_seconds", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 142}) SET s.end_line = -1, s.scope = "ReporterConfig";
MERGE (s:Class {name: "SmellThresholdsConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 148}) SET s.end_line = 155;
MERGE (s:Variable {name: "long_function_lines", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 150}) SET s.end_line = -1, s.scope = "SmellThresholdsConfig";

// BATCH 00011
MERGE (s:Variable {name: "long_param_count", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 151}) SET s.end_line = -1, s.scope = "SmellThresholdsConfig";
MERGE (s:Variable {name: "large_class_loc", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 152}) SET s.end_line = -1, s.scope = "SmellThresholdsConfig";
MERGE (s:Variable {name: "god_class_methods", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 153}) SET s.end_line = -1, s.scope = "SmellThresholdsConfig";
MERGE (s:Variable {name: "high_fan_out", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 154}) SET s.end_line = -1, s.scope = "SmellThresholdsConfig";
MERGE (s:Variable {name: "high_fan_in", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 155}) SET s.end_line = -1, s.scope = "SmellThresholdsConfig";

// BATCH 00012
MERGE (s:Class {name: "SmellDetectorsConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 158}) SET s.end_line = 161;
MERGE (s:Variable {name: "include", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 160}) SET s.end_line = -1, s.scope = "SmellDetectorsConfig";
MERGE (s:Variable {name: "exclude", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 161}) SET s.end_line = -1, s.scope = "SmellDetectorsConfig";
MERGE (s:Class {name: "SmellConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 164}) SET s.end_line = 167;
MERGE (s:Variable {name: "thresholds", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 166}) SET s.end_line = -1, s.scope = "SmellConfig";

// BATCH 00013
MERGE (s:Variable {name: "detectors", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 167}) SET s.end_line = -1, s.scope = "SmellConfig";
MERGE (s:Class {name: "CoreAPIConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 170}) SET s.end_line = 181;
MERGE (s:Variable {name: "model", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 172}) SET s.end_line = -1, s.scope = "CoreAPIConfig";
MERGE (s:Variable {name: "fqdn", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 174}) SET s.end_line = -1, s.scope = "CoreAPIConfig";
MERGE (s:Variable {name: "provider", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 176}) SET s.end_line = -1, s.scope = "CoreAPIConfig";

// BATCH 00014
MERGE (s:Variable {name: "fallback_models", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 178}) SET s.end_line = -1, s.scope = "CoreAPIConfig";
MERGE (s:Class {name: "Neo4jConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 184}) SET s.end_line = 231;
MERGE (s:Variable {name: "image", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 187}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "uri", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 189}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "username", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 191}) SET s.end_line = -1, s.scope = "Neo4jConfig";

// BATCH 00015
MERGE (s:Variable {name: "database", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 192}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "clear_on_start", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 193}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "enabled", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 195}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "cypher_shell_repository", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 199}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "http_port", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 205}) SET s.end_line = -1, s.scope = "Neo4jConfig";

// BATCH 00016
MERGE (s:Variable {name: "bolt_port", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 206}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "data_volume_path", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 208}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "cache_volume_name", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 210}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "plugins", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 214}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "apoc_export_file_enabled", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 218}) SET s.end_line = -1, s.scope = "Neo4jConfig";

// BATCH 00017
MERGE (s:Variable {name: "apoc_import_file_enabled", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 220}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "apoc_import_use_neo4j_config", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 222}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "memory_pagecache_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 226}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "memory_heap_initial_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 228}) SET s.end_line = -1, s.scope = "Neo4jConfig";
MERGE (s:Variable {name: "memory_heap_max_size", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 230}) SET s.end_line = -1, s.scope = "Neo4jConfig";

// BATCH 00018
MERGE (s:Class {name: "YAMLConfig", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 234}) SET s.end_line = 250;
MERGE (s:Variable {name: "container", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 236}) SET s.end_line = -1, s.scope = "YAMLConfig";
MERGE (s:Variable {name: "git", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 237}) SET s.end_line = -1, s.scope = "YAMLConfig";
MERGE (s:Variable {name: "concurrency", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 238}) SET s.end_line = -1, s.scope = "YAMLConfig";
MERGE (s:Variable {name: "indexing", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 240}) SET s.end_line = -1, s.scope = "YAMLConfig";

// BATCH 00019
MERGE (s:Variable {name: "test_generation", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 241}) SET s.end_line = -1, s.scope = "YAMLConfig";
MERGE (s:Variable {name: "reporter", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 242}) SET s.end_line = -1, s.scope = "YAMLConfig";
MERGE (s:Variable {name: "core_api", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 243}) SET s.end_line = -1, s.scope = "YAMLConfig";
MERGE (s:Variable {name: "neo4j", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 244}) SET s.end_line = -1, s.scope = "YAMLConfig";
MERGE (s:Variable {name: "smell", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 246}) SET s.end_line = -1, s.scope = "YAMLConfig";

// BATCH 00020
MERGE (s:Class {name: "Config", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", start_line: 248}) SET s.end_line = 250, s.scope = "YAMLConfig";
MERGE (s:Variable {name: "extra", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/models.py", line_number: 250}) SET s.end_line = -1, s.scope = "YAMLConfig.Config";
MERGE (f:File {filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/__init__.py" ON MATCH SET f.language = "python";
MERGE (s:Variable {name: "__version__", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/__init__.py", line_number: 21}) SET s.end_line = -1;
MERGE (s:Variable {name: "__all__", filepath: "/app/shared/dagger-agents-config/src/ais_dagger_agents_config/__init__.py", line_number: 23}) SET s.end_line = -1;

// BATCH 00021
MERGE (f:File {filepath: "/app/scripts/coverage_all.py"}) ON CREATE SET f.language = "python", f.path = "/app/scripts/coverage_all.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "run_command", filepath: "/app/scripts/coverage_all.py", start_line: 8}) SET s.end_line = 16, s.docstring = "Run a command and return exit code.", s.signature = "def";
MERGE (s:Variable {name: "result", filepath: "/app/scripts/coverage_all.py", line_number: 12}) SET s.end_line = -1;
MERGE (s:Function {name: "main", filepath: "/app/scripts/coverage_all.py", start_line: 18}) SET s.end_line = 112, s.signature = "def";
MERGE (s:Variable {name: "project_root", filepath: "/app/scripts/coverage_all.py", line_number: 19}) SET s.end_line = -1;

// BATCH 00022
MERGE (s:Variable {name: "modules", filepath: "/app/scripts/coverage_all.py", line_number: 22}) SET s.end_line = -1;
MERGE (s:Variable {name: "coverage_dir", filepath: "/app/scripts/coverage_all.py", line_number: 35}) SET s.end_line = -1;
MERGE (s:Variable {name: "all_passed", filepath: "/app/scripts/coverage_all.py", line_number: 38}) SET s.end_line = -1;
MERGE (s:Variable {name: "module_dir", filepath: "/app/scripts/coverage_all.py", line_number: 41}) SET s.end_line = -1;
MERGE (s:Variable {name: "cmd", filepath: "/app/scripts/coverage_all.py", line_number: 49}) SET s.end_line = -1;

// BATCH 00023
MERGE (s:Variable {name: "exit_code", filepath: "/app/scripts/coverage_all.py", line_number: 59}) SET s.end_line = -1;
MERGE (s:Variable {name: "all_passed", filepath: "/app/scripts/coverage_all.py", line_number: 80}) SET s.end_line = -1;
MERGE (s:Variable {name: "cmd", filepath: "/app/scripts/coverage_all.py", line_number: 84}) SET s.end_line = -1;
MERGE (s:Variable {name: "exit_code", filepath: "/app/scripts/coverage_all.py", line_number: 93}) SET s.end_line = -1;
MERGE (s:Variable {name: "all_passed", filepath: "/app/scripts/coverage_all.py", line_number: 98}) SET s.end_line = -1;

// BATCH 00024
MERGE (f:File {filepath: "/app/scripts/run_tests.py"}) ON CREATE SET f.language = "python", f.path = "/app/scripts/run_tests.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "run_command", filepath: "/app/scripts/run_tests.py", start_line: 10}) SET s.end_line = 18, s.docstring = "Run a command and return exit code.", s.signature = "def";
MERGE (s:Variable {name: "result", filepath: "/app/scripts/run_tests.py", line_number: 14}) SET s.end_line = -1;
MERGE (s:Function {name: "main", filepath: "/app/scripts/run_tests.py", start_line: 21}) SET s.end_line = 99, s.signature = "def";
MERGE (s:Variable {name: "parser", filepath: "/app/scripts/run_tests.py", line_number: 22}) SET s.end_line = -1;

// BATCH 00025
MERGE (s:Variable {name: "args", filepath: "/app/scripts/run_tests.py", line_number: 45}) SET s.end_line = -1;
MERGE (s:Variable {name: "cmd", filepath: "/app/scripts/run_tests.py", line_number: 48}) SET s.end_line = -1;
MERGE (s:Variable {name: "exit_code", filepath: "/app/scripts/run_tests.py", line_number: 92}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/shared/dagger-agents-config/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/shared/dagger-agents-config/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/shared/agent-utils/src/agent_utils/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/shared/agent-utils/src/agent_utils/main.py" ON MATCH SET f.language = "python";

// BATCH 00026
MERGE (s:Class {name: "SymbolType", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 12}) SET s.end_line = 25;
MERGE (s:Constant {name: "VARIABLE", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 13}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "FUNCTION", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 14}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "CLASS", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 15}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "INTERFACE", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 16}) SET s.end_line = -1, s.scope = "SymbolType";

// BATCH 00027
MERGE (s:Constant {name: "ENUM", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 17}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "STRUCT", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 18}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "TRAIT", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 19}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "CONSTANT", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 20}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "METHOD", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 21}) SET s.end_line = -1, s.scope = "SymbolType";

// BATCH 00028
MERGE (s:Constant {name: "PROPERTY", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 22}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "MODULE", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 23}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "TYPE", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 24}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "IMPORT", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 25}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Class {name: "CodeSymbol", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 28}) SET s.end_line = 40;

// BATCH 00029
MERGE (s:Variable {name: "name", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 29}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "type", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 30}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "line_number", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 31}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "column", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 32}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "end_line_number", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 33}) SET s.end_line = -1, s.scope = "CodeSymbol";

// BATCH 00030
MERGE (s:Variable {name: "end_column", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 34}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "scope", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 35}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "signature", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 36}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "visibility", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 37}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "parameters", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 38}) SET s.end_line = -1, s.scope = "CodeSymbol";

// BATCH 00031
MERGE (s:Variable {name: "return_type", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 39}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "docstring", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 40}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Class {name: "CodeFile", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 43}) SET s.end_line = 48;
MERGE (s:Variable {name: "content", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 44}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "filepath", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 45}) SET s.end_line = -1, s.scope = "CodeFile";

// BATCH 00032
MERGE (s:Variable {name: "language", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 46}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "symbols", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 47}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "imports", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 48}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Function {name: "detect_language", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 51}) SET s.end_line = 77, s.docstring = "Detect the programming language from the file extension.", s.signature = "def";
MERGE (s:Variable {name: "ext", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 53}) SET s.end_line = -1;

// BATCH 00033
MERGE (s:Variable {name: "language_map", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 54}) SET s.end_line = -1;
MERGE (s:Class {name: "AgentUtils", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 82}) SET s.end_line = 637;
MERGE (s:Method {name: "parse_code_file_to_json", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 86}) SET s.end_line = 99, s.scope = "AgentUtils", s.docstring = "Parse a code file using Tree-sitter and return JSON with extracted symbols.", s.signature = "async";
MERGE (s:Variable {name: "language", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 92}) SET s.end_line = -1, s.scope = "AgentUtils";
MERGE (s:Method {name: "_parse_with_tree_sitter", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 102}) SET s.end_line = 138, s.scope = "AgentUtils", s.docstring = "Parse code using Tree-sitter with language-specific query patterns.", s.signature = "async";

// BATCH 00034
MERGE (s:Variable {name: "ext", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 106}) SET s.end_line = -1, s.scope = "AgentUtils";
MERGE (s:Variable {name: "filename", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 107}) SET s.end_line = -1, s.scope = "AgentUtils";
MERGE (s:Variable {name: "parser_script", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 110}) SET s.end_line = -1, s.scope = "AgentUtils";
MERGE (s:Method {name: "_get_file_extension", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 140}) SET s.end_line = 152, s.scope = "AgentUtils", s.docstring = "Get appropriate file extension for the language.", s.signature = "def";
MERGE (s:Variable {name: "extensions", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", line_number: 142}) SET s.end_line = -1, s.scope = "AgentUtils";

// BATCH 00035
MERGE (s:Method {name: "_generate_parser_script", filepath: "/app/shared/agent-utils/src/agent_utils/main.py", start_line: 154}) SET s.end_line = 637, s.scope = "AgentUtils", s.docstring = "Generate a Python script that uses Tree-sitter to parse the code.", s.signature = "def";
MERGE (f:File {filepath: "/app/shared/agent-utils/src/agent_utils/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/shared/agent-utils/src/agent_utils/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/shared/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/shared/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/shared/agent-utils/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/shared/agent-utils/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/shared/pytest_plugins/fixtures.py"}) ON CREATE SET f.language = "python", f.path = "/app/shared/pytest_plugins/fixtures.py" ON MATCH SET f.language = "python";

// BATCH 00036
MERGE (s:Function {name: "sample_yaml_config", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 9}) SET s.end_line = 30, s.docstring = "Sample YAML configuration for tests across modules.", s.signature = "def";
MERGE (s:Function {name: "mock_neo4j_driver", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 37}) SET s.end_line = 42, s.docstring = "Mock Neo4j driver for testing.", s.signature = "def";
MERGE (s:Variable {name: "driver", filepath: "/app/shared/pytest_plugins/fixtures.py", line_number: 39}) SET s.end_line = -1;
MERGE (s:Function {name: "mock_dagger_container", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 45}) SET s.end_line = 51, s.docstring = "Mock Dagger container for testing.", s.signature = "def";
MERGE (s:Variable {name: "container", filepath: "/app/shared/pytest_plugins/fixtures.py", line_number: 47}) SET s.end_line = -1;

// BATCH 00037
MERGE (s:Function {name: "mock_llm_credentials", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 54}) SET s.end_line = 59, s.docstring = "Mock LLM credentials for testing.", s.signature = "def";
MERGE (s:Variable {name: "creds", filepath: "/app/shared/pytest_plugins/fixtures.py", line_number: 56}) SET s.end_line = -1;
MERGE (s:Function {name: "mock_openai_model", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 62}) SET s.end_line = 66, s.docstring = "Mock OpenAI model for testing.", s.signature = "def";
MERGE (s:Variable {name: "model", filepath: "/app/shared/pytest_plugins/fixtures.py", line_number: 64}) SET s.end_line = -1;
MERGE (s:Function {name: "setup_test_environment", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 69}) SET s.end_line = 76, s.docstring = "Set up test environment variables for all tests.", s.signature = "def";

// BATCH 00038
MERGE (s:Function {name: "temp_file", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 79}) SET s.end_line = 83, s.docstring = "Create a temporary file for testing.", s.signature = "def";
MERGE (s:Variable {name: "file_path", filepath: "/app/shared/pytest_plugins/fixtures.py", line_number: 81}) SET s.end_line = -1;
MERGE (s:Function {name: "mock_code_file", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 86}) SET s.end_line = 100, s.docstring = "Mock code file for testing.", s.signature = "def";
MERGE (s:Class {name: "AsyncContextManager", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 102}) SET s.end_line = 111;
MERGE (s:Method {name: "__init__", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 104}) SET s.end_line = 105, s.scope = "AsyncContextManager", s.signature = "def";

// BATCH 00039
MERGE (s:Method {name: "__aenter__", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 107}) SET s.end_line = 108, s.scope = "AsyncContextManager", s.signature = "async";
MERGE (s:Method {name: "__aexit__", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 110}) SET s.end_line = 111, s.scope = "AsyncContextManager", s.signature = "async";
MERGE (s:Function {name: "async_context_manager", filepath: "/app/shared/pytest_plugins/fixtures.py", start_line: 114}) SET s.end_line = 116, s.docstring = "Factory for creating async context managers in tests.", s.signature = "def";
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/constants.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/constants.py" ON MATCH SET f.language = "python";
MERGE (s:Constant {name: "EXCLUDED_DIRS", filepath: "/app/agents/codebuff/src/codebuff/constants.py", start_line: 4}) SET s.end_line = -1;

// BATCH 00040
MERGE (f:File {filepath: "/app/shared/pytest_plugins/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/shared/pytest_plugins/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/utils.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/utils.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "LLMCredentials", filepath: "/app/agents/codebuff/src/codebuff/utils.py", start_line: 9}) SET s.end_line = 12;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 11}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 12}) SET s.end_line = -1, s.scope = "LLMCredentials";

// BATCH 00041
MERGE (s:Function {name: "get_llm_credentials", filepath: "/app/agents/codebuff/src/codebuff/utils.py", start_line: 15}) SET s.end_line = 61, s.docstring = "
    Determines the LLM base URL and retrieves the plaintext API key based on the provider.

    Args:
        provider: The name of the LLM provider (\'openrouter\' or \'openai\').
        open_router_key: The Dagger secret for the OpenRouter API key.
        openai_key: The Dagger secret for the OpenAI API key.

    Returns:
        A tuple containing (base_url, api_key_plain).
        base_url is None for OpenAI default.

    Raises:
        ValueError: If the provider is unsupported or the required key is missing.
    ", s.signature = "async";
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 35}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 36}) SET s.end_line = -1;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 42}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 43}) SET s.end_line = -1;

// BATCH 00042
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 49}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 50}) SET s.end_line = -1;
MERGE (s:Function {name: "create_llm_model", filepath: "/app/agents/codebuff/src/codebuff/utils.py", start_line: 64}) SET s.end_line = 101, s.docstring = "
    Creates the Pydantic AI model instance (currently OpenAIModel).

    Args:
        api_key: The API key as Dagger secret.
        base_url: The base URL for the API (None for OpenAI default).
        model_name: The specific model name to use.

    Returns:
        An instance of OpenAIModel.

    Raises:
        Exception: If initialization of the provider or model fails.
    ", s.signature = "async";
MERGE (s:Variable {name: "api_key_plain", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 88}) SET s.end_line = -1;
MERGE (s:Variable {name: "llm_provider", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 91}) SET s.end_line = -1;

// BATCH 00043
MERGE (s:Variable {name: "effective_base_url", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 93}) SET s.end_line = -1;
MERGE (s:Variable {name: "pydantic_ai_model", filepath: "/app/agents/codebuff/src/codebuff/utils.py", line_number: 94}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/reviewer/agent.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "ReviewerDependencies", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", start_line: 11}) SET s.end_line = 14;
MERGE (s:Variable {name: "config", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 12}) SET s.end_line = -1, s.scope = "ReviewerDependencies";

// BATCH 00044
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 13}) SET s.end_line = -1, s.scope = "ReviewerDependencies";
MERGE (s:Variable {name: "changes_description", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 14}) SET s.end_line = -1, s.scope = "ReviewerDependencies";
MERGE (s:Function {name: "check_syntax", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", start_line: 17}) SET s.end_line = 48, s.docstring = "Check syntax of modified files.", s.signature = "async";
MERGE (s:Variable {name: "results", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 25}) SET s.end_line = -1;
MERGE (s:Variable {name: "py_check", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 29}) SET s.end_line = -1;

// BATCH 00045
MERGE (s:Variable {name: "js_env_check", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 36}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 41}) SET s.end_line = -1;
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 46}) SET s.end_line = -1;
MERGE (s:Function {name: "run_tests", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", start_line: 51}) SET s.end_line = 96, s.docstring = "Run tests to validate changes.", s.signature = "async";
MERGE (s:Variable {name: "test_check", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 60}) SET s.end_line = -1;

// BATCH 00046
MERGE (s:Variable {name: "pytest_check", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 70}) SET s.end_line = -1;
MERGE (s:Variable {name: "test_command", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 73}) SET s.end_line = -1;
MERGE (s:Variable {name: "test_result", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 76}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 80}) SET s.end_line = -1;
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 94}) SET s.end_line = -1;

// BATCH 00047
MERGE (s:Function {name: "analyze_changes", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", start_line: 99}) SET s.end_line = 140, s.docstring = "Analyze the changes made to the codebase.", s.signature = "async";
MERGE (s:Variable {name: "git_status", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 107}) SET s.end_line = -1;
MERGE (s:Variable {name: "recent_changes", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 112}) SET s.end_line = -1;
MERGE (s:Variable {name: "potential_issues", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 117}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 121}) SET s.end_line = -1;

// BATCH 00048
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 138}) SET s.end_line = -1;
MERGE (s:Function {name: "create_reviewer_agent", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", start_line: 143}) SET s.end_line = 186, s.docstring = "Create the Reviewer agent.", s.signature = "def";
MERGE (s:Variable {name: "system_prompt", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 145}) SET s.end_line = -1;
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/reviewer/agent.py", line_number: 172}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/orchestrator/models.py" ON MATCH SET f.language = "python";

// BATCH 00049
MERGE (s:Class {name: "Phase", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 13}) SET s.end_line = 23;
MERGE (s:Constant {name: "EXPLORATION", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 15}) SET s.end_line = -1, s.scope = "Phase";
MERGE (s:Constant {name: "FILE_SELECTION", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 16}) SET s.end_line = -1, s.scope = "Phase";
MERGE (s:Constant {name: "PLANNING", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 17}) SET s.end_line = -1, s.scope = "Phase";
MERGE (s:Constant {name: "IMPLEMENTATION", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 18}) SET s.end_line = -1, s.scope = "Phase";

// BATCH 00050
MERGE (s:Constant {name: "REVIEW", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 19}) SET s.end_line = -1, s.scope = "Phase";
MERGE (s:Constant {name: "PULL_REQUEST", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 20}) SET s.end_line = -1, s.scope = "Phase";
MERGE (s:Constant {name: "CONTEXT_PRUNING", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 21}) SET s.end_line = -1, s.scope = "Phase";
MERGE (s:Constant {name: "COMPLETE", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 22}) SET s.end_line = -1, s.scope = "Phase";
MERGE (s:Constant {name: "FAILED", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 23}) SET s.end_line = -1, s.scope = "Phase";

// BATCH 00051
MERGE (s:Class {name: "Status", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 26}) SET s.end_line = 32;
MERGE (s:Constant {name: "PENDING", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 28}) SET s.end_line = -1, s.scope = "Status";
MERGE (s:Constant {name: "IN_PROGRESS", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 29}) SET s.end_line = -1, s.scope = "Status";
MERGE (s:Constant {name: "SUCCESS", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 30}) SET s.end_line = -1, s.scope = "Status";
MERGE (s:Constant {name: "FAILED", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 31}) SET s.end_line = -1, s.scope = "Status";

// BATCH 00052
MERGE (s:Constant {name: "RETRYING", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 32}) SET s.end_line = -1, s.scope = "Status";
MERGE (s:Class {name: "ErrorKind", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 35}) SET s.end_line = 41;
MERGE (s:Constant {name: "TOOL_ERROR", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 37}) SET s.end_line = -1, s.scope = "ErrorKind";
MERGE (s:Constant {name: "VALIDATION_ERROR", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 38}) SET s.end_line = -1, s.scope = "ErrorKind";
MERGE (s:Constant {name: "MODEL_ERROR", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 39}) SET s.end_line = -1, s.scope = "ErrorKind";

// BATCH 00053
MERGE (s:Constant {name: "RESOURCE_ERROR", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 40}) SET s.end_line = -1, s.scope = "ErrorKind";
MERGE (s:Constant {name: "POLICY_ERROR", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 41}) SET s.end_line = -1, s.scope = "ErrorKind";
MERGE (s:Class {name: "TaskSpec", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 44}) SET s.end_line = 50;
MERGE (s:Variable {name: "id", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 46}) SET s.end_line = -1, s.scope = "TaskSpec";
MERGE (s:Variable {name: "goal", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 47}) SET s.end_line = -1, s.scope = "TaskSpec";

// BATCH 00054
MERGE (s:Variable {name: "focus_area", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 48}) SET s.end_line = -1, s.scope = "TaskSpec";
MERGE (s:Variable {name: "constraints", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 49}) SET s.end_line = -1, s.scope = "TaskSpec";
MERGE (s:Variable {name: "success_criteria", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 50}) SET s.end_line = -1, s.scope = "TaskSpec";
MERGE (s:Class {name: "PathInfo", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 53}) SET s.end_line = 57;
MERGE (s:Variable {name: "path", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 55}) SET s.end_line = -1, s.scope = "PathInfo";

// BATCH 00055
MERGE (s:Variable {name: "relevance_score", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 56}) SET s.end_line = -1, s.scope = "PathInfo";
MERGE (s:Variable {name: "rationale", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 57}) SET s.end_line = -1, s.scope = "PathInfo";
MERGE (s:Class {name: "ExplorationReport", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 60}) SET s.end_line = 66;
MERGE (s:Variable {name: "areas_explored", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 62}) SET s.end_line = -1, s.scope = "ExplorationReport";
MERGE (s:Variable {name: "file_index", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 63}) SET s.end_line = -1, s.scope = "ExplorationReport";

// BATCH 00056
MERGE (s:Variable {name: "key_patterns", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 64}) SET s.end_line = -1, s.scope = "ExplorationReport";
MERGE (s:Variable {name: "architecture_notes", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 65}) SET s.end_line = -1, s.scope = "ExplorationReport";
MERGE (s:Variable {name: "confidence", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 66}) SET s.end_line = -1, s.scope = "ExplorationReport";
MERGE (s:Class {name: "FileSet", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 69}) SET s.end_line = 74;
MERGE (s:Variable {name: "files", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 71}) SET s.end_line = -1, s.scope = "FileSet";

// BATCH 00057
MERGE (s:Variable {name: "rationale", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 72}) SET s.end_line = -1, s.scope = "FileSet";
MERGE (s:Variable {name: "total_files_considered", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 73}) SET s.end_line = -1, s.scope = "FileSet";
MERGE (s:Variable {name: "confidence", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 74}) SET s.end_line = -1, s.scope = "FileSet";
MERGE (s:Class {name: "PlanStep", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 77}) SET s.end_line = 83;
MERGE (s:Variable {name: "id", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 79}) SET s.end_line = -1, s.scope = "PlanStep";

// BATCH 00058
MERGE (s:Variable {name: "description", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 80}) SET s.end_line = -1, s.scope = "PlanStep";
MERGE (s:Variable {name: "dependencies", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 81}) SET s.end_line = -1, s.scope = "PlanStep";
MERGE (s:Variable {name: "risk_level", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 82}) SET s.end_line = -1, s.scope = "PlanStep";
MERGE (s:Variable {name: "estimated_effort", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 83}) SET s.end_line = -1, s.scope = "PlanStep";
MERGE (s:Class {name: "Plan", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 86}) SET s.end_line = 93;

// BATCH 00059
MERGE (s:Variable {name: "steps", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 88}) SET s.end_line = -1, s.scope = "Plan";
MERGE (s:Variable {name: "risks", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 89}) SET s.end_line = -1, s.scope = "Plan";
MERGE (s:Variable {name: "dependencies", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 90}) SET s.end_line = -1, s.scope = "Plan";
MERGE (s:Variable {name: "test_strategy", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 91}) SET s.end_line = -1, s.scope = "Plan";
MERGE (s:Variable {name: "confidence", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 92}) SET s.end_line = -1, s.scope = "Plan";

// BATCH 00060
MERGE (s:Variable {name: "estimated_complexity", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 93}) SET s.end_line = -1, s.scope = "Plan";
MERGE (s:Class {name: "FileEdit", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 96}) SET s.end_line = 101;
MERGE (s:Variable {name: "path", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 98}) SET s.end_line = -1, s.scope = "FileEdit";
MERGE (s:Variable {name: "operation", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 99}) SET s.end_line = -1, s.scope = "FileEdit";
MERGE (s:Variable {name: "content_preview", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 100}) SET s.end_line = -1, s.scope = "FileEdit";

// BATCH 00061
MERGE (s:Variable {name: "line_count_change", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 101}) SET s.end_line = -1, s.scope = "FileEdit";
MERGE (s:Class {name: "CommandExecution", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 104}) SET s.end_line = 108;
MERGE (s:Variable {name: "command", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 106}) SET s.end_line = -1, s.scope = "CommandExecution";
MERGE (s:Variable {name: "exit_code", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 107}) SET s.end_line = -1, s.scope = "CommandExecution";
MERGE (s:Variable {name: "output_preview", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 108}) SET s.end_line = -1, s.scope = "CommandExecution";

// BATCH 00062
MERGE (s:Class {name: "ChangeSet", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 111}) SET s.end_line = 116;
MERGE (s:Variable {name: "edits", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 113}) SET s.end_line = -1, s.scope = "ChangeSet";
MERGE (s:Variable {name: "commands", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 114}) SET s.end_line = -1, s.scope = "ChangeSet";
MERGE (s:Variable {name: "migration_notes", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 115}) SET s.end_line = -1, s.scope = "ChangeSet";
MERGE (s:Variable {name: "rollback_instructions", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 116}) SET s.end_line = -1, s.scope = "ChangeSet";

// BATCH 00063
MERGE (s:Class {name: "ReviewFinding", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 119}) SET s.end_line = 125;
MERGE (s:Variable {name: "category", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 121}) SET s.end_line = -1, s.scope = "ReviewFinding";
MERGE (s:Variable {name: "severity", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 122}) SET s.end_line = -1, s.scope = "ReviewFinding";
MERGE (s:Variable {name: "description", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 123}) SET s.end_line = -1, s.scope = "ReviewFinding";
MERGE (s:Variable {name: "file_path", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 124}) SET s.end_line = -1, s.scope = "ReviewFinding";

// BATCH 00064
MERGE (s:Variable {name: "suggestion", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 125}) SET s.end_line = -1, s.scope = "ReviewFinding";
MERGE (s:Class {name: "ReviewReport", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 128}) SET s.end_line = 135;
MERGE (s:Variable {name: "findings", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 130}) SET s.end_line = -1, s.scope = "ReviewReport";
MERGE (s:Variable {name: "overall_status", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 131}) SET s.end_line = -1, s.scope = "ReviewReport";
MERGE (s:Variable {name: "tests_passed", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 132}) SET s.end_line = -1, s.scope = "ReviewReport";

// BATCH 00065
MERGE (s:Variable {name: "syntax_valid", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 133}) SET s.end_line = -1, s.scope = "ReviewReport";
MERGE (s:Variable {name: "recommendations", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 134}) SET s.end_line = -1, s.scope = "ReviewReport";
MERGE (s:Variable {name: "approval_status", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 135}) SET s.end_line = -1, s.scope = "ReviewReport";
MERGE (s:Class {name: "ContextSummary", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 138}) SET s.end_line = 145;
MERGE (s:Variable {name: "original_size", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 140}) SET s.end_line = -1, s.scope = "ContextSummary";

// BATCH 00066
MERGE (s:Variable {name: "pruned_size", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 141}) SET s.end_line = -1, s.scope = "ContextSummary";
MERGE (s:Variable {name: "reduction_percent", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 142}) SET s.end_line = -1, s.scope = "ContextSummary";
MERGE (s:Variable {name: "strategy_used", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 143}) SET s.end_line = -1, s.scope = "ContextSummary";
MERGE (s:Variable {name: "token_estimate", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 144}) SET s.end_line = -1, s.scope = "ContextSummary";
MERGE (s:Variable {name: "preserved_sections", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 145}) SET s.end_line = -1, s.scope = "ContextSummary";

// BATCH 00067
MERGE (s:Class {name: "OrchestrationError", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 148}) SET s.end_line = 155;
MERGE (s:Variable {name: "kind", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 150}) SET s.end_line = -1, s.scope = "OrchestrationError";
MERGE (s:Variable {name: "message", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 151}) SET s.end_line = -1, s.scope = "OrchestrationError";
MERGE (s:Variable {name: "phase", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 152}) SET s.end_line = -1, s.scope = "OrchestrationError";
MERGE (s:Variable {name: "retry_count", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 153}) SET s.end_line = -1, s.scope = "OrchestrationError";

// BATCH 00068
MERGE (s:Variable {name: "recoverable", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 154}) SET s.end_line = -1, s.scope = "OrchestrationError";
MERGE (s:Variable {name: "context", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 155}) SET s.end_line = -1, s.scope = "OrchestrationError";
MERGE (s:Class {name: "PullRequestResult", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 158}) SET s.end_line = 165;
MERGE (s:Variable {name: "pr_number", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 160}) SET s.end_line = -1, s.scope = "PullRequestResult";
MERGE (s:Variable {name: "pr_url", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 161}) SET s.end_line = -1, s.scope = "PullRequestResult";

// BATCH 00069
MERGE (s:Variable {name: "branch_name", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 162}) SET s.end_line = -1, s.scope = "PullRequestResult";
MERGE (s:Variable {name: "commit_hash", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 163}) SET s.end_line = -1, s.scope = "PullRequestResult";
MERGE (s:Variable {name: "status", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 164}) SET s.end_line = -1, s.scope = "PullRequestResult";
MERGE (s:Variable {name: "message", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 165}) SET s.end_line = -1, s.scope = "PullRequestResult";
MERGE (s:Class {name: "OrchestrationState", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 168}) SET s.end_line = 193;

// BATCH 00070
MERGE (s:Variable {name: "task_id", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 170}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "current_phase", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 171}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "status", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 172}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "start_time", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 173}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "last_update", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 174}) SET s.end_line = -1, s.scope = "OrchestrationState";

// BATCH 00071
MERGE (s:Variable {name: "retry_count", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 175}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "task_spec", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 178}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "exploration_report", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 179}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "file_set", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 180}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "plan", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 181}) SET s.end_line = -1, s.scope = "OrchestrationState";

// BATCH 00072
MERGE (s:Variable {name: "change_set", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 182}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "review_report", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 183}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "pull_request_result", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 184}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "context_summary", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 185}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "errors", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 188}) SET s.end_line = -1, s.scope = "OrchestrationState";

// BATCH 00073
MERGE (s:Variable {name: "total_tokens_used", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 191}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "total_requests", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 192}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Variable {name: "phase_durations", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 193}) SET s.end_line = -1, s.scope = "OrchestrationState";
MERGE (s:Class {name: "OrchestratorDependencies", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", start_line: 197}) SET s.end_line = 203;
MERGE (s:Variable {name: "config", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 199}) SET s.end_line = -1, s.scope = "OrchestratorDependencies";

// BATCH 00074
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 200}) SET s.end_line = -1, s.scope = "OrchestratorDependencies";
MERGE (s:Variable {name: "codebuff_module", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 201}) SET s.end_line = -1, s.scope = "OrchestratorDependencies";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 202}) SET s.end_line = -1, s.scope = "OrchestratorDependencies";
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/models.py", line_number: 203}) SET s.end_line = -1, s.scope = "OrchestratorDependencies";
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/context_pruner/agent.py" ON MATCH SET f.language = "python";

// BATCH 00075
MERGE (s:Class {name: "ContextPrunerDependencies", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", start_line: 12}) SET s.end_line = 16;
MERGE (s:Variable {name: "config", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 13}) SET s.end_line = -1, s.scope = "ContextPrunerDependencies";
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 14}) SET s.end_line = -1, s.scope = "ContextPrunerDependencies";
MERGE (s:Variable {name: "context_data", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 15}) SET s.end_line = -1, s.scope = "ContextPrunerDependencies";
MERGE (s:Variable {name: "max_tokens", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 16}) SET s.end_line = -1, s.scope = "ContextPrunerDependencies";

// BATCH 00076
MERGE (s:Function {name: "analyze_context_size", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", start_line: 19}) SET s.end_line = 75, s.docstring = "Analyze the current context size and identify pruning opportunities.", s.signature = "async";
MERGE (s:Variable {name: "context", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 26}) SET s.end_line = -1;
MERGE (s:Variable {name: "context_length", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 27}) SET s.end_line = -1;
MERGE (s:Variable {name: "estimated_tokens", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 28}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 31}) SET s.end_line = -1;

// BATCH 00077
MERGE (s:Variable {name: "sections", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 32}) SET s.end_line = -1;
MERGE (s:Variable {name: "current_section", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 33}) SET s.end_line = -1;
MERGE (s:Variable {name: "current_section", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 39}) SET s.end_line = -1;
MERGE (s:Variable {name: "large_sections", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 48}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 50}) SET s.end_line = -1;

// BATCH 00078
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 73}) SET s.end_line = -1;
MERGE (s:Function {name: "prune_context", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", start_line: 78}) SET s.end_line = 172, s.docstring = "Prune context to fit within token limits.", s.signature = "async";
MERGE (s:Variable {name: "context", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 86}) SET s.end_line = -1;
MERGE (s:Variable {name: "max_chars", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 87}) SET s.end_line = -1;
MERGE (s:Variable {name: "pruned_context", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 92}) SET s.end_line = -1;

// BATCH 00079
MERGE (s:Variable {name: "lines", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 96}) SET s.end_line = -1;
MERGE (s:Variable {name: "important_keywords", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 97}) SET s.end_line = -1;
MERGE (s:Variable {name: "line_lower", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 101}) SET s.end_line = -1;
MERGE (s:Variable {name: "is_important", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 102}) SET s.end_line = -1;
MERGE (s:Variable {name: "pruned_context", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 113}) SET s.end_line = -1;

// BATCH 00080
MERGE (s:Variable {name: "pruned_context", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 118}) SET s.end_line = -1;
MERGE (s:Variable {name: "quarter_size", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 122}) SET s.end_line = -1;
MERGE (s:Variable {name: "pruned_context", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 123}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 131}) SET s.end_line = -1;
MERGE (s:Variable {name: "in_section", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 132}) SET s.end_line = -1;

// BATCH 00081
MERGE (s:Variable {name: "lines_in_section", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 133}) SET s.end_line = -1;
MERGE (s:Variable {name: "in_section", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 137}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines_in_section", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 138}) SET s.end_line = -1;
MERGE (s:Variable {name: "in_section", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 145}) SET s.end_line = -1;
MERGE (s:Variable {name: "original_size", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 150}) SET s.end_line = -1;

// BATCH 00082
MERGE (s:Variable {name: "pruned_size", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 151}) SET s.end_line = -1;
MERGE (s:Variable {name: "reduction_percent", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 152}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 154}) SET s.end_line = -1;
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 170}) SET s.end_line = -1;
MERGE (s:Function {name: "create_context_pruner_agent", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", start_line: 175}) SET s.end_line = 219, s.docstring = "Create the Context Pruner agent.", s.signature = "def";

// BATCH 00083
MERGE (s:Variable {name: "system_prompt", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 177}) SET s.end_line = -1;
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/context_pruner/agent.py", line_number: 206}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/file_picker/agent.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "FilePickerDependencies", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", start_line: 13}) SET s.end_line = 16;
MERGE (s:Variable {name: "config", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 14}) SET s.end_line = -1, s.scope = "FilePickerDependencies";

// BATCH 00084
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 15}) SET s.end_line = -1, s.scope = "FilePickerDependencies";
MERGE (s:Variable {name: "task_description", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 16}) SET s.end_line = -1, s.scope = "FilePickerDependencies";
MERGE (s:Function {name: "search_relevant_files", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", start_line: 19}) SET s.end_line = 54, s.docstring = "Search for files relevant to the task.", s.signature = "async";
MERGE (s:Variable {name: "exclude_args", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 28}) SET s.end_line = -1;
MERGE (s:Variable {name: "name_search", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 30}) SET s.end_line = -1;

// BATCH 00085
MERGE (s:Variable {name: "exclude_grep", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 35}) SET s.end_line = -1;
MERGE (s:Variable {name: "content_search", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 36}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 40}) SET s.end_line = -1;
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 52}) SET s.end_line = -1;
MERGE (s:Function {name: "analyze_file_relevance", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", start_line: 57}) SET s.end_line = 93, s.docstring = "Analyze files to determine relevance to the task.", s.signature = "async";

// BATCH 00086
MERGE (s:Variable {name: "exclude_args", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 66}) SET s.end_line = -1;
MERGE (s:Variable {name: "recent_files", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 68}) SET s.end_line = -1;
MERGE (s:Variable {name: "file_types", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 73}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 77}) SET s.end_line = -1;
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 91}) SET s.end_line = -1;

// BATCH 00087
MERGE (s:Function {name: "create_file_picker_agent", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", start_line: 96}) SET s.end_line = 131, s.docstring = "Create the File Picker agent.", s.signature = "def";
MERGE (s:Variable {name: "system_prompt", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 98}) SET s.end_line = -1;
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/file_picker/agent.py", line_number: 118}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/orchestrator/agent.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "start_task", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 30}) SET s.end_line = 56, s.docstring = "Initialize a new orchestration task.", s.signature = "async";

// BATCH 00088
MERGE (s:Variable {name: "task_spec", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 38}) SET s.end_line = -1;
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 45}) SET s.end_line = -1;
MERGE (s:Function {name: "explore_codebase", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 59}) SET s.end_line = 107, s.docstring = "Execute exploration phase using File Explorer agent.", s.signature = "async";
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 66}) SET s.end_line = -1;
MERGE (s:Variable {name: "exploration_result", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 75}) SET s.end_line = -1;

// BATCH 00089
MERGE (s:Variable {name: "exploration_report", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 83}) SET s.end_line = -1;
MERGE (s:Variable {name: "error", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 98}) SET s.end_line = -1;
MERGE (s:Function {name: "select_files", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 110}) SET s.end_line = 157, s.docstring = "Execute file selection phase using File Picker agent.", s.signature = "async";
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 117}) SET s.end_line = -1;
MERGE (s:Variable {name: "selection_result", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 126}) SET s.end_line = -1;

// BATCH 00090
MERGE (s:Variable {name: "file_set", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 133}) SET s.end_line = -1;
MERGE (s:Variable {name: "error", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 148}) SET s.end_line = -1;
MERGE (s:Function {name: "create_implementation_plan", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 160}) SET s.end_line = 213, s.docstring = "Execute planning phase using Thinker agent.", s.signature = "async";
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 167}) SET s.end_line = -1;
MERGE (s:Variable {name: "relevant_files", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 176}) SET s.end_line = -1;

// BATCH 00091
MERGE (s:Variable {name: "relevant_files", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 178}) SET s.end_line = -1;
MERGE (s:Variable {name: "plan_result", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 181}) SET s.end_line = -1;
MERGE (s:Variable {name: "plan", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 189}) SET s.end_line = -1;
MERGE (s:Variable {name: "error", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 204}) SET s.end_line = -1;
MERGE (s:Function {name: "execute_implementation", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 216}) SET s.end_line = 265, s.docstring = "Execute implementation phase using Implementation agent.", s.signature = "async";

// BATCH 00092
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 223}) SET s.end_line = -1;
MERGE (s:Variable {name: "plan_str", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 232}) SET s.end_line = -1;
MERGE (s:Variable {name: "impl_result", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 235}) SET s.end_line = -1;
MERGE (s:Variable {name: "change_set", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 242}) SET s.end_line = -1;
MERGE (s:Variable {name: "error", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 256}) SET s.end_line = -1;

// BATCH 00093
MERGE (s:Function {name: "review_changes", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 268}) SET s.end_line = 314, s.docstring = "Execute review phase using Reviewer agent.", s.signature = "async";
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 275}) SET s.end_line = -1;
MERGE (s:Variable {name: "review_result", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 284}) SET s.end_line = -1;
MERGE (s:Variable {name: "review_report", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 291}) SET s.end_line = -1;
MERGE (s:Variable {name: "error", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 305}) SET s.end_line = -1;

// BATCH 00094
MERGE (s:Function {name: "create_pull_request", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 317}) SET s.end_line = 378, s.docstring = "Execute pull request creation phase using Pull Request agent.", s.signature = "async";
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 324}) SET s.end_line = -1;
MERGE (s:Variable {name: "task_description", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 333}) SET s.end_line = -1;
MERGE (s:Variable {name: "changes_summary", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 334}) SET s.end_line = -1;
MERGE (s:Variable {name: "review_status", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 335}) SET s.end_line = -1;

// BATCH 00095
MERGE (s:Variable {name: "pr_context", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 337}) SET s.end_line = -1;
MERGE (s:Variable {name: "pr_result", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 347}) SET s.end_line = -1;
MERGE (s:Variable {name: "pull_request_result", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 355}) SET s.end_line = -1;
MERGE (s:Variable {name: "error", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 369}) SET s.end_line = -1;
MERGE (s:Function {name: "get_orchestration_status", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 381}) SET s.end_line = 405, s.docstring = "Get current orchestration status and summary.", s.signature = "async";

// BATCH 00096
MERGE (s:Variable {name: "state", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 388}) SET s.end_line = -1;
MERGE (s:Variable {name: "duration", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 389}) SET s.end_line = -1;
MERGE (s:Variable {name: "status_summary", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 391}) SET s.end_line = -1;
MERGE (s:Function {name: "create_orchestrator_agent", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", start_line: 408}) SET s.end_line = 453, s.docstring = "Create the orchestration agent.", s.signature = "def";
MERGE (s:Variable {name: "system_prompt", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 410}) SET s.end_line = -1;

// BATCH 00097
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/orchestrator/agent.py", line_number: 433}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/implementation/agent.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "ImplementationDependencies", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", start_line: 11}) SET s.end_line = 14;
MERGE (s:Variable {name: "config", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 12}) SET s.end_line = -1, s.scope = "ImplementationDependencies";
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 13}) SET s.end_line = -1, s.scope = "ImplementationDependencies";

// BATCH 00098
MERGE (s:Variable {name: "plan", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 14}) SET s.end_line = -1, s.scope = "ImplementationDependencies";
MERGE (s:Function {name: "run_command", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", start_line: 17}) SET s.end_line = 42, s.docstring = "Execute a command in the container.", s.signature = "async";
MERGE (s:Variable {name: "command", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 28}) SET s.end_line = -1;
MERGE (s:Variable {name: "command", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 30}) SET s.end_line = -1;
MERGE (s:Variable {name: "container_with_exec", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 32}) SET s.end_line = -1;

// BATCH 00099
MERGE (s:Variable {name: "stdout", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 33}) SET s.end_line = -1;
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 40}) SET s.end_line = -1;
MERGE (s:Function {name: "read_file", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", start_line: 45}) SET s.end_line = 63, s.docstring = "Read the contents of a file.", s.signature = "async";
MERGE (s:Variable {name: "file_content", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 53}) SET s.end_line = -1;
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 61}) SET s.end_line = -1;

// BATCH 00100
MERGE (s:Function {name: "write_file", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", start_line: 66}) SET s.end_line = 94, s.docstring = "Write content to a file.", s.signature = "async";
MERGE (s:Variable {name: "container_with_write", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 76}) SET s.end_line = -1;
MERGE (s:Variable {name: "verify_result", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 84}) SET s.end_line = -1;
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 92}) SET s.end_line = -1;
MERGE (s:Function {name: "create_implementation_agent", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", start_line: 97}) SET s.end_line = 137, s.docstring = "Create the Implementation agent.", s.signature = "def";

// BATCH 00101
MERGE (s:Variable {name: "system_prompt", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 99}) SET s.end_line = -1;
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/implementation/agent.py", line_number: 123}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/thinker/agent.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "ThinkerDependencies", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", start_line: 12}) SET s.end_line = 16;

// BATCH 00102
MERGE (s:Variable {name: "config", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 13}) SET s.end_line = -1, s.scope = "ThinkerDependencies";
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 14}) SET s.end_line = -1, s.scope = "ThinkerDependencies";
MERGE (s:Variable {name: "task_description", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 15}) SET s.end_line = -1, s.scope = "ThinkerDependencies";
MERGE (s:Variable {name: "relevant_files", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 16}) SET s.end_line = -1, s.scope = "ThinkerDependencies";
MERGE (s:Function {name: "analyze_task_complexity", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", start_line: 19}) SET s.end_line = 71, s.docstring = "Analyze the complexity and requirements of the task.", s.signature = "async";

// BATCH 00103
MERGE (s:Variable {name: "file_analysis", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 27}) SET s.end_line = -1;
MERGE (s:Variable {name: "file_info", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 30}) SET s.end_line = -1;
MERGE (s:Variable {name: "deps_check", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 38}) SET s.end_line = -1;
MERGE (s:Variable {name: "git_status", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 43}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 47}) SET s.end_line = -1;

// BATCH 00104
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 69}) SET s.end_line = -1;
MERGE (s:Function {name: "create_execution_strategy", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", start_line: 74}) SET s.end_line = 142, s.docstring = "Create a detailed execution strategy for the task.", s.signature = "async";
MERGE (s:Variable {name: "test_files", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 83}) SET s.end_line = -1;
MERGE (s:Variable {name: "project_structure", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 88}) SET s.end_line = -1;
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 92}) SET s.end_line = -1;

// BATCH 00105
MERGE (s:Variable {name: "error_msg", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 140}) SET s.end_line = -1;
MERGE (s:Function {name: "create_thinker_agent", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", start_line: 145}) SET s.end_line = 181, s.docstring = "Create the Thinker/Planner agent.", s.signature = "def";
MERGE (s:Variable {name: "system_prompt", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 147}) SET s.end_line = -1;
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/thinker/agent.py", line_number: 168}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/main.py" ON MATCH SET f.language = "python";

// BATCH 00106
MERGE (s:Class {name: "Codebuff", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 29}) SET s.end_line = 535;
MERGE (s:Variable {name: "config", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 32}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "config_file", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 33}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 34}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "github_token", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 35}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00107
MERGE (s:Variable {name: "open_router_api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 36}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "openai_api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 37}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "model", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 38}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "_get_model_for_agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 40}) SET s.end_line = 61, s.scope = "Codebuff", s.docstring = "Get model name for specific agent from config, with fallbacks.", s.signature = "def";
MERGE (s:Variable {name: "fallbacks", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 52}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00108
MERGE (s:Method {name: "_get_llm_for_agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 63}) SET s.end_line = 82, s.scope = "Codebuff", s.docstring = "Determines the correct provider and creates the LLM for a given agent.", s.signature = "async";
MERGE (s:Variable {name: "model_name", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 70}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "provider", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 75}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "provider", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 77}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "provider", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 79}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00109
MERGE (s:Variable {name: "creds", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 81}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "create", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 85}) SET s.end_line = 100, s.scope = "Codebuff", s.docstring = "Create orchestrator from configuration.", s.signature = "async";
MERGE (s:Variable {name: "config_str", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 90}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "config_dict", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 91}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "explore_files", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 103}) SET s.end_line = 136, s.scope = "Codebuff", s.docstring = "Explore and map the codebase structure like Codebuff\'s File Explorer.", s.signature = "async";

// BATCH 00110
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 115}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "model", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 119}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "deps", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 123}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 129}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 130}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00111
MERGE (s:Method {name: "pick_files", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 139}) SET s.end_line = 171, s.scope = "Codebuff", s.docstring = "Pick relevant files for a task like Codebuff\'s File Picker.", s.signature = "async";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 150}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "model", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 154}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "deps", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 158}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 164}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00112
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 165}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "create_plan", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 174}) SET s.end_line = 212, s.scope = "Codebuff", s.docstring = "Create an execution plan like Codebuff\'s Thinker/Planner agent.", s.signature = "async";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 187}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "model", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 191}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "file_list", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 195}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00113
MERGE (s:Variable {name: "deps", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 198}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 205}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 206}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "implement_plan", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 215}) SET s.end_line = 247, s.scope = "Codebuff", s.docstring = "Implement the plan like Codebuff\'s Implementation agent.", s.signature = "async";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 226}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00114
MERGE (s:Variable {name: "model", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 230}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "deps", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 234}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 240}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 241}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "review_changes", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 250}) SET s.end_line = 282, s.scope = "Codebuff", s.docstring = "Review code changes like Codebuff\'s Reviewer agent.", s.signature = "async";

// BATCH 00115
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 261}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "model", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 265}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "deps", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 269}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 275}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 276}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00116
MERGE (s:Method {name: "prune_context", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 285}) SET s.end_line = 321, s.scope = "Codebuff", s.docstring = "Prune context like Codebuff\'s Context Pruner agent.", s.signature = "async";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 299}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "model", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 303}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "deps", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 307}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 314}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00117
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 315}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "create_pull_request", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 324}) SET s.end_line = 381, s.scope = "Codebuff", s.docstring = "Create pull request like Codebuff\'s Pull Request agent.", s.signature = "async";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 336}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "provider", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 341}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "creds", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 342}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00118
MERGE (s:Variable {name: "pr_agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 346}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "auth_container", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 350}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "pr_context", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 357}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "result_container", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 360}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "status", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 371}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00119
MERGE (s:Variable {name: "error_content", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 375}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "orchestrate_feature_development", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 384}) SET s.end_line = 473, s.scope = "Codebuff", s.docstring = "Orchestrate complete feature development workflow using all Codebuff agents.", s.signature = "async";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 405}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "model", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 410}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "deps", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 428}) SET s.end_line = -1, s.scope = "Codebuff";

// BATCH 00120
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 437}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "workflow_prompt", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 441}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "result", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 458}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "final_status", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 465}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Method {name: "setup_environment", filepath: "/app/agents/codebuff/src/codebuff/main.py", start_line: 476}) SET s.end_line = 535, s.scope = "Codebuff", s.docstring = "Set up the test environment and return a ready-to-use container.", s.signature = "async";

// BATCH 00121
MERGE (s:Variable {name: "config_obj", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 497}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "source", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 502}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/main.py", line_number: 512}) SET s.end_line = -1, s.scope = "Codebuff";
MERGE (f:File {filepath: "/app/agents/codebuff/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/agents/codebuff/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/codebuff/src/codebuff/file_explorer/agent.py" ON MATCH SET f.language = "python";

// BATCH 00122
MERGE (s:Class {name: "FileExplorerDependencies", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", start_line: 10}) SET s.end_line = 13;
MERGE (s:Variable {name: "config", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", line_number: 11}) SET s.end_line = -1, s.scope = "FileExplorerDependencies";
MERGE (s:Variable {name: "container", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", line_number: 12}) SET s.end_line = -1, s.scope = "FileExplorerDependencies";
MERGE (s:Variable {name: "focus_area", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", line_number: 13}) SET s.end_line = -1, s.scope = "FileExplorerDependencies";
MERGE (s:Function {name: "scan_directory_structure", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", start_line: 15}) SET s.end_line = 27, s.signature = "async";

// BATCH 00123
MERGE (s:Variable {name: "exclude_args", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", line_number: 19}) SET s.end_line = -1;
MERGE (s:Variable {name: "tree_output", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", line_number: 21}) SET s.end_line = -1;
MERGE (s:Function {name: "create_file_explorer_agent", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", start_line: 29}) SET s.end_line = 43, s.signature = "def";
MERGE (s:Variable {name: "system_prompt", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", line_number: 30}) SET s.end_line = -1;
MERGE (s:Variable {name: "agent", filepath: "/app/agents/codebuff/src/codebuff/file_explorer/agent.py", line_number: 34}) SET s.end_line = -1;

// BATCH 00124
MERGE (f:File {filepath: "/app/agents/codebuff/demo/feature-development-example.sh"}) ON CREATE SET f.language = "unknown", f.path = "/app/agents/codebuff/demo/feature-development-example.sh" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/template.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/pull_request/src/pull_request_agent/template.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "get_pull_request_agent_template", filepath: "/app/agents/pull_request/src/pull_request_agent/template.py", start_line: 6}) SET s.end_line = 59, s.signature = "def";
MERGE (s:Variable {name: "prompt", filepath: "/app/agents/pull_request/src/pull_request_agent/template.py", line_number: 7}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/pull_request/src/pull_request_agent/__init__.py" ON MATCH SET f.language = "python";

// BATCH 00125
MERGE (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/pull_request/src/pull_request_agent/utils.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "LLMCredentials", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", start_line: 9}) SET s.end_line = 12;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 11}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 12}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Function {name: "get_llm_credentials", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", start_line: 15}) SET s.end_line = 61, s.docstring = "
    Determines the LLM base URL and retrieves the plaintext API key based on the provider.

    Args:
        provider: The name of the LLM provider (\'openrouter\' or \'openai\').
        open_router_key: The Dagger secret for the OpenRouter API key.
        openai_key: The Dagger secret for the OpenAI API key.

    Returns:
        A tuple containing (base_url, api_key_plain).
        base_url is None for OpenAI default.

    Raises:
        ValueError: If the provider is unsupported or the required key is missing.
    ", s.signature = "async";

// BATCH 00126
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 35}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 36}) SET s.end_line = -1;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 42}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 43}) SET s.end_line = -1;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 49}) SET s.end_line = -1;

// BATCH 00127
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 50}) SET s.end_line = -1;
MERGE (s:Function {name: "create_llm_model", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", start_line: 64}) SET s.end_line = 95, s.docstring = "
    Creates the Pydantic AI model instance (currently OpenAIModel).

    Args:
        api_key: The plaintext API key.
        base_url: The base URL for the API (None for OpenAI default).
        model_name: The specific model name to use.

    Returns:
        An instance of OpenAIModel.

    Raises:
        Exception: If initialization of the provider or model fails.
    ", s.signature = "async";
MERGE (s:Variable {name: "llm_provider", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 84}) SET s.end_line = -1;
MERGE (s:Variable {name: "effective_base_url", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 87}) SET s.end_line = -1;
MERGE (s:Variable {name: "pydantic_ai_model", filepath: "/app/agents/pull_request/src/pull_request_agent/utils.py", line_number: 88}) SET s.end_line = -1;

// BATCH 00128
MERGE (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/pull_request/src/pull_request_agent/main.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "PullRequestAgent", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", start_line: 16}) SET s.end_line = 107;
MERGE (s:Variable {name: "config", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 17}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (s:Variable {name: "container", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 18}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (s:Method {name: "create", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", start_line: 21}) SET s.end_line = 25, s.scope = "PullRequestAgent", s.docstring = " Create a PullRequestAgent instance with the given configuration and container. ", s.signature = "async";

// BATCH 00129
MERGE (s:Variable {name: "config_str", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 23}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (s:Variable {name: "config_dict", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 24}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (s:Method {name: "_setup_logging", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", start_line: 27}) SET s.end_line = 34, s.scope = "PullRequestAgent", s.signature = "def";
MERGE (s:Method {name: "run", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", start_line: 37}) SET s.end_line = 107, s.scope = "PullRequestAgent", s.docstring = " Run the pull request agent with the given dependencies.", s.signature = "async";
MERGE (s:Method {name: "_run_agent", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", start_line: 48}) SET s.end_line = 88, s.scope = "PullRequestAgent", s.signature = "async";

// BATCH 00130
MERGE (s:Variable {name: "deps", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 57}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (s:Variable {name: "model", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 63}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (s:Variable {name: "agent", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 68}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (s:Variable {name: "result", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 71}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (s:Variable {name: "messages", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 76}) SET s.end_line = -1, s.scope = "PullRequestAgent";

// BATCH 00131
MERGE (s:Variable {name: "llm_credentials", filepath: "/app/agents/pull_request/src/pull_request_agent/main.py", line_number: 92}) SET s.end_line = -1, s.scope = "PullRequestAgent";
MERGE (f:File {filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "PullRequestAgentDependencies", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", start_line: 13}) SET s.end_line = 17;
MERGE (s:Variable {name: "config", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 14}) SET s.end_line = -1, s.scope = "PullRequestAgentDependencies";
MERGE (s:Variable {name: "container", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 15}) SET s.end_line = -1, s.scope = "PullRequestAgentDependencies";

// BATCH 00132
MERGE (s:Variable {name: "error_context", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 16}) SET s.end_line = -1, s.scope = "PullRequestAgentDependencies";
MERGE (s:Variable {name: "insight_context", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 17}) SET s.end_line = -1, s.scope = "PullRequestAgentDependencies";
MERGE (s:Function {name: "run_command", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", start_line: 20}) SET s.end_line = 70, s.docstring = "
    Run a command in the container and return the output.
    ", s.signature = "async";
MERGE (s:Variable {name: "branch_info", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 30}) SET s.end_line = -1;
MERGE (s:Variable {name: "status", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 34}) SET s.end_line = -1;

// BATCH 00133
MERGE (s:Variable {name: "branch_name", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 38}) SET s.end_line = -1;
MERGE (s:Variable {name: "branch_name", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 39}) SET s.end_line = -1;
MERGE (s:Variable {name: "command", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 43}) SET s.end_line = -1;
MERGE (s:Variable {name: "command", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 55}) SET s.end_line = -1;
MERGE (s:Variable {name: "command", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 58}) SET s.end_line = -1;

// BATCH 00134
MERGE (s:Variable {name: "container_with_exec", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 62}) SET s.end_line = -1;
MERGE (s:Variable {name: "stdout", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 64}) SET s.end_line = -1;
MERGE (s:Function {name: "create_pull_request_agent", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", start_line: 73}) SET s.end_line = 102, s.docstring = "
    Create and configure a pydantic_ai.Agent instance for code review and test generation.

    Args:
        pydantic_ai_model: An instance of pydantic_ai.models.OpenAIModel
                           configured with the desired provider and API key.

    Returns:
        A configured pydantic_ai.Agent instance.
    ", s.signature = "def";
MERGE (s:Variable {name: "base_system_prompt", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 85}) SET s.end_line = -1;
MERGE (s:Variable {name: "agent", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 87}) SET s.end_line = -1;

// BATCH 00135
MERGE (s:Variable {name: "__all__", filepath: "/app/agents/pull_request/src/pull_request_agent/core/pull_request_agent.py", line_number: 106}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/pull_request/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/agents/pull_request/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/agents/builder/src/builder/template.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/builder/src/builder/template.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "get_container_builder_template", filepath: "/app/agents/builder/src/builder/template.py", start_line: 5}) SET s.end_line = 68, s.signature = "def";
MERGE (s:Variable {name: "prompt", filepath: "/app/agents/builder/src/builder/template.py", line_number: 6}) SET s.end_line = -1;

// BATCH 00136
MERGE (f:File {filepath: "/app/agents/builder/src/builder/utils.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/builder/src/builder/utils.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "LLMCredentials", filepath: "/app/agents/builder/src/builder/utils.py", start_line: 9}) SET s.end_line = 12;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 11}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 12}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Function {name: "get_llm_credentials", filepath: "/app/agents/builder/src/builder/utils.py", start_line: 15}) SET s.end_line = 61, s.docstring = "
    Determines the LLM base URL and retrieves the plaintext API key based on the provider.

    Args:
        provider: The name of the LLM provider (\'openrouter\' or \'openai\').
        open_router_key: The Dagger secret for the OpenRouter API key.
        openai_key: The Dagger secret for the OpenAI API key.

    Returns:
        A tuple containing (base_url, api_key_plain).
        base_url is None for OpenAI default.

    Raises:
        ValueError: If the provider is unsupported or the required key is missing.
    ", s.signature = "async";

// BATCH 00137
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 35}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 36}) SET s.end_line = -1;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 42}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 43}) SET s.end_line = -1;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 49}) SET s.end_line = -1;

// BATCH 00138
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 50}) SET s.end_line = -1;
MERGE (s:Function {name: "create_llm_model", filepath: "/app/agents/builder/src/builder/utils.py", start_line: 64}) SET s.end_line = 95, s.docstring = "
    Creates the Pydantic AI model instance (currently OpenAIModel).

    Args:
        api_key: The plaintext API key.
        base_url: The base URL for the API (None for OpenAI default).
        model_name: The specific model name to use.

    Returns:
        An instance of OpenAIModel.

    Raises:
        Exception: If initialization of the provider or model fails.
    ", s.signature = "async";
MERGE (s:Variable {name: "llm_provider", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 84}) SET s.end_line = -1;
MERGE (s:Variable {name: "effective_base_url", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 87}) SET s.end_line = -1;
MERGE (s:Variable {name: "pydantic_ai_model", filepath: "/app/agents/builder/src/builder/utils.py", line_number: 88}) SET s.end_line = -1;

// BATCH 00139
MERGE (f:File {filepath: "/app/agents/builder/src/builder/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/builder/src/builder/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/agents/builder/src/builder/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/builder/src/builder/main.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "Builder", filepath: "/app/agents/builder/src/builder/main.py", start_line: 17}) SET s.end_line = 424;
MERGE (s:Variable {name: "base_container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 19}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "config", filepath: "/app/agents/builder/src/builder/main.py", line_number: 20}) SET s.end_line = -1, s.scope = "Builder";

// BATCH 00140
MERGE (s:Method {name: "create", filepath: "/app/agents/builder/src/builder/main.py", start_line: 23}) SET s.end_line = 27, s.scope = "Builder", s.docstring = " Create a Clean object from a YAML config file ", s.signature = "async";
MERGE (s:Variable {name: "config_str", filepath: "/app/agents/builder/src/builder/main.py", line_number: 25}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "config_dict", filepath: "/app/agents/builder/src/builder/main.py", line_number: 26}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Method {name: "_setup_logging", filepath: "/app/agents/builder/src/builder/main.py", start_line: 29}) SET s.end_line = 38, s.scope = "Builder", s.docstring = "Initializes logging for the Builder.", s.signature = "def";
MERGE (s:Method {name: "_install_dependencies", filepath: "/app/agents/builder/src/builder/main.py", start_line: 40}) SET s.end_line = 58, s.scope = "Builder", s.docstring = "Installs dependencies using OS detection first, then agent as fallback.", s.signature = "async";

// BATCH 00141
MERGE (s:Variable {name: "container_with_deps", filepath: "/app/agents/builder/src/builder/main.py", line_number: 49}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Method {name: "_install_dependencies_by_os_detection", filepath: "/app/agents/builder/src/builder/main.py", start_line: 60}) SET s.end_line = 139, s.scope = "Builder", s.docstring = "Install dependencies based on OS detection.", s.signature = "async";
MERGE (s:Variable {name: "os_release", filepath: "/app/agents/builder/src/builder/main.py", line_number: 67}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "package_managers", filepath: "/app/agents/builder/src/builder/main.py", line_number: 80}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "pm_check", filepath: "/app/agents/builder/src/builder/main.py", line_number: 92}) SET s.end_line = -1, s.scope = "Builder";

// BATCH 00142
MERGE (s:Variable {name: "verify", filepath: "/app/agents/builder/src/builder/main.py", line_number: 102}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "verify", filepath: "/app/agents/builder/src/builder/main.py", line_number: 110}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "debian_check", filepath: "/app/agents/builder/src/builder/main.py", line_number: 126}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Method {name: "_install_dependencies_with_agent", filepath: "/app/agents/builder/src/builder/main.py", start_line: 141}) SET s.end_line = 171, s.scope = "Builder", s.docstring = "Install dependencies using the builder agent.", s.signature = "async";
MERGE (s:Variable {name: "deps", filepath: "/app/agents/builder/src/builder/main.py", line_number: 148}) SET s.end_line = -1, s.scope = "Builder";

// BATCH 00143
MERGE (s:Variable {name: "model", filepath: "/app/agents/builder/src/builder/main.py", line_number: 151}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "builder_agent", filepath: "/app/agents/builder/src/builder/main.py", line_number: 157}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Method {name: "_install_alpine_deps", filepath: "/app/agents/builder/src/builder/main.py", start_line: 173}) SET s.end_line = 205, s.scope = "Builder", s.docstring = "Install dependencies using Alpine package manager.", s.signature = "async";
MERGE (s:Variable {name: "test_container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 177}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 183}) SET s.end_line = -1, s.scope = "Builder";

// BATCH 00144
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 184}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 189}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Method {name: "_install_debian_deps", filepath: "/app/agents/builder/src/builder/main.py", start_line: 207}) SET s.end_line = 233, s.scope = "Builder", s.docstring = "Install dependencies using Debian/Ubuntu package manager.", s.signature = "async";
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 211}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 212}) SET s.end_line = -1, s.scope = "Builder";

// BATCH 00145
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 217}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Method {name: "_install_generic_deps", filepath: "/app/agents/builder/src/builder/main.py", start_line: 235}) SET s.end_line = 276, s.scope = "Builder", s.docstring = "Install dependencies using a generic approach when OS cannot be identified.", s.signature = "async";
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 243}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 253}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "git_version", filepath: "/app/agents/builder/src/builder/main.py", line_number: 266}) SET s.end_line = -1, s.scope = "Builder";

// BATCH 00146
MERGE (s:Method {name: "_configure_git", filepath: "/app/agents/builder/src/builder/main.py", start_line: 278}) SET s.end_line = 286, s.scope = "Builder", s.docstring = "Configures git user name and email in the container.", s.signature = "def";
MERGE (s:Method {name: "build_test_environment", filepath: "/app/agents/builder/src/builder/main.py", start_line: 289}) SET s.end_line = 373, s.scope = "Builder", s.docstring = "
        Builds the primary container environment for testing.
        ", s.signature = "async";
MERGE (s:Variable {name: "work_dir", filepath: "/app/agents/builder/src/builder/main.py", line_number: 303}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "dockerfile_exists", filepath: "/app/agents/builder/src/builder/main.py", line_number: 311}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "llm_credentials", filepath: "/app/agents/builder/src/builder/main.py", line_number: 349}) SET s.end_line = -1, s.scope = "Builder";

// BATCH 00147
MERGE (s:Variable {name: "container_with_deps", filepath: "/app/agents/builder/src/builder/main.py", line_number: 356}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "git_container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 357}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "cmd", filepath: "/app/agents/builder/src/builder/main.py", line_number: 361}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "final_container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 362}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Variable {name: "final_container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 365}) SET s.end_line = -1, s.scope = "Builder";

// BATCH 00148
MERGE (s:Method {name: "build_cypher_shell", filepath: "/app/agents/builder/src/builder/main.py", start_line: 376}) SET s.end_line = 398, s.scope = "Builder", s.docstring = "
        Builds a container with a Cypher shell for Neo4j operations.

        Args:
            base_container: The container already built with user and agent dependencies.

        Returns:
            A container configured for Cypher shell operations.
        ", s.signature = "def";
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 390}) SET s.end_line = -1, s.scope = "Builder";
MERGE (s:Method {name: "setup_pull_request_container", filepath: "/app/agents/builder/src/builder/main.py", start_line: 401}) SET s.end_line = 424, s.scope = "Builder", s.docstring = "
        Sets up the container for managing pull requests, starting from a base container.

        Args:
            base_container: The container already built with user and agent dependencies.
            token: The GitHub token secret.

        Returns:
            A container configured for PR operations.
        ", s.signature = "def";
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/main.py", line_number: 416}) SET s.end_line = -1, s.scope = "Builder";
MERGE (f:File {filepath: "/app/agents/builder/src/builder/core/builder_agent.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/builder/src/builder/core/builder_agent.py" ON MATCH SET f.language = "python";

// BATCH 00149
MERGE (s:Class {name: "BuilderAgentDependencies", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", start_line: 11}) SET s.end_line = 12;
MERGE (s:Variable {name: "container", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 12}) SET s.end_line = -1, s.scope = "BuilderAgentDependencies";
MERGE (s:Variable {name: "dependencies", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 15}) SET s.end_line = -1;
MERGE (s:Function {name: "add_required_dependencies_prompt", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", start_line: 23}) SET s.end_line = 30, s.docstring = " System Prompt: Get the required dependencies content. ", s.signature = "async";
MERGE (s:Variable {name: "required_dependencies", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 26}) SET s.end_line = -1;

// BATCH 00150
MERGE (s:Function {name: "run_command", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", start_line: 33}) SET s.end_line = 66, s.docstring = "
    Run a command in the container and return the output.
    Args:  
        ctx: The run context containing the container and config.
        command: The command to run in the container.
    Returns:
        The output of the command.
    ", s.signature = "async";
MERGE (s:Variable {name: "command", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 51}) SET s.end_line = -1;
MERGE (s:Variable {name: "command", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 54}) SET s.end_line = -1;
MERGE (s:Variable {name: "container_with_exec", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 58}) SET s.end_line = -1;
MERGE (s:Variable {name: "stdout", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 60}) SET s.end_line = -1;

// BATCH 00151
MERGE (s:Function {name: "create_builder_agent", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", start_line: 69}) SET s.end_line = 89, s.signature = "def";
MERGE (s:Variable {name: "base_system_prompt", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 71}) SET s.end_line = -1;
MERGE (s:Variable {name: "agent", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 73}) SET s.end_line = -1;
MERGE (s:Variable {name: "__all__", filepath: "/app/agents/builder/src/builder/core/builder_agent.py", line_number: 92}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/agents/builder/src/builder/models/llm_credentials.py"}) ON CREATE SET f.language = "python", f.path = "/app/agents/builder/src/builder/models/llm_credentials.py" ON MATCH SET f.language = "python";

// BATCH 00152
MERGE (s:Class {name: "LLMCredentials", filepath: "/app/agents/builder/src/builder/models/llm_credentials.py", start_line: 8}) SET s.end_line = 11;
MERGE (s:Variable {name: "base_url", filepath: "/app/agents/builder/src/builder/models/llm_credentials.py", line_number: 10}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Variable {name: "api_key", filepath: "/app/agents/builder/src/builder/models/llm_credentials.py", line_number: 11}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (f:File {filepath: "/app/agents/builder/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/agents/builder/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/workflows/smell/src/smell/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/smell/src/smell/__init__.py" ON MATCH SET f.language = "python";

// BATCH 00153
MERGE (f:File {filepath: "/app/workflows/smell/src/smell/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/smell/src/smell/main.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "SmellSeverity", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 20}) SET s.end_line = 25;
MERGE (s:Constant {name: "LOW", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 22}) SET s.end_line = -1, s.scope = "SmellSeverity";
MERGE (s:Constant {name: "MEDIUM", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 23}) SET s.end_line = -1, s.scope = "SmellSeverity";
MERGE (s:Constant {name: "HIGH", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 24}) SET s.end_line = -1, s.scope = "SmellSeverity";

// BATCH 00154
MERGE (s:Constant {name: "CRITICAL", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 25}) SET s.end_line = -1, s.scope = "SmellSeverity";
MERGE (s:Class {name: "CodeSmell", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 29}) SET s.end_line = 57;
MERGE (s:Variable {name: "name", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 31}) SET s.end_line = -1, s.scope = "CodeSmell";
MERGE (s:Variable {name: "description", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 32}) SET s.end_line = -1, s.scope = "CodeSmell";
MERGE (s:Variable {name: "severity", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 33}) SET s.end_line = -1, s.scope = "CodeSmell";

// BATCH 00155
MERGE (s:Variable {name: "location", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 34}) SET s.end_line = -1, s.scope = "CodeSmell";
MERGE (s:Variable {name: "metrics", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 35}) SET s.end_line = -1, s.scope = "CodeSmell";
MERGE (s:Variable {name: "recommendation", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 36}) SET s.end_line = -1, s.scope = "CodeSmell";
MERGE (s:Method {name: "smell_type", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 39}) SET s.end_line = 42, s.scope = "CodeSmell", s.signature = "def";
MERGE (s:Variable {name: "s", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 40}) SET s.end_line = -1, s.scope = "CodeSmell";

// BATCH 00156
MERGE (s:Variable {name: "s", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 41}) SET s.end_line = -1, s.scope = "CodeSmell";
MERGE (s:Method {name: "symbol_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 45}) SET s.end_line = 50, s.scope = "CodeSmell", s.signature = "def";
MERGE (s:Variable {name: "v", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 47}) SET s.end_line = -1, s.scope = "CodeSmell";
MERGE (s:Method {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 53}) SET s.end_line = 54, s.scope = "CodeSmell", s.signature = "def";
MERGE (s:Method {name: "__str__", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 56}) SET s.end_line = 57, s.scope = "CodeSmell", s.signature = "def";

// BATCH 00157
MERGE (s:Class {name: "CodeSmellDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 60}) SET s.end_line = 71;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 64}) SET s.end_line = 66, s.scope = "CodeSmellDetector", s.docstring = "Detect code smells using Neo4j service", s.signature = "async";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 69}) SET s.end_line = 71, s.scope = "CodeSmellDetector", s.docstring = "Get the detector name", s.signature = "def";
MERGE (s:Class {name: "CircularDependencyDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 74}) SET s.end_line = 111;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 77}) SET s.end_line = 108, s.scope = "CircularDependencyDetector", s.docstring = "Clean Code Principle: Avoid circular dependencies (Dependency Inversion Principle)", s.signature = "async";

// BATCH 00158
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 79}) SET s.end_line = -1, s.scope = "CircularDependencyDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 90}) SET s.end_line = -1, s.scope = "CircularDependencyDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 91}) SET s.end_line = -1, s.scope = "CircularDependencyDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 94}) SET s.end_line = -1, s.scope = "CircularDependencyDetector";
MERGE (s:Variable {name: "data_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 96}) SET s.end_line = -1, s.scope = "CircularDependencyDetector";

// BATCH 00159
MERGE (s:Variable {name: "first", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 99}) SET s.end_line = -1, s.scope = "CircularDependencyDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 110}) SET s.end_line = 111, s.scope = "CircularDependencyDetector", s.signature = "def";
MERGE (s:Class {name: "LargeClassDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 114}) SET s.end_line = 169;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 117}) SET s.end_line = 166, s.scope = "LargeClassDetector", s.docstring = "Clean Code Principle: Single Responsibility Principle", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 119}) SET s.end_line = -1, s.scope = "LargeClassDetector";

// BATCH 00160
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 135}) SET s.end_line = -1, s.scope = "LargeClassDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 136}) SET s.end_line = -1, s.scope = "LargeClassDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 138}) SET s.end_line = -1, s.scope = "LargeClassDetector";
MERGE (s:Variable {name: "data_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 142}) SET s.end_line = -1, s.scope = "LargeClassDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 145}) SET s.end_line = -1, s.scope = "LargeClassDetector";

// BATCH 00161
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 149}) SET s.end_line = -1, s.scope = "LargeClassDetector";
MERGE (s:Variable {name: "sc_token", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 150}) SET s.end_line = -1, s.scope = "LargeClassDetector";
MERGE (s:Variable {name: "symbol_count", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 151}) SET s.end_line = -1, s.scope = "LargeClassDetector";
MERGE (s:Variable {name: "severity", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 154}) SET s.end_line = -1, s.scope = "LargeClassDetector";
MERGE (s:Variable {name: "class_name", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 155}) SET s.end_line = -1, s.scope = "LargeClassDetector";

// BATCH 00162
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 168}) SET s.end_line = 169, s.scope = "LargeClassDetector", s.signature = "def";
MERGE (s:Class {name: "FeatureEnvyDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 172}) SET s.end_line = 215;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 175}) SET s.end_line = 212, s.scope = "FeatureEnvyDetector", s.docstring = "Clean Code Principle: Tell, Don\'t Ask", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 177}) SET s.end_line = -1, s.scope = "FeatureEnvyDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 188}) SET s.end_line = -1, s.scope = "FeatureEnvyDetector";

// BATCH 00163
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 189}) SET s.end_line = -1, s.scope = "FeatureEnvyDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 191}) SET s.end_line = -1, s.scope = "FeatureEnvyDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 196}) SET s.end_line = -1, s.scope = "FeatureEnvyDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 198}) SET s.end_line = -1, s.scope = "FeatureEnvyDetector";
MERGE (s:Variable {name: "external_deps", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 199}) SET s.end_line = -1, s.scope = "FeatureEnvyDetector";

// BATCH 00164
MERGE (s:Variable {name: "severity", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 201}) SET s.end_line = -1, s.scope = "FeatureEnvyDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 214}) SET s.end_line = 215, s.scope = "FeatureEnvyDetector", s.signature = "def";
MERGE (s:Class {name: "DeadCodeDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 218}) SET s.end_line = 273;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 221}) SET s.end_line = 270, s.scope = "DeadCodeDetector", s.docstring = "Clean Code Principle: Delete dead code, don\'t comment it out", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 224}) SET s.end_line = -1, s.scope = "DeadCodeDetector";

// BATCH 00165
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 243}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 244}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 245}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Variable {name: "header", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 250}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Variable {name: "tokens", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 251}) SET s.end_line = -1, s.scope = "DeadCodeDetector";

// BATCH 00166
MERGE (s:Variable {name: "has_header", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 252}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Variable {name: "data_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 254}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 256}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Variable {name: "symbol_name", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 258}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 259}) SET s.end_line = -1, s.scope = "DeadCodeDetector";

// BATCH 00167
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 260}) SET s.end_line = -1, s.scope = "DeadCodeDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 272}) SET s.end_line = 273, s.scope = "DeadCodeDetector", s.signature = "def";
MERGE (s:Class {name: "ShotgunSurgeryDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 276}) SET s.end_line = 321;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 279}) SET s.end_line = 318, s.scope = "ShotgunSurgeryDetector", s.docstring = "Clean Code Principle: Minimize coupling", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 281}) SET s.end_line = -1, s.scope = "ShotgunSurgeryDetector";

// BATCH 00168
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 293}) SET s.end_line = -1, s.scope = "ShotgunSurgeryDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 294}) SET s.end_line = -1, s.scope = "ShotgunSurgeryDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 296}) SET s.end_line = -1, s.scope = "ShotgunSurgeryDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 301}) SET s.end_line = -1, s.scope = "ShotgunSurgeryDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 303}) SET s.end_line = -1, s.scope = "ShotgunSurgeryDetector";

// BATCH 00169
MERGE (s:Variable {name: "dependent_count", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 304}) SET s.end_line = -1, s.scope = "ShotgunSurgeryDetector";
MERGE (s:Variable {name: "severity", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 307}) SET s.end_line = -1, s.scope = "ShotgunSurgeryDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 320}) SET s.end_line = 321, s.scope = "ShotgunSurgeryDetector", s.signature = "def";
MERGE (s:Class {name: "HighFanOutDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 324}) SET s.end_line = 365;
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 326}) SET s.end_line = 327, s.scope = "HighFanOutDetector", s.signature = "def";

// BATCH 00170
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 329}) SET s.end_line = 362, s.scope = "HighFanOutDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 330}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 339}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 340}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 341}) SET s.end_line = -1, s.scope = "HighFanOutDetector";

// BATCH 00171
MERGE (s:Variable {name: "data_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 342}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 345}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 348}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Variable {name: "fo_token", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 349}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Variable {name: "fan_out", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 350}) SET s.end_line = -1, s.scope = "HighFanOutDetector";

// BATCH 00172
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 351}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Variable {name: "symbol_hint", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 353}) SET s.end_line = -1, s.scope = "HighFanOutDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 364}) SET s.end_line = 365, s.scope = "HighFanOutDetector", s.signature = "def";
MERGE (s:Class {name: "HighFanInDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 368}) SET s.end_line = 404;
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 371}) SET s.end_line = 372, s.scope = "HighFanInDetector", s.signature = "def";

// BATCH 00173
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 374}) SET s.end_line = 401, s.scope = "HighFanInDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 375}) SET s.end_line = -1, s.scope = "HighFanInDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 384}) SET s.end_line = -1, s.scope = "HighFanInDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 385}) SET s.end_line = -1, s.scope = "HighFanInDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 386}) SET s.end_line = -1, s.scope = "HighFanInDetector";

// BATCH 00174
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 388}) SET s.end_line = -1, s.scope = "HighFanInDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 390}) SET s.end_line = -1, s.scope = "HighFanInDetector";
MERGE (s:Variable {name: "fan_in", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 391}) SET s.end_line = -1, s.scope = "HighFanInDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 392}) SET s.end_line = -1, s.scope = "HighFanInDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 403}) SET s.end_line = 404, s.scope = "HighFanInDetector", s.signature = "def";

// BATCH 00175
MERGE (s:Class {name: "InstabilityDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 407}) SET s.end_line = 451;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 410}) SET s.end_line = 448, s.scope = "InstabilityDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 411}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 425}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 426}) SET s.end_line = -1, s.scope = "InstabilityDetector";

// BATCH 00176
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 427}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 429}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 431}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Variable {name: "fan_in", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 432}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Variable {name: "fan_out", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 433}) SET s.end_line = -1, s.scope = "InstabilityDetector";

// BATCH 00177
MERGE (s:Variable {name: "instability", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 435}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Variable {name: "instability", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 437}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 438}) SET s.end_line = -1, s.scope = "InstabilityDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 450}) SET s.end_line = 451, s.scope = "InstabilityDetector", s.signature = "def";
MERGE (s:Class {name: "LongFunctionDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 454}) SET s.end_line = 504;

// BATCH 00178
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 456}) SET s.end_line = 457, s.scope = "LongFunctionDetector", s.signature = "def";
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 459}) SET s.end_line = 501, s.scope = "LongFunctionDetector", s.signature = "async";
MERGE (s:Variable {name: "threshold", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 460}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 461}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 470}) SET s.end_line = -1, s.scope = "LongFunctionDetector";

// BATCH 00179
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 471}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 472}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "data_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 475}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 478}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 481}) SET s.end_line = -1, s.scope = "LongFunctionDetector";

// BATCH 00180
MERGE (s:Variable {name: "nums", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 482}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "span", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 484}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "span", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 487}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "span", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 489}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "symbol", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 490}) SET s.end_line = -1, s.scope = "LongFunctionDetector";

// BATCH 00181
MERGE (s:Variable {name: "kind", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 491}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 492}) SET s.end_line = -1, s.scope = "LongFunctionDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 503}) SET s.end_line = 504, s.scope = "LongFunctionDetector", s.signature = "def";
MERGE (s:Class {name: "DeepDependencyChainDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 507}) SET s.end_line = 540;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 510}) SET s.end_line = 537, s.scope = "DeepDependencyChainDetector", s.signature = "async";

// BATCH 00182
MERGE (s:Variable {name: "min_depth", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 511}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 512}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 520}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 521}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 522}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";

// BATCH 00183
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 524}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 526}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";
MERGE (s:Variable {name: "depth", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 527}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 528}) SET s.end_line = -1, s.scope = "DeepDependencyChainDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 539}) SET s.end_line = 540, s.scope = "DeepDependencyChainDetector", s.signature = "def";

// BATCH 00184
MERGE (s:Class {name: "OrphanModuleDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 543}) SET s.end_line = 570;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 546}) SET s.end_line = 567, s.scope = "OrphanModuleDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 547}) SET s.end_line = -1, s.scope = "OrphanModuleDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 554}) SET s.end_line = -1, s.scope = "OrphanModuleDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 555}) SET s.end_line = -1, s.scope = "OrphanModuleDetector";

// BATCH 00185
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 556}) SET s.end_line = -1, s.scope = "OrphanModuleDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 558}) SET s.end_line = -1, s.scope = "OrphanModuleDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 569}) SET s.end_line = 570, s.scope = "OrphanModuleDetector", s.signature = "def";
MERGE (s:Class {name: "BarrelFileDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 573}) SET s.end_line = 610;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 576}) SET s.end_line = 607, s.scope = "BarrelFileDetector", s.signature = "async";

// BATCH 00186
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 577}) SET s.end_line = -1, s.scope = "BarrelFileDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 589}) SET s.end_line = -1, s.scope = "BarrelFileDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 590}) SET s.end_line = -1, s.scope = "BarrelFileDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 591}) SET s.end_line = -1, s.scope = "BarrelFileDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 593}) SET s.end_line = -1, s.scope = "BarrelFileDetector";

// BATCH 00187
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 595}) SET s.end_line = -1, s.scope = "BarrelFileDetector";
MERGE (s:Variable {name: "fan_out", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 596}) SET s.end_line = -1, s.scope = "BarrelFileDetector";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 597}) SET s.end_line = -1, s.scope = "BarrelFileDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 598}) SET s.end_line = -1, s.scope = "BarrelFileDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 609}) SET s.end_line = 610, s.scope = "BarrelFileDetector", s.signature = "def";

// BATCH 00188
MERGE (s:Class {name: "DuplicateSymbolDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 613}) SET s.end_line = 646;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 616}) SET s.end_line = 643, s.scope = "DuplicateSymbolDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 617}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 625}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 626}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";

// BATCH 00189
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 627}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 629}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";
MERGE (s:Variable {name: "name", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 631}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";
MERGE (s:Variable {name: "kind", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 632}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";
MERGE (s:Variable {name: "occ", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 633}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";

// BATCH 00190
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 634}) SET s.end_line = -1, s.scope = "DuplicateSymbolDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 645}) SET s.end_line = 646, s.scope = "DuplicateSymbolDetector", s.signature = "def";
MERGE (s:Class {name: "GodComponentDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 649}) SET s.end_line = 700;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 652}) SET s.end_line = 697, s.scope = "GodComponentDetector", s.signature = "async";
MERGE (s:Variable {name: "threshold", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 653}) SET s.end_line = -1, s.scope = "GodComponentDetector";

// BATCH 00191
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 654}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 665}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 666}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 667}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "data_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 668}) SET s.end_line = -1, s.scope = "GodComponentDetector";

// BATCH 00192
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 671}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 673}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "imports", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 674}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 675}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 676}) SET s.end_line = -1, s.scope = "GodComponentDetector";

// BATCH 00193
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 686}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "fcount", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 687}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 688}) SET s.end_line = -1, s.scope = "GodComponentDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 699}) SET s.end_line = 700, s.scope = "GodComponentDetector", s.signature = "def";
MERGE (s:Class {name: "CrossDirectoryCouplingDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 703}) SET s.end_line = 741;

// BATCH 00194
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 706}) SET s.end_line = 738, s.scope = "CrossDirectoryCouplingDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 707}) SET s.end_line = -1, s.scope = "CrossDirectoryCouplingDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 721}) SET s.end_line = -1, s.scope = "CrossDirectoryCouplingDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 722}) SET s.end_line = -1, s.scope = "CrossDirectoryCouplingDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 723}) SET s.end_line = -1, s.scope = "CrossDirectoryCouplingDetector";

// BATCH 00195
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 725}) SET s.end_line = -1, s.scope = "CrossDirectoryCouplingDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 727}) SET s.end_line = -1, s.scope = "CrossDirectoryCouplingDetector";
MERGE (s:Variable {name: "dirs", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 728}) SET s.end_line = -1, s.scope = "CrossDirectoryCouplingDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 729}) SET s.end_line = -1, s.scope = "CrossDirectoryCouplingDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 740}) SET s.end_line = 741, s.scope = "CrossDirectoryCouplingDetector", s.signature = "def";

// BATCH 00196
MERGE (s:Class {name: "MutualDependencyDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 745}) SET s.end_line = 775;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 748}) SET s.end_line = 772, s.scope = "MutualDependencyDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 749}) SET s.end_line = -1, s.scope = "MutualDependencyDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 756}) SET s.end_line = -1, s.scope = "MutualDependencyDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 757}) SET s.end_line = -1, s.scope = "MutualDependencyDetector";

// BATCH 00197
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 758}) SET s.end_line = -1, s.scope = "MutualDependencyDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 760}) SET s.end_line = -1, s.scope = "MutualDependencyDetector";
MERGE (s:Variable {name: "a", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 762}) SET s.end_line = -1, s.scope = "MutualDependencyDetector";
MERGE (s:Variable {name: "b", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 763}) SET s.end_line = -1, s.scope = "MutualDependencyDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 774}) SET s.end_line = 775, s.scope = "MutualDependencyDetector", s.signature = "def";

// BATCH 00198
MERGE (s:Class {name: "HubModuleDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 779}) SET s.end_line = 818;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 782}) SET s.end_line = 815, s.scope = "HubModuleDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 783}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 794}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 795}) SET s.end_line = -1, s.scope = "HubModuleDetector";

// BATCH 00199
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 796}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 798}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 800}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Variable {name: "fi", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 802}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Variable {name: "fo", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 803}) SET s.end_line = -1, s.scope = "HubModuleDetector";

// BATCH 00200
MERGE (s:Variable {name: "fi", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 805}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Variable {name: "fo", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 805}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 806}) SET s.end_line = -1, s.scope = "HubModuleDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 817}) SET s.end_line = 818, s.scope = "HubModuleDetector", s.signature = "def";
MERGE (s:Class {name: "LargeClassByLinesDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 822}) SET s.end_line = 866;

// BATCH 00201
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 824}) SET s.end_line = 825, s.scope = "LargeClassByLinesDetector", s.signature = "def";
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 827}) SET s.end_line = 863, s.scope = "LargeClassByLinesDetector", s.signature = "async";
MERGE (s:Variable {name: "threshold", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 828}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 829}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 837}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";

// BATCH 00202
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 838}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Variable {name: "lines_out", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 839}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 842}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 844}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Variable {name: "class_name", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 845}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";

// BATCH 00203
MERGE (s:Variable {name: "loc", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 847}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Variable {name: "loc", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 849}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 850}) SET s.end_line = -1, s.scope = "LargeClassByLinesDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 865}) SET s.end_line = 866, s.scope = "LargeClassByLinesDetector", s.signature = "def";
MERGE (s:Class {name: "LongParameterListDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 870}) SET s.end_line = 917;

// BATCH 00204
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 872}) SET s.end_line = 873, s.scope = "LongParameterListDetector", s.signature = "def";
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 875}) SET s.end_line = 914, s.scope = "LongParameterListDetector", s.signature = "async";
MERGE (s:Variable {name: "min_params", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 876}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 877}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 890}) SET s.end_line = -1, s.scope = "LongParameterListDetector";

// BATCH 00205
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 891}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "lines_out", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 892}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 895}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 897}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "name", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 898}) SET s.end_line = -1, s.scope = "LongParameterListDetector";

// BATCH 00206
MERGE (s:Variable {name: "kind", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 899}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "param_count", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 901}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "param_count", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 903}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 904}) SET s.end_line = -1, s.scope = "LongParameterListDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 916}) SET s.end_line = 917, s.scope = "LongParameterListDetector", s.signature = "def";

// BATCH 00207
MERGE (s:Class {name: "GodClassByMethodsDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 921}) SET s.end_line = 962;
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 923}) SET s.end_line = 924, s.scope = "GodClassByMethodsDetector", s.signature = "def";
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 926}) SET s.end_line = 959, s.scope = "GodClassByMethodsDetector", s.signature = "async";
MERGE (s:Variable {name: "threshold", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 927}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 928}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";

// BATCH 00208
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 937}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 938}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Variable {name: "lines_out", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 939}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 942}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 944}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";

// BATCH 00209
MERGE (s:Variable {name: "class_name", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 945}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Variable {name: "method_count", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 947}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Variable {name: "method_count", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 949}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 950}) SET s.end_line = -1, s.scope = "GodClassByMethodsDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 961}) SET s.end_line = 962, s.scope = "GodClassByMethodsDetector", s.signature = "def";

// BATCH 00210
MERGE (s:Class {name: "FeatureEnvyAdvancedDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 966}) SET s.end_line = 1012;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 969}) SET s.end_line = 1009, s.scope = "FeatureEnvyAdvancedDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 971}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 985}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 986}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";

// BATCH 00211
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 987}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 990}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 992}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "method", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 993}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "internal_calls", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 995}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";

// BATCH 00212
MERGE (s:Variable {name: "external_calls", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 996}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "internal_calls", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 998}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "external_calls", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 999}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1000}) SET s.end_line = -1, s.scope = "FeatureEnvyAdvancedDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1011}) SET s.end_line = 1012, s.scope = "FeatureEnvyAdvancedDetector", s.signature = "def";

// BATCH 00213
MERGE (s:Class {name: "MessageChainDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1016}) SET s.end_line = 1053;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1019}) SET s.end_line = 1050, s.scope = "MessageChainDetector", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1021}) SET s.end_line = -1, s.scope = "MessageChainDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1029}) SET s.end_line = -1, s.scope = "MessageChainDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1030}) SET s.end_line = -1, s.scope = "MessageChainDetector";

// BATCH 00214
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1031}) SET s.end_line = -1, s.scope = "MessageChainDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1033}) SET s.end_line = -1, s.scope = "MessageChainDetector";
MERGE (s:Variable {name: "method", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1035}) SET s.end_line = -1, s.scope = "MessageChainDetector";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1036}) SET s.end_line = -1, s.scope = "MessageChainDetector";
MERGE (s:Variable {name: "max_chain", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1038}) SET s.end_line = -1, s.scope = "MessageChainDetector";

// BATCH 00215
MERGE (s:Variable {name: "max_chain", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1040}) SET s.end_line = -1, s.scope = "MessageChainDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1041}) SET s.end_line = -1, s.scope = "MessageChainDetector";
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1052}) SET s.end_line = 1053, s.scope = "MessageChainDetector", s.signature = "def";
MERGE (s:Class {name: "LawOfDemeterDetector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1057}) SET s.end_line = 1097;
MERGE (s:Method {name: "detect", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1060}) SET s.end_line = 1094, s.scope = "LawOfDemeterDetector", s.signature = "async";

// BATCH 00216
MERGE (s:Variable {name: "query", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1062}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1073}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1074}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1075}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1077}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";

// BATCH 00217
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1079}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";
MERGE (s:Variable {name: "method", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1080}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";
MERGE (s:Variable {name: "ext_files", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1082}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";
MERGE (s:Variable {name: "ext_files", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1084}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";
MERGE (s:Variable {name: "sev", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1085}) SET s.end_line = -1, s.scope = "LawOfDemeterDetector";

// BATCH 00218
MERGE (s:Method {name: "get_name", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1096}) SET s.end_line = 1097, s.scope = "LawOfDemeterDetector", s.signature = "def";
MERGE (s:Class {name: "Smell", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1101}) SET s.end_line = 1665;
MERGE (s:Variable {name: "config", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1103}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "config_file", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1104}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "neo_data", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1105}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00219
MERGE (s:Method {name: "_get_smell_config", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1107}) SET s.end_line = 1118, s.scope = "Smell", s.docstring = "Return smell configuration block from YAML if present (safe defaults).", s.signature = "def";
MERGE (s:Method {name: "create", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1121}) SET s.end_line = 1132, s.scope = "Smell", s.docstring = "Create a Smell object from a YAML config file.", s.signature = "async";
MERGE (s:Variable {name: "config_str", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1130}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "config_dict", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1131}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "_setup_logging", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1134}) SET s.end_line = 1140, s.scope = "Smell", s.docstring = "Setup structured logging.", s.signature = "def";

// BATCH 00220
MERGE (s:Method {name: "_github_url_for_file", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1142}) SET s.end_line = 1158, s.scope = "Smell", s.signature = "def";
MERGE (s:Variable {name: "git_cfg", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1146}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "repo_url", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1147}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "branch", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1149}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "base", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1152}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00221
MERGE (s:Variable {name: "rel", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1153}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "rel_quoted", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1154}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "br", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1155}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "_get_concurrency_config", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1160}) SET s.end_line = 1170, s.scope = "Smell", s.docstring = "Extract concurrency configuration from YAML config.", s.signature = "def";
MERGE (s:Variable {name: "config_obj", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1165}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00222
MERGE (s:Variable {name: "concurrency_config", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1167}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "_get_all_detectors", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1172}) SET s.end_line = 1226, s.scope = "Smell", s.docstring = "Get all available code smell detectors, honoring YAML include/exclude and thresholds", s.signature = "def";
MERGE (s:Variable {name: "cfg", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1175}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "thresholds", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1176}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "detectors_cfg", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1177}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00223
MERGE (s:Variable {name: "include", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1178}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "exclude", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1179}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "t", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1181}) SET s.end_line = 1186, s.scope = "Smell", s.signature = "def";
MERGE (s:Variable {name: "val", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1183}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "detector_entries", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1189}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00224
MERGE (s:Method {name: "norm", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1216}) SET s.end_line = 1217, s.scope = "Smell", s.signature = "def";
MERGE (s:Variable {name: "wanted", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1220}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "detector_entries", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1221}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "blocked", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1223}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "detector_entries", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1224}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00225
MERGE (s:Method {name: "_run_detectors_concurrently", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1228}) SET s.end_line = 1271, s.scope = "Smell", s.docstring = "Run all detectors concurrently with controlled concurrency.", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1239}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "semaphore", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1240}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1241}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "run_detector_with_limit", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1243}) SET s.end_line = 1258, s.scope = "Smell", s.signature = "async";

// BATCH 00226
MERGE (s:Variable {name: "det_label", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1245}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1249}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "display", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1253}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "collect_result", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1262}) SET s.end_line = 1264, s.scope = "Smell", s.signature = "async";
MERGE (s:Method {name: "_generate_report", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1273}) SET s.end_line = 1368, s.scope = "Smell", s.docstring = "Generate a clean, actionable report", s.signature = "def";

// BATCH 00227
MERGE (s:Variable {name: "total_smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1275}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "report_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1283}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "totals", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1291}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "severity_counts", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1304}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "critical_found", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1317}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00228
MERGE (s:Variable {name: "critical_found", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1321}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "metrics_str", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1322}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "link", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1324}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "mstr", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1360}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "link", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1362}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00229
MERGE (s:Method {name: "analyze_codebase", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1371}) SET s.end_line = 1437, s.scope = "Smell", s.docstring = "Analyze codebase for code smells using Clean Code principles with concurrent execution.", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1378}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "concurrency_config", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1379}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1384}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1386}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00230
MERGE (s:Variable {name: "connection_test", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1394}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "connection_test", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1396}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "detectors", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1404}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "concurrent_results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1409}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1418}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00231
MERGE (s:Variable {name: "results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1421}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1424}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1426}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1428}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "report", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1429}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00232
MERGE (s:Variable {name: "error_msg", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1435}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "analyze_specific_detector", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1440}) SET s.end_line = 1505, s.scope = "Smell", s.docstring = "Run a specific code smell detector.", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1451}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "detector_map", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1454}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "norm", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1471}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00233
MERGE (s:Variable {name: "normalized_map", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1472}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1478}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1480}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "detector", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1489}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Class {name: "_NoopNeo", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1492}) SET s.end_line = 1494, s.scope = "Smell";

// BATCH 00234
MERGE (s:Method {name: "run_query", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1493}) SET s.end_line = 1494, s.scope = "Smell._NoopNeo", s.signature = "async";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1495}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "smells", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1498}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "error_msg", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1503}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "analyze_multiple_detectors", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1508}) SET s.end_line = 1608, s.scope = "Smell", s.docstring = "Run multiple specific detectors concurrently.", s.signature = "async";

// BATCH 00235
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1519}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "concurrency_config", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1520}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "detector_map", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1523}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "normalized_map", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1540}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "norm_names", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1542}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00236
MERGE (s:Variable {name: "invalid_detectors", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1544}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "selected_detectors", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1548}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1552}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1554}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "_needs_graph", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1564}) SET s.end_line = 1584, s.scope = "Smell", s.signature = "def";

// BATCH 00237
MERGE (s:Variable {name: "graph_detectors", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1565}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "name", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1583}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Class {name: "_NoopNeo", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1586}) SET s.end_line = 1588, s.scope = "Smell";
MERGE (s:Method {name: "run_query", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1587}) SET s.end_line = 1588, s.scope = "Smell._NoopNeo", s.signature = "async";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1589}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00238
MERGE (s:Variable {name: "concurrent_results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1594}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "dict_results", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1601}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "error_msg", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1606}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Method {name: "analyze_codebase_export", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1611}) SET s.end_line = 1665, s.scope = "Smell", s.docstring = "Generate a smell report and return it as a File so callers can --export to host.
        Uses analyze_codebase for content, wraps as HTML when format=\'html\'.
        ", s.signature = "async";
MERGE (s:Variable {name: "report_text", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1621}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00239
MERGE (s:Variable {name: "fmt", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1627}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "summary_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1630}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "details_lines", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1631}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "in_details", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1632}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "in_details", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1635}) SET s.end_line = -1, s.scope = "Smell";

// BATCH 00240
MERGE (s:Method {name: "esc", filepath: "/app/workflows/smell/src/smell/main.py", start_line: 1639}) SET s.end_line = 1640, s.scope = "Smell", s.signature = "def";
MERGE (s:Variable {name: "summary_html", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1642}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "details_html", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1643}) SET s.end_line = -1, s.scope = "Smell";
MERGE (s:Variable {name: "html", filepath: "/app/workflows/smell/src/smell/main.py", line_number: 1645}) SET s.end_line = -1, s.scope = "Smell";
MERGE (f:File {filepath: "/app/workflows/graph/src/graph/utils.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/graph/src/graph/utils.py" ON MATCH SET f.language = "python";

// BATCH 00241
MERGE (s:Function {name: "dagger_json_file_to_pydantic", filepath: "/app/workflows/graph/src/graph/utils.py", start_line: 7}) SET s.end_line = 29, s.docstring = "
    Convert a Dagger JSON file to a list of Pydantic models.

    Args:
    json_file (dagger.File): The Dagger JSON file to convert.
    pydantic_model (type): The Pydantic model class to use for conversion.

    Returns:
    List: A list of Pydantic models.
    ", s.signature = "def";
MERGE (s:Function {name: "convert", filepath: "/app/workflows/graph/src/graph/utils.py", start_line: 19}) SET s.end_line = 27, s.signature = "async";
MERGE (s:Variable {name: "json_content", filepath: "/app/workflows/graph/src/graph/utils.py", line_number: 21}) SET s.end_line = -1;
MERGE (s:Variable {name: "data_list", filepath: "/app/workflows/graph/src/graph/utils.py", line_number: 24}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/workflows/smell/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/workflows/smell/pyproject.toml" ON MATCH SET f.language = "unknown";

// BATCH 00242
MERGE (f:File {filepath: "/app/workflows/graph/src/graph/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/graph/src/graph/main.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "Graph", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 15}) SET s.end_line = 1016;
MERGE (s:Variable {name: "config", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 16}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "config_file", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 17}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "neo_service", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 18}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00243
MERGE (s:Variable {name: "neo_data", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 19}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "create", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 22}) SET s.end_line = 28, s.scope = "Graph", s.docstring = "Create a Graph object from a YAML config file.", s.signature = "async";
MERGE (s:Variable {name: "config_str", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 26}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "config_dict", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 27}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_setup_logging", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 30}) SET s.end_line = 36, s.scope = "Graph", s.docstring = "Setup structured logging.", s.signature = "def";

// BATCH 00244
MERGE (s:Method {name: "_get_processing_config", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 38}) SET s.end_line = 56, s.scope = "Graph", s.docstring = "Extract processing configuration from YAML config.", s.signature = "def";
MERGE (s:Variable {name: "config_obj", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 40}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "concurrency_config", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 44}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "indexing_config", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 45}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_escape_cypher_string", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 58}) SET s.end_line = 63, s.scope = "Graph", s.docstring = "Escape special characters in Cypher string values.", s.signature = "def";

// BATCH 00245
MERGE (s:Method {name: "_build_file_cypher", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 65}) SET s.end_line = 70, s.scope = "Graph", s.docstring = "Build Cypher query for creating a file node ", s.signature = "def";
MERGE (s:Variable {name: "escaped_filepath", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 67}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "escaped_language", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 68}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_build_symbol_cypher", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 72}) SET s.end_line = 93, s.scope = "Graph", s.docstring = "Build Cypher query for creating a symbol node.", s.signature = "def";
MERGE (s:Variable {name: "symbol_name", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 74}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00246
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 75}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "start_line", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 76}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "end_line", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 77}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "escaped_filepath", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 78}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "properties", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 81}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00247
MERGE (s:Variable {name: "escaped_value", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 84}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "props_string", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 87}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_build_import_cypher", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 95}) SET s.end_line = 100, s.scope = "Graph", s.docstring = "Build Cypher query for creating import relationships - OPTIMIZED VERSION.", s.signature = "def";
MERGE (s:Variable {name: "escaped_from", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 97}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "escaped_to", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 98}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00248
MERGE (s:Method {name: "_build_relationship_cypher", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 102}) SET s.end_line = 105, s.scope = "Graph", s.docstring = "Build DEFINED_IN relationship query.", s.signature = "def";
MERGE (s:Variable {name: "escaped_filepath", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 104}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_build_symbol_relationship_cypher", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 107}) SET s.end_line = 118, s.scope = "Graph", s.docstring = "Build Cypher query for creating symbol-to-symbol relationships within a file.", s.signature = "def";
MERGE (s:Variable {name: "escaped_from", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 110}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "escaped_to", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 111}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00249
MERGE (s:Variable {name: "escaped_filepath", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 112}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_build_cross_file_symbol_relationship_cypher", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 120}) SET s.end_line = 129, s.scope = "Graph", s.docstring = "Build Cypher for creating symbol-to-symbol relationships across files.", s.signature = "def";
MERGE (s:Variable {name: "ef", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 124}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_resolve_relative_import", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 131}) SET s.end_line = 169, s.scope = "Graph", s.docstring = "Resolve relative import paths to absolute paths.", s.signature = "def";
MERGE (s:Variable {name: "current_dir", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 137}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00250
MERGE (s:Variable {name: "relative_path", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 142}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "relative_path", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 145}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "resolved_path", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 150}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "potential_path", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 157}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "index_path", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 163}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00251
MERGE (s:Method {name: "_extract_symbol_references", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 171}) SET s.end_line = 216, s.scope = "Graph", s.docstring = "Extract CALLS and REFERENCES relationships between symbols.", s.signature = "def";
MERGE (s:Variable {name: "relationships", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 173}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbol_map", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 176}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 178}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbols_in_line", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 182}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00252
MERGE (s:Variable {name: "current_line", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 189}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "containing_symbol", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 199}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "rel_query", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 202}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "containing_symbol", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 208}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "rel_query", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 211}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00253
MERGE (s:Method {name: "_find_containing_symbol", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 218}) SET s.end_line = 244, s.scope = "Graph", s.docstring = "Find which symbol (function/class/method) contains the given line number.", s.signature = "def";
MERGE (s:Variable {name: "containing_symbols", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 220}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "start_line", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 223}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "end_line", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 225}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 231}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00254
MERGE (s:Method {name: "_execute_queries_concurrently", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 246}) SET s.end_line = 285, s.scope = "Graph", s.docstring = "Execute queries concurrently with controlled concurrency.", s.signature = "async";
MERGE (s:Variable {name: "semaphore", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 257}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "successful", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 258}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "failed", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 259}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "execute_with_limit", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 261}) SET s.end_line = 276, s.scope = "Graph", s.signature = "async";

// BATCH 00255
MERGE (s:Method {name: "_execute_queries_in_concurrent_batches", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 287}) SET s.end_line = 329, s.scope = "Graph", s.docstring = "Execute queries in small concurrent batches for optimal performance.", s.signature = "async";
MERGE (s:Variable {name: "batches", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 300}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "semaphore", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 302}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "total_successful", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 303}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "total_failed", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 304}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00256
MERGE (s:Method {name: "execute_batch_with_limit", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 306}) SET s.end_line = 320, s.scope = "Graph", s.signature = "async";
MERGE (s:Variable {name: "batch_query", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 309}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_safe_build_graph_data_for_file", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 331}) SET s.end_line = 359, s.scope = "Graph", s.docstring = "Safely process a single file and return graph data instead of executing queries.", s.signature = "async";
MERGE (s:Variable {name: "content", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 340}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 348}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00257
MERGE (s:Method {name: "_build_graph_data_for_file", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 361}) SET s.end_line = 491, s.scope = "Graph", s.docstring = "Process a file and return Cypher queries instead of executing them.", s.signature = "async";
MERGE (s:Variable {name: "excluded_extensions", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 371}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "ext", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 376}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "config_obj", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 384}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "valid_extensions", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 387}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00258
MERGE (s:Variable {name: "queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 393}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "imports", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 394}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 395}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbol_relationships", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 396}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbol_names", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 397}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00259
MERGE (s:Variable {name: "agent_utils", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 401}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "code_file_json", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 402}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "json_content", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 403}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "code_file_dict", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 404}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "language", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 410}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00260
MERGE (s:Variable {name: "parsed_symbols", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 411}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "parsed_imports", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 413}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbol_name", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 430}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 432}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "relationship_queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 441}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00261
MERGE (s:Variable {name: "import_file_path", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 457}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "config_query", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 476}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "_process_files_with_semaphore", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 493}) SET s.end_line = 539, s.scope = "Graph", s.docstring = "Process files with semaphore-controlled concurrency and collect all queries.", s.signature = "async";
MERGE (s:Variable {name: "semaphore", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 504}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 505}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00262
MERGE (s:Variable {name: "all_queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 506}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "all_imports", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 507}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "all_symbols", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 508}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "all_symbol_relationships", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 509}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "all_symbol_names", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 510}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00263
MERGE (s:Method {name: "process_with_limit", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 512}) SET s.end_line = 524, s.scope = "Graph", s.signature = "async";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 514}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "processed", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 532}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "failed", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 533}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "setup_neo", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 542}) SET s.end_line = 573, s.scope = "Graph", s.docstring = "Set up Neo4j service and return connection status.", s.signature = "async";

// BATCH 00264
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 549}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "test_result", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 564}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "clear", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 566}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "build_graph_for_repository", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 576}) SET s.end_line = 815, s.scope = "Graph", s.docstring = "Build a graph representation of an entire repository using concurrent query execution.", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 588}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00265
MERGE (s:Variable {name: "processing_config", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 589}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "source", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 600}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "container", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 610}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "work_dir", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 621}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "file_extensions", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 625}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00266
MERGE (s:Variable {name: "find_cmd", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 630}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "ext", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 634}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "file_list", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 666}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "files", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 669}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "files", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 670}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00267
MERGE (s:Variable {name: "constraints_and_indexes", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 689}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "constraint_name", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 704}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "relationship_queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 719}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "rel_query", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 721}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "import_queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 732}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00268
MERGE (s:Variable {name: "unique_imports", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 733}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "import_query", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 736}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbol_rel_successful", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 751}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbol_rel_failed", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 751}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "file_to_imports", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 756}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00269
MERGE (s:Variable {name: "symbols_by_file", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 759}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "cross_file_queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 764}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "agent_utils", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 765}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "a_content", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 768}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "code_file_json", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 770}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00270
MERGE (s:Variable {name: "json_content", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 771}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "a_dict", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 772}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "a_symbols", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 773}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "a_symbol_map", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 774}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "a_lines", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 775}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00271
MERGE (s:Variable {name: "container_symbol", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 784}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "rel_type", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 787}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "test_result", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 809}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Method {name: "build_graph_for_directory", filepath: "/app/workflows/graph/src/graph/main.py", start_line: 818}) SET s.end_line = 1016, s.scope = "Graph", s.docstring = "Build a graph representation of a locally checked-out repository (attached directory mode).
        Mirrors build_graph_for_repository, but uses a local path for the source tree.
        ", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 829}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00272
MERGE (s:Variable {name: "processing_config", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 830}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "source", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 841}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "container", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 846}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "work_dir", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 855}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "file_extensions", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 859}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00273
MERGE (s:Variable {name: "find_cmd", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 863}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "ext", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 865}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "file_list", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 895}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "files", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 896}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "constraints_and_indexes", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 914}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00274
MERGE (s:Variable {name: "constraint_name", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 929}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "relationship_queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 942}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "import_queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 951}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "file_to_imports", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 965}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "symbols_by_file", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 968}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00275
MERGE (s:Variable {name: "cross_file_queries", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 972}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "agent_utils", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 973}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "a_content", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 976}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "code_file_json", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 977}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "a_dict", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 978}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00276
MERGE (s:Variable {name: "a_symbol_map", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 979}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "a_lines", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 980}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "container_symbol", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 987}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "rel_type", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 990}) SET s.end_line = -1, s.scope = "Graph";
MERGE (s:Variable {name: "test_result", filepath: "/app/workflows/graph/src/graph/main.py", line_number: 1008}) SET s.end_line = -1, s.scope = "Graph";

// BATCH 00277
MERGE (f:File {filepath: "/app/workflows/graph/src/graph/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/graph/src/graph/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/graph/src/graph/operations/relationship_extractor.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "RelationshipExtractor", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 9}) SET s.end_line = 305;
MERGE (s:Method {name: "extract_relationships", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 13}) SET s.end_line = 34, s.scope = "RelationshipExtractor", s.docstring = "Extract relationships between code symbols", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 18}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00278
MERGE (s:Variable {name: "symbol_map", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 22}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_internal_relationships", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 37}) SET s.end_line = 85, s.scope = "RelationshipExtractor", s.docstring = "Extract relationships between symbols within the same file", s.signature = "async";
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 43}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "symbol_name", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 44}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "line_number", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 45}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00279
MERGE (s:Variable {name: "base_symbol", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 51}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "base_type", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 52}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "called_symbol", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 71}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "called_type", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 72}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_file_imports", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 88}) SET s.end_line = 132, s.scope = "RelationshipExtractor", s.docstring = "Extract file import relationships", s.signature = "async";

// BATCH 00280
MERGE (s:Variable {name: "language", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 97}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "content", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 98}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 105}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 106}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_python_imports", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 135}) SET s.end_line = 168, s.scope = "RelationshipExtractor", s.docstring = "Extract Python import statements", s.signature = "async";

// BATCH 00281
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 138}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 147}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "possible_paths", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 154}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_js_imports", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 171}) SET s.end_line = 221, s.scope = "RelationshipExtractor", s.docstring = "Extract JavaScript/TypeScript import statements", s.signature = "async";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 174}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00282
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 185}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "current_dir", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 192}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "abs_path", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 193}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "possible_paths", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 198}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_java_imports", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 224}) SET s.end_line = 239, s.scope = "RelationshipExtractor", s.docstring = "Extract Java import statements", s.signature = "async";

// BATCH 00283
MERGE (s:Variable {name: "pattern", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 226}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 230}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_go_imports", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 242}) SET s.end_line = 283, s.scope = "RelationshipExtractor", s.docstring = "Extract Go import statements", s.signature = "async";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 244}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "import_line", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 245}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00284
MERGE (s:Variable {name: "single_match", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 249}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 251}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 264}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "import_line", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 265}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 270}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00285
MERGE (s:Variable {name: "pkg_match", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 273}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 275}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_rust_imports", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", start_line: 286}) SET s.end_line = 305, s.scope = "RelationshipExtractor", s.docstring = "Extract Rust import statements", s.signature = "async";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 288}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/graph/src/graph/operations/relationship_extractor.py", line_number: 296}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00286
MERGE (f:File {filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/graph/src/graph/operations/import_analyzer.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "ImportAnalyzer", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 9}) SET s.end_line = 278;
MERGE (s:Method {name: "analyze_file_imports", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 13}) SET s.end_line = 57, s.scope = "ImportAnalyzer", s.docstring = "
        Analyze a file for imports without using AST parsing.
        Returns the set of imported files and creates relationships in Neo4j.
        ", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 22}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "language", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 23}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00287
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 24}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 33}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 36}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 39}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 42}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00288
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 45}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_detect_language", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 60}) SET s.end_line = 81, s.scope = "ImportAnalyzer", s.docstring = "Detect programming language from file extension.", s.signature = "def";
MERGE (s:Variable {name: "ext", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 62}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "language_map", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 64}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_analyze_python_imports", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 84}) SET s.end_line = 139, s.scope = "ImportAnalyzer", s.docstring = "Extract Python import statements using regex.", s.signature = "def";

// BATCH 00289
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 86}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "current_dir", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 87}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 88}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 91}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 102}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00290
MERGE (s:Variable {name: "dots", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 107}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "relative_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 108}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "parent_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 111}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "parent_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 113}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 116}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00291
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 119}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "possible_paths", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 126}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 134}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 136}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_analyze_js_imports", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 142}) SET s.end_line = 188, s.scope = "ImportAnalyzer", s.docstring = "Extract JavaScript/TypeScript import statements using regex.", s.signature = "def";

// BATCH 00292
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 144}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "current_dir", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 145}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 146}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 149}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 158}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00293
MERGE (s:Variable {name: "abs_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 165}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "possible_paths", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 170}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 177}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 179}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 183}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00294
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 185}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_analyze_java_imports", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 191}) SET s.end_line = 203, s.scope = "ImportAnalyzer", s.docstring = "Extract Java import statements using regex.", s.signature = "def";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 193}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 194}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "pattern", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 196}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00295
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 200}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_analyze_go_imports", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 206}) SET s.end_line = 236, s.scope = "ImportAnalyzer", s.docstring = "Extract Go import statements using regex.", s.signature = "def";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 208}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 209}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 211}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00296
MERGE (s:Variable {name: "single_match", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 215}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 217}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 223}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 228}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "pkg_match", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 231}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00297
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 233}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_analyze_rust_imports", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 239}) SET s.end_line = 255, s.scope = "ImportAnalyzer", s.docstring = "Extract Rust import statements using regex.", s.signature = "def";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 241}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 242}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 244}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00298
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", line_number: 252}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_create_import_relationships", filepath: "/app/workflows/graph/src/graph/operations/import_analyzer.py", start_line: 258}) SET s.end_line = 278, s.scope = "ImportAnalyzer", s.docstring = "Create import relationships in Neo4j.", s.signature = "async";
MERGE (f:File {filepath: "/app/workflows/graph/src/graph/models/code_file.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/graph/src/graph/models/code_file.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "CodeSymbol", filepath: "/app/workflows/graph/src/graph/models/code_file.py", start_line: 4}) SET s.end_line = 13;
MERGE (s:Variable {name: "name", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 5}) SET s.end_line = -1, s.scope = "CodeSymbol";

// BATCH 00299
MERGE (s:Variable {name: "type", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 6}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "line_number", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 7}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "column", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 8}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "end_line_number", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 9}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "end_column", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 10}) SET s.end_line = -1, s.scope = "CodeSymbol";

// BATCH 00300
MERGE (s:Variable {name: "scope", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 11}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "signature", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 12}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "visibility", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 13}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Class {name: "CodeFile", filepath: "/app/workflows/graph/src/graph/models/code_file.py", start_line: 15}) SET s.end_line = 19;
MERGE (s:Variable {name: "content", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 16}) SET s.end_line = -1, s.scope = "CodeFile";

// BATCH 00301
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 17}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "language", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 18}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/graph/src/graph/models/code_file.py", line_number: 19}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (f:File {filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/graph/src/graph/services/neo4j_service.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "Neo4jService", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 9}) SET s.end_line = 294;

// BATCH 00302
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 12}) SET s.end_line = 39, s.scope = "Neo4jService", s.docstring = "Initialize Neo4jService with user and password.", s.signature = "def";
MERGE (s:Method {name: "create_neo4j_service", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 41}) SET s.end_line = 60, s.scope = "Neo4jService", s.docstring = "Create a Neo4j service as a Dagger service", s.signature = "async";
MERGE (s:Method {name: "create_neo4j_client", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 62}) SET s.end_line = 82, s.scope = "Neo4jService", s.docstring = "Create a Neo4j client container with cypher-shell", s.signature = "async";
MERGE (s:Variable {name: "source", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 64}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "cypher_cli", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 70}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00303
MERGE (s:Method {name: "run_query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 84}) SET s.end_line = 113, s.scope = "Neo4jService", s.docstring = "Run a query against the Neo4j service with readiness probe", s.signature = "async";
MERGE (s:Variable {name: "client", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 91}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "client", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 94}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "test_connection", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 115}) SET s.end_line = 117, s.scope = "Neo4jService", s.docstring = "Test connection to Neo4j service", s.signature = "async";
MERGE (s:Method {name: "connect", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 119}) SET s.end_line = 127, s.scope = "Neo4jService", s.docstring = "Verify connection to Neo4j", s.signature = "def";

// BATCH 00304
MERGE (s:Method {name: "clear_database", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 129}) SET s.end_line = 138, s.scope = "Neo4jService", s.docstring = "Clear all nodes and relationships from the database", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 133}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "add_file_node", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 140}) SET s.end_line = 153, s.scope = "Neo4jService", s.docstring = "Add a file node to the graph", s.signature = "async";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 144}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "language", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 145}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00305
MERGE (s:Variable {name: "query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 148}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "add_symbol", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 155}) SET s.end_line = 205, s.scope = "Neo4jService", s.docstring = "Add a symbol node to the graph with connection to its file", s.signature = "async";
MERGE (s:Variable {name: "properties", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 159}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "name", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 163}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 164}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00306
MERGE (s:Variable {name: "end_line_str", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 167}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "start_line_str", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 168}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "props", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 171}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "escaped_v", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 179}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "properties_str", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 182}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00307
MERGE (s:Variable {name: "query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 185}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "add_relationship", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 207}) SET s.end_line = 230, s.scope = "Neo4jService", s.docstring = "Add a relationship between two code elements", s.signature = "async";
MERGE (s:Variable {name: "from_name", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 213}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "from_filepath", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 214}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "to_name", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 215}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00308
MERGE (s:Variable {name: "to_filepath", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 216}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 219}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "execute_query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", start_line: 232}) SET s.end_line = 294, s.scope = "Neo4jService", s.docstring = "Execute a parameterized Cypher query and return structured results.
        
        This method is used by the CodeGraphInterface to provide a clean API
        for LLMs to query the code graph.
        
        Args:
            query: Cypher query with parameter placeholders
            params: Dictionary of parameters to inject into the query
        
        Returns:
            List of result records as dictionaries
        ", s.signature = "async";
MERGE (s:Variable {name: "params", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 247}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "formatted_query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 251}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00309
MERGE (s:Variable {name: "formatted_query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 254}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "formatted_query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 257}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "formatted_query", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 260}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "result_text", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 264}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 268}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00310
MERGE (s:Variable {name: "headers", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 274}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 277}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "values", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 282}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "result_dict", filepath: "/app/workflows/graph/src/graph/services/neo4j_service.py", line_number: 286}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (f:File {filepath: "/app/workflows/graph/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/workflows/graph/pyproject.toml" ON MATCH SET f.language = "unknown";

// BATCH 00311
MERGE (f:File {filepath: "/app/workflows/index/src/index/template.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/template.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "get_rag_naming_agent_template", filepath: "/app/workflows/index/src/index/template.py", start_line: 7}) SET s.end_line = 38, s.docstring = "
    Return the system prompt template for the RAG naming agent.
    ", s.signature = "def";
MERGE (s:Function {name: "get_meaningful_names_agent_template", filepath: "/app/workflows/index/src/index/template.py", start_line: 41}) SET s.end_line = 67, s.docstring = "
    Return the system prompt template for the meaningful names agent.
    ", s.signature = "def";
MERGE (f:File {filepath: "/app/workflows/index/src/index/utils/llm.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/utils/llm.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "get_llm_credentials", filepath: "/app/workflows/index/src/index/utils/llm.py", start_line: 10}) SET s.end_line = 56, s.docstring = "
    Determines the LLM base URL and retrieves the plaintext API key based on the provider.

    Args:
        provider: The name of the LLM provider (\'openrouter\' or \'openai\').
        open_router_key: The Dagger secret for the OpenRouter API key.
        openai_key: The Dagger secret for the OpenAI API key.

    Returns:
        A tuple containing (base_url, api_key_plain).
        base_url is None for OpenAI default.

    Raises:
        ValueError: If the provider is unsupported or the required key is missing.
    ", s.signature = "async";

// BATCH 00312
MERGE (s:Variable {name: "base_url", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 30}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 31}) SET s.end_line = -1;
MERGE (s:Variable {name: "base_url", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 37}) SET s.end_line = -1;
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 38}) SET s.end_line = -1;
MERGE (s:Variable {name: "base_url", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 44}) SET s.end_line = -1;

// BATCH 00313
MERGE (s:Variable {name: "api_key_secret", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 45}) SET s.end_line = -1;
MERGE (s:Function {name: "create_llm_model", filepath: "/app/workflows/index/src/index/utils/llm.py", start_line: 59}) SET s.end_line = 90, s.docstring = "
    Creates the Pydantic AI model instance (currently OpenAIModel).

    Args:
        api_key: The plaintext API key.
        base_url: The base URL for the API (None for OpenAI default).
        model_name: The specific model name to use.

    Returns:
        An instance of OpenAIModel.

    Raises:
        Exception: If initialization of the provider or model fails.
    ", s.signature = "async";
MERGE (s:Variable {name: "llm_provider", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 79}) SET s.end_line = -1;
MERGE (s:Variable {name: "effective_base_url", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 82}) SET s.end_line = -1;
MERGE (s:Variable {name: "pydantic_ai_model", filepath: "/app/workflows/index/src/index/utils/llm.py", line_number: 83}) SET s.end_line = -1;

// BATCH 00314
MERGE (f:File {filepath: "/app/workflows/index/src/index/models.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/models.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "ProcessingConfig", filepath: "/app/workflows/index/src/index/models.py", start_line: 8}) SET s.end_line = 16;
MERGE (s:Variable {name: "max_semantic_chunk_lines", filepath: "/app/workflows/index/src/index/models.py", line_number: 10}) SET s.end_line = -1, s.scope = "ProcessingConfig";
MERGE (s:Variable {name: "fallback_chunk_size", filepath: "/app/workflows/index/src/index/models.py", line_number: 11}) SET s.end_line = -1, s.scope = "ProcessingConfig";
MERGE (s:Variable {name: "max_file_size", filepath: "/app/workflows/index/src/index/models.py", line_number: 12}) SET s.end_line = -1, s.scope = "ProcessingConfig";

// BATCH 00315
MERGE (s:Variable {name: "batch_size", filepath: "/app/workflows/index/src/index/models.py", line_number: 13}) SET s.end_line = -1, s.scope = "ProcessingConfig";
MERGE (s:Variable {name: "max_concurrent", filepath: "/app/workflows/index/src/index/models.py", line_number: 14}) SET s.end_line = -1, s.scope = "ProcessingConfig";
MERGE (s:Variable {name: "embedding_model", filepath: "/app/workflows/index/src/index/models.py", line_number: 15}) SET s.end_line = -1, s.scope = "ProcessingConfig";
MERGE (s:Variable {name: "embedding_batch_size", filepath: "/app/workflows/index/src/index/models.py", line_number: 16}) SET s.end_line = -1, s.scope = "ProcessingConfig";
MERGE (s:Class {name: "ChunkData", filepath: "/app/workflows/index/src/index/models.py", start_line: 20}) SET s.end_line = 28;

// BATCH 00316
MERGE (s:Variable {name: "content", filepath: "/app/workflows/index/src/index/models.py", line_number: 22}) SET s.end_line = -1, s.scope = "ChunkData";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/index/src/index/models.py", line_number: 23}) SET s.end_line = -1, s.scope = "ChunkData";
MERGE (s:Variable {name: "start_line", filepath: "/app/workflows/index/src/index/models.py", line_number: 24}) SET s.end_line = -1, s.scope = "ChunkData";
MERGE (s:Variable {name: "end_line", filepath: "/app/workflows/index/src/index/models.py", line_number: 25}) SET s.end_line = -1, s.scope = "ChunkData";
MERGE (s:Variable {name: "language", filepath: "/app/workflows/index/src/index/models.py", line_number: 26}) SET s.end_line = -1, s.scope = "ChunkData";

// BATCH 00317
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/models.py", line_number: 27}) SET s.end_line = -1, s.scope = "ChunkData";
MERGE (s:Variable {name: "context", filepath: "/app/workflows/index/src/index/models.py", line_number: 28}) SET s.end_line = -1, s.scope = "ChunkData";
MERGE (s:Class {name: "LLMCredentials", filepath: "/app/workflows/index/src/index/models.py", start_line: 31}) SET s.end_line = 34;
MERGE (s:Variable {name: "base_url", filepath: "/app/workflows/index/src/index/models.py", line_number: 33}) SET s.end_line = -1, s.scope = "LLMCredentials";
MERGE (s:Variable {name: "api_key", filepath: "/app/workflows/index/src/index/models.py", line_number: 34}) SET s.end_line = -1, s.scope = "LLMCredentials";

// BATCH 00318
MERGE (f:File {filepath: "/app/workflows/index/src/index/utils/embeddings.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/utils/embeddings.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "generate_embeddings", filepath: "/app/workflows/index/src/index/utils/embeddings.py", start_line: 6}) SET s.end_line = 41, s.docstring = "
    Generate embeddings for the given text using OpenAI API.
    ", s.signature = "async";
MERGE (s:Variable {name: "api_key", filepath: "/app/workflows/index/src/index/utils/embeddings.py", line_number: 16}) SET s.end_line = -1;
MERGE (s:Variable {name: "client", filepath: "/app/workflows/index/src/index/utils/embeddings.py", line_number: 23}) SET s.end_line = -1;
MERGE (s:Variable {name: "response", filepath: "/app/workflows/index/src/index/utils/embeddings.py", line_number: 26}) SET s.end_line = -1;

// BATCH 00319
MERGE (f:File {filepath: "/app/workflows/index/src/index/utils/code_parser.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/utils/code_parser.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "SymbolType", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 9}) SET s.end_line = 19;
MERGE (s:Constant {name: "VARIABLE", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 10}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "FUNCTION", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 11}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "CLASS", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 12}) SET s.end_line = -1, s.scope = "SymbolType";

// BATCH 00320
MERGE (s:Constant {name: "INTERFACE", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 13}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "ENUM", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 14}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "STRUCT", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 15}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "TRAIT", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 16}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "CONSTANT", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 17}) SET s.end_line = -1, s.scope = "SymbolType";

// BATCH 00321
MERGE (s:Constant {name: "METHOD", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 18}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "PROPERTY", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 19}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Class {name: "CodeSymbol", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 23}) SET s.end_line = 33;
MERGE (s:Variable {name: "name", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 25}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 26}) SET s.end_line = -1, s.scope = "CodeSymbol";

// BATCH 00322
MERGE (s:Variable {name: "line_number", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 27}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "column", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 28}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "end_line", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 29}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "end_column", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 30}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "scope", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 31}) SET s.end_line = -1, s.scope = "CodeSymbol";

// BATCH 00323
MERGE (s:Variable {name: "signature", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 32}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "visibility", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 33}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Class {name: "CodeFile", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 37}) SET s.end_line = 55;
MERGE (s:Variable {name: "content", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 39}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 40}) SET s.end_line = -1, s.scope = "CodeFile";

// BATCH 00324
MERGE (s:Variable {name: "language", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 41}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 42}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 43}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Method {name: "__post_init__", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 45}) SET s.end_line = 46, s.scope = "CodeFile", s.signature = "def";
MERGE (s:Method {name: "get_context_around_line", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 48}) SET s.end_line = 55, s.scope = "CodeFile", s.docstring = "Get a few lines of context around the specified line.", s.signature = "def";

// BATCH 00325
MERGE (s:Variable {name: "start", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 50}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "end", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 51}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "context", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 52}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Function {name: "detect_language", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 58}) SET s.end_line = 86, s.docstring = "Detect the programming language from the file extension.", s.signature = "def";
MERGE (s:Variable {name: "ext", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 60}) SET s.end_line = -1;

// BATCH 00326
MERGE (s:Variable {name: "language_map", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 61}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_python_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 89}) SET s.end_line = 174, s.docstring = "Parse Python code to extract symbols using AST.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 91}) SET s.end_line = -1;
MERGE (s:Variable {name: "tree", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 94}) SET s.end_line = -1;
MERGE (s:Variable {name: "current_scope", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 97}) SET s.end_line = -1;

// BATCH 00327
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 103}) SET s.end_line = -1;
MERGE (s:Variable {name: "args_list", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 106}) SET s.end_line = -1;
MERGE (s:Variable {name: "defaults", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 111}) SET s.end_line = -1;
MERGE (s:Variable {name: "arg_signatures", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 115}) SET s.end_line = -1;
MERGE (s:Variable {name: "default_val", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 121}) SET s.end_line = -1;

// BATCH 00328
MERGE (s:Variable {name: "signature", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 126}) SET s.end_line = -1;
MERGE (s:Variable {name: "full_name", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 128}) SET s.end_line = -1;
MERGE (s:Variable {name: "old_scope", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 142}) SET s.end_line = -1;
MERGE (s:Variable {name: "current_scope", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 143}) SET s.end_line = -1;
MERGE (s:Variable {name: "current_scope", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 156}) SET s.end_line = -1;

// BATCH 00329
MERGE (s:Variable {name: "is_constant", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 162}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_javascript_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 177}) SET s.end_line = 253, s.docstring = "Parse JavaScript/TypeScript code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 179}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_patterns", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 182}) SET s.end_line = -1;
MERGE (s:Variable {name: "class_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 193}) SET s.end_line = -1;

// BATCH 00330
MERGE (s:Variable {name: "variable_patterns", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 194}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 206}) SET s.end_line = -1;
MERGE (s:Variable {name: "name", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 212}) SET s.end_line = -1;
MERGE (s:Variable {name: "name", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 214}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 237}) SET s.end_line = -1;

// BATCH 00331
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 239}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 241}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 243}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_java_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 256}) SET s.end_line = 319, s.docstring = "Parse Java code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 258}) SET s.end_line = -1;

// BATCH 00332
MERGE (s:Variable {name: "class_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 261}) SET s.end_line = -1;
MERGE (s:Variable {name: "interface_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 262}) SET s.end_line = -1;
MERGE (s:Variable {name: "enum_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 263}) SET s.end_line = -1;
MERGE (s:Variable {name: "method_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 265}) SET s.end_line = -1;
MERGE (s:Variable {name: "field_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 266}) SET s.end_line = -1;

// BATCH 00333
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 269}) SET s.end_line = -1;
MERGE (s:Variable {name: "is_constant", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 310}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_c_cpp_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 322}) SET s.end_line = 393, s.docstring = "Parse C/C++ code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 324}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 327}) SET s.end_line = -1;

// BATCH 00334
MERGE (s:Variable {name: "class_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 328}) SET s.end_line = -1;
MERGE (s:Variable {name: "variable_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 329}) SET s.end_line = -1;
MERGE (s:Variable {name: "enum_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 330}) SET s.end_line = -1;
MERGE (s:Variable {name: "define_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 331}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 334}) SET s.end_line = -1;

// BATCH 00335
MERGE (s:Variable {name: "line", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 337}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 351}) SET s.end_line = -1;
MERGE (s:Variable {name: "is_constant", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 384}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_go_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 396}) SET s.end_line = 471, s.docstring = "Parse Go code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 398}) SET s.end_line = -1;

// BATCH 00336
MERGE (s:Variable {name: "function_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 401}) SET s.end_line = -1;
MERGE (s:Variable {name: "method_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 402}) SET s.end_line = -1;
MERGE (s:Variable {name: "struct_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 403}) SET s.end_line = -1;
MERGE (s:Variable {name: "interface_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 404}) SET s.end_line = -1;
MERGE (s:Variable {name: "const_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 405}) SET s.end_line = -1;

// BATCH 00337
MERGE (s:Variable {name: "var_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 406}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 409}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_rust_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 474}) SET s.end_line = 557, s.docstring = "Parse Rust code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 476}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 479}) SET s.end_line = -1;

// BATCH 00338
MERGE (s:Variable {name: "struct_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 480}) SET s.end_line = -1;
MERGE (s:Variable {name: "trait_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 481}) SET s.end_line = -1;
MERGE (s:Variable {name: "enum_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 482}) SET s.end_line = -1;
MERGE (s:Variable {name: "impl_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 483}) SET s.end_line = -1;
MERGE (s:Variable {name: "const_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 484}) SET s.end_line = -1;

// BATCH 00339
MERGE (s:Variable {name: "let_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 485}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 488}) SET s.end_line = -1;
MERGE (s:Variable {name: "line", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 491}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_ruby_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 560}) SET s.end_line = 640, s.docstring = "Parse Ruby code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 562}) SET s.end_line = -1;

// BATCH 00340
MERGE (s:Variable {name: "class_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 565}) SET s.end_line = -1;
MERGE (s:Variable {name: "module_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 566}) SET s.end_line = -1;
MERGE (s:Variable {name: "method_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 567}) SET s.end_line = -1;
MERGE (s:Variable {name: "constant_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 568}) SET s.end_line = -1;
MERGE (s:Variable {name: "attr_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 569}) SET s.end_line = -1;

// BATCH 00341
MERGE (s:Variable {name: "var_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 570}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 573}) SET s.end_line = -1;
MERGE (s:Variable {name: "line", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 576}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 625}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 627}) SET s.end_line = -1;

// BATCH 00342
MERGE (s:Variable {name: "var_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 629}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 631}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_php_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 643}) SET s.end_line = 750, s.docstring = "Parse PHP code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 645}) SET s.end_line = -1;
MERGE (s:Variable {name: "class_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 648}) SET s.end_line = -1;

// BATCH 00343
MERGE (s:Variable {name: "interface_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 649}) SET s.end_line = -1;
MERGE (s:Variable {name: "trait_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 650}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 651}) SET s.end_line = -1;
MERGE (s:Variable {name: "method_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 652}) SET s.end_line = -1;
MERGE (s:Variable {name: "property_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 653}) SET s.end_line = -1;

// BATCH 00344
MERGE (s:Variable {name: "const_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 654}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 655}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 658}) SET s.end_line = -1;
MERGE (s:Variable {name: "line", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 661}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 702}) SET s.end_line = -1;

// BATCH 00345
MERGE (s:Variable {name: "visibility", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 704}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 706}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 718}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 720}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 722}) SET s.end_line = -1;

// BATCH 00346
MERGE (s:Function {name: "parse_generic_code", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 753}) SET s.end_line = 809, s.docstring = "Parse code generically using regex patterns for common symbols.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 755}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 758}) SET s.end_line = -1;
MERGE (s:Variable {name: "class_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 759}) SET s.end_line = -1;
MERGE (s:Variable {name: "variable_pattern", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 760}) SET s.end_line = -1;

// BATCH 00347
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 777}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 779}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 781}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 783}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 785}) SET s.end_line = -1;

// BATCH 00348
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 798}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 800}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_code_file", filepath: "/app/workflows/index/src/index/utils/code_parser.py", start_line: 812}) SET s.end_line = 842, s.docstring = "Parse a code file to extract symbols based on the language.", s.signature = "def";
MERGE (s:Variable {name: "language", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 814}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 815}) SET s.end_line = -1;

// BATCH 00349
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 819}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 821}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 823}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 825}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 827}) SET s.end_line = -1;

// BATCH 00350
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 829}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 831}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 833}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/workflows/index/src/index/utils/code_parser.py", line_number: 835}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/workflows/index/src/index/utils/file.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/utils/file.py" ON MATCH SET f.language = "python";

// BATCH 00351
MERGE (s:Function {name: "get_file_size", filepath: "/app/workflows/index/src/index/utils/file.py", start_line: 5}) SET s.end_line = 15, s.docstring = "Get the size of a file inside a container.", s.signature = "async";
MERGE (s:Variable {name: "size_str", filepath: "/app/workflows/index/src/index/utils/file.py", line_number: 9}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/utils/llm_neo4j_interface.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "CodeGraphInterface", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 7}) SET s.end_line = 168;
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 10}) SET s.end_line = 12, s.scope = "CodeGraphInterface", s.signature = "def";

// BATCH 00352
MERGE (s:Method {name: "get_file_structure", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 14}) SET s.end_line = 24, s.scope = "CodeGraphInterface", s.docstring = "Get the structure of files in the codebase", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 16}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "get_function_details", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 26}) SET s.end_line = 34, s.scope = "CodeGraphInterface", s.docstring = "Get details about a specific function", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 28}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "get_function_callers", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 36}) SET s.end_line = 43, s.scope = "CodeGraphInterface", s.docstring = "Find all callers of a specific function", s.signature = "async";

// BATCH 00353
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 38}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "get_class_hierarchy", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 45}) SET s.end_line = 51, s.scope = "CodeGraphInterface", s.docstring = "Get class inheritance hierarchy", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 47}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "get_module_dependencies", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 53}) SET s.end_line = 61, s.scope = "CodeGraphInterface", s.docstring = "Get files imported by a specific file", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 55}) SET s.end_line = -1, s.scope = "CodeGraphInterface";

// BATCH 00354
MERGE (s:Method {name: "get_dependent_files", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 63}) SET s.end_line = 71, s.scope = "CodeGraphInterface", s.docstring = "Get files that import this file", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 65}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "get_import_graph", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 73}) SET s.end_line = 81, s.scope = "CodeGraphInterface", s.docstring = "Get the import graph of the codebase up to a certain depth", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 75}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "find_circular_imports", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 83}) SET s.end_line = 91, s.scope = "CodeGraphInterface", s.docstring = "Find circular dependencies in the codebase", s.signature = "async";

// BATCH 00355
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 85}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "get_most_imported_files", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 93}) SET s.end_line = 104, s.scope = "CodeGraphInterface", s.docstring = "Find the most imported files in the codebase", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 95}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "get_files_with_most_imports", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 106}) SET s.end_line = 117, s.scope = "CodeGraphInterface", s.docstring = "Find files that import the most other files", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 108}) SET s.end_line = -1, s.scope = "CodeGraphInterface";

// BATCH 00356
MERGE (s:Method {name: "analyze_module_coupling", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 119}) SET s.end_line = 143, s.scope = "CodeGraphInterface", s.docstring = "Analyze module coupling by finding directories with most inter-dependencies", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 121}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Method {name: "generate_import_visualization", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", start_line: 145}) SET s.end_line = 168, s.scope = "CodeGraphInterface", s.docstring = "Generate data for import graph visualization", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 147}) SET s.end_line = -1, s.scope = "CodeGraphInterface";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/index/src/index/utils/llm_neo4j_interface.py", line_number: 167}) SET s.end_line = -1, s.scope = "CodeGraphInterface";

// BATCH 00357
MERGE (f:File {filepath: "/app/workflows/index/src/index/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/workflows/index/src/index/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/main.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "Index", filepath: "/app/workflows/index/src/index/main.py", start_line: 19}) SET s.end_line = 262;
MERGE (s:Variable {name: "config", filepath: "/app/workflows/index/src/index/main.py", line_number: 20}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "config_file", filepath: "/app/workflows/index/src/index/main.py", line_number: 21}) SET s.end_line = -1, s.scope = "Index";

// BATCH 00358
MERGE (s:Method {name: "create", filepath: "/app/workflows/index/src/index/main.py", start_line: 24}) SET s.end_line = 28, s.scope = "Index", s.docstring = "Create a Clean object from a YAML config file.", s.signature = "async";
MERGE (s:Variable {name: "config_str", filepath: "/app/workflows/index/src/index/main.py", line_number: 26}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "config_dict", filepath: "/app/workflows/index/src/index/main.py", line_number: 27}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Method {name: "_setup_logging", filepath: "/app/workflows/index/src/index/main.py", start_line: 30}) SET s.end_line = 36, s.scope = "Index", s.docstring = "Setup structured logging.", s.signature = "def";
MERGE (s:Method {name: "_get_processing_config", filepath: "/app/workflows/index/src/index/main.py", start_line: 38}) SET s.end_line = 61, s.scope = "Index", s.docstring = "Extract processing configuration from YAML config.", s.signature = "def";

// BATCH 00359
MERGE (s:Variable {name: "config_obj", filepath: "/app/workflows/index/src/index/main.py", line_number: 40}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "indexing_config", filepath: "/app/workflows/index/src/index/main.py", line_number: 44}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "concurrency_config", filepath: "/app/workflows/index/src/index/main.py", line_number: 46}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Method {name: "_safe_process_file", filepath: "/app/workflows/index/src/index/main.py", start_line: 63}) SET s.end_line = 106, s.scope = "Index", s.docstring = "Safely process a single file with comprehensive error handling.", s.signature = "async";
MERGE (s:Variable {name: "file_size", filepath: "/app/workflows/index/src/index/main.py", line_number: 75}) SET s.end_line = -1, s.scope = "Index";

// BATCH 00360
MERGE (s:Variable {name: "content", filepath: "/app/workflows/index/src/index/main.py", line_number: 80}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "chunks_data", filepath: "/app/workflows/index/src/index/main.py", line_number: 88}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/index/src/index/main.py", line_number: 97}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Method {name: "_process_files_with_semaphore", filepath: "/app/workflows/index/src/index/main.py", start_line: 108}) SET s.end_line = 138, s.scope = "Index", s.docstring = "Process files with semaphore-controlled concurrency using anyio.", s.signature = "async";
MERGE (s:Variable {name: "semaphore", filepath: "/app/workflows/index/src/index/main.py", line_number: 121}) SET s.end_line = -1, s.scope = "Index";

// BATCH 00361
MERGE (s:Variable {name: "results", filepath: "/app/workflows/index/src/index/main.py", line_number: 122}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Method {name: "process_with_limit", filepath: "/app/workflows/index/src/index/main.py", start_line: 124}) SET s.end_line = 129, s.scope = "Index", s.signature = "async";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/index/src/index/main.py", line_number: 126}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "total_chunks", filepath: "/app/workflows/index/src/index/main.py", line_number: 135}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Method {name: "_setup_repository", filepath: "/app/workflows/index/src/index/main.py", start_line: 140}) SET s.end_line = 177, s.scope = "Index", s.docstring = "Setup repository and get filtered file list.", s.signature = "async";

// BATCH 00362
MERGE (s:Variable {name: "source", filepath: "/app/workflows/index/src/index/main.py", line_number: 150}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "config_obj", filepath: "/app/workflows/index/src/index/main.py", line_number: 158}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "container", filepath: "/app/workflows/index/src/index/main.py", line_number: 161}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "file_extensions", filepath: "/app/workflows/index/src/index/main.py", line_number: 170}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "files", filepath: "/app/workflows/index/src/index/main.py", line_number: 172}) SET s.end_line = -1, s.scope = "Index";

// BATCH 00363
MERGE (s:Method {name: "index_codebase", filepath: "/app/workflows/index/src/index/main.py", start_line: 180}) SET s.end_line = 238, s.scope = "Index", s.docstring = "Index all code files in a repository using anyio concurrency.", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/index/src/index/main.py", line_number: 191}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "processing_config", filepath: "/app/workflows/index/src/index/main.py", line_number: 192}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "supabase", filepath: "/app/workflows/index/src/index/main.py", line_number: 203}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "total_chunks", filepath: "/app/workflows/index/src/index/main.py", line_number: 224}) SET s.end_line = -1, s.scope = "Index";

// BATCH 00364
MERGE (s:Method {name: "clear_embeddings_table", filepath: "/app/workflows/index/src/index/main.py", start_line: 241}) SET s.end_line = 262, s.scope = "Index", s.docstring = "Clear all data from the code_embeddings table.", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/index/src/index/main.py", line_number: 247}) SET s.end_line = -1, s.scope = "Index";
MERGE (s:Variable {name: "supabase", filepath: "/app/workflows/index/src/index/main.py", line_number: 250}) SET s.end_line = -1, s.scope = "Index";
MERGE (f:File {filepath: "/app/workflows/index/src/index/operations/embedding_handler.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/operations/embedding_handler.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "EmbeddingHandler", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", start_line: 11}) SET s.end_line = 154;

// BATCH 00365
MERGE (s:Method {name: "generate_embeddings_batch", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", start_line: 15}) SET s.end_line = 42, s.scope = "EmbeddingHandler", s.docstring = "Generate embeddings for a batch of chunks.", s.signature = "async";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 22}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Method {name: "generate_single_embedding", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", start_line: 24}) SET s.end_line = 36, s.scope = "EmbeddingHandler", s.docstring = "Generate embedding and append to results.", s.signature = "async";
MERGE (s:Variable {name: "embedding", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 27}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Method {name: "insert_chunk_safe", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", start_line: 45}) SET s.end_line = 70, s.scope = "EmbeddingHandler", s.docstring = "Safely insert a single chunk.", s.signature = "async";

// BATCH 00366
MERGE (s:Variable {name: "insert_payload", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 53}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Method {name: "store_chunks_with_embeddings", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", start_line: 73}) SET s.end_line = 113, s.scope = "EmbeddingHandler", s.docstring = "Store chunks with embeddings in batches.", s.signature = "async";
MERGE (s:Variable {name: "successful_inserts", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 86}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Variable {name: "batch", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 90}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Variable {name: "embedding_results", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 95}) SET s.end_line = -1, s.scope = "EmbeddingHandler";

// BATCH 00367
MERGE (s:Variable {name: "batch_inserts", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 103}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Method {name: "clear_embeddings_safe", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", start_line: 116}) SET s.end_line = 154, s.scope = "EmbeddingHandler", s.docstring = "Safely clear embeddings table with multiple fallback methods.", s.signature = "async";
MERGE (s:Variable {name: "count_result", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 120}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Variable {name: "initial_count", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 122}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Variable {name: "final_count_result", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 137}) SET s.end_line = -1, s.scope = "EmbeddingHandler";

// BATCH 00368
MERGE (s:Variable {name: "final_count", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 139}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (s:Variable {name: "deleted", filepath: "/app/workflows/index/src/index/operations/embedding_handler.py", line_number: 142}) SET s.end_line = -1, s.scope = "EmbeddingHandler";
MERGE (f:File {filepath: "/app/workflows/index/src/index/operations/file_processor.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/operations/file_processor.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "FileProcessor", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 10}) SET s.end_line = 344;
MERGE (s:Method {name: "_validate_symbol_lines", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 14}) SET s.end_line = 27, s.scope = "FileProcessor", s.docstring = "Validate symbol line numbers.", s.signature = "def";

// BATCH 00369
MERGE (s:Method {name: "_is_file_processable", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 30}) SET s.end_line = 39, s.scope = "FileProcessor", s.docstring = "Check if file should be processed.", s.signature = "def";
MERGE (s:Method {name: "_create_chunk_data", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 42}) SET s.end_line = 60, s.scope = "FileProcessor", s.docstring = "Create a standardized chunk data object.", s.signature = "def";
MERGE (s:Method {name: "_create_semantic_chunks", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 63}) SET s.end_line = 114, s.scope = "FileProcessor", s.docstring = "Extract semantic chunks from code symbols.", s.signature = "def";
MERGE (s:Variable {name: "chunks", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 72}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "block_symbols", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 73}) SET s.end_line = -1, s.scope = "FileProcessor";

// BATCH 00370
MERGE (s:Variable {name: "chunk_lines", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 83}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "chunk_text", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 84}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "symbols_info", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 95}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "context", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 106}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Method {name: "_sub_chunk_symbol", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 117}) SET s.end_line = 154, s.scope = "FileProcessor", s.docstring = "Sub-chunk large symbols into smaller pieces.", s.signature = "def";

// BATCH 00371
MERGE (s:Variable {name: "sub_chunks", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 126}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "sub_chunk_slice", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 131}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "sub_content_text", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 132}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "actual_start_line", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 137}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "actual_end_line", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 138}) SET s.end_line = -1, s.scope = "FileProcessor";

// BATCH 00372
MERGE (s:Variable {name: "sub_symbols_info", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 140}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "context", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 146}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Method {name: "_create_fallback_chunks", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 157}) SET s.end_line = 205, s.scope = "FileProcessor", s.docstring = "Create fixed-size chunks as fallback.", s.signature = "def";
MERGE (s:Variable {name: "chunks", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 167}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "chunk_end_idx", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 171}) SET s.end_line = -1, s.scope = "FileProcessor";

// BATCH 00373
MERGE (s:Variable {name: "chunk_slice", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 172}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "chunk_content", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 173}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "actual_start_line", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 178}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "actual_end_line", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 179}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "symbols_info", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 181}) SET s.end_line = -1, s.scope = "FileProcessor";

// BATCH 00374
MERGE (s:Variable {name: "symbols_info", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 183}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "context", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 189}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "middle_line", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 193}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "context", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 195}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Method {name: "process_file_core", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 208}) SET s.end_line = 249, s.scope = "FileProcessor", s.docstring = "Core file processing logic - returns chunk data without embeddings.", s.signature = "async";

// BATCH 00375
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 215}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "code_file", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 219}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "file_language", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 220}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "all_file_symbols", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 221}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "file_language", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 224}) SET s.end_line = -1, s.scope = "FileProcessor";

// BATCH 00376
MERGE (s:Variable {name: "all_file_symbols", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 225}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "semantic_chunks", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 231}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "fallback_chunks", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 241}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Method {name: "get_filtered_files", filepath: "/app/workflows/index/src/index/operations/file_processor.py", start_line: 252}) SET s.end_line = 344, s.scope = "FileProcessor", s.docstring = "Get all source files in the container, filtering out build artifacts and binaries.", s.signature = "async";
MERGE (s:Variable {name: "extensions", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 257}) SET s.end_line = -1, s.scope = "FileProcessor";

// BATCH 00377
MERGE (s:Variable {name: "exclude_dirs", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 272}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "exclude_files", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 291}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "all_files", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 300}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "file_list", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 301}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "filtered_files", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 304}) SET s.end_line = -1, s.scope = "FileProcessor";

// BATCH 00378
MERGE (s:Variable {name: "excluded_count", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 305}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "file_path", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 314}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "file_ext", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 327}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (s:Variable {name: "is_special_file", filepath: "/app/workflows/index/src/index/operations/file_processor.py", line_number: 328}) SET s.end_line = -1, s.scope = "FileProcessor";
MERGE (f:File {filepath: "/app/workflows/index/src/index/operations/import_analyzer.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/operations/import_analyzer.py" ON MATCH SET f.language = "python";

// BATCH 00379
MERGE (s:Class {name: "ImportAnalyzer", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 9}) SET s.end_line = 277;
MERGE (s:Method {name: "analyze_file_imports", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 13}) SET s.end_line = 57, s.scope = "ImportAnalyzer", s.docstring = "
        Analyze a file for imports without using AST parsing.
        Returns the set of imported files and creates relationships in Neo4j.
        ", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 22}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "language", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 23}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 24}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00380
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 33}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 36}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 39}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 42}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 45}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00381
MERGE (s:Method {name: "_detect_language", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 60}) SET s.end_line = 81, s.scope = "ImportAnalyzer", s.docstring = "Detect programming language from file extension.", s.signature = "def";
MERGE (s:Variable {name: "ext", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 62}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "language_map", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 64}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_analyze_python_imports", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 84}) SET s.end_line = 139, s.scope = "ImportAnalyzer", s.docstring = "Extract Python import statements using regex.", s.signature = "def";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 86}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00382
MERGE (s:Variable {name: "current_dir", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 87}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 88}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 91}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 102}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "dots", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 107}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00383
MERGE (s:Variable {name: "relative_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 108}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "parent_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 111}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "parent_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 113}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 116}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 119}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00384
MERGE (s:Variable {name: "possible_paths", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 126}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 134}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 136}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Method {name: "_analyze_js_imports", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 142}) SET s.end_line = 188, s.scope = "ImportAnalyzer", s.docstring = "Extract JavaScript/TypeScript import statements using regex.", s.signature = "def";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 144}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00385
MERGE (s:Variable {name: "current_dir", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 145}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 146}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 149}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 158}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "abs_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 165}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00386
MERGE (s:Variable {name: "possible_paths", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 170}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 177}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 179}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 183}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "norm_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 185}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00387
MERGE (s:Method {name: "_analyze_java_imports", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 191}) SET s.end_line = 203, s.scope = "ImportAnalyzer", s.docstring = "Extract Java import statements using regex.", s.signature = "def";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 193}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 194}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "pattern", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 196}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 200}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00388
MERGE (s:Method {name: "_analyze_go_imports", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 206}) SET s.end_line = 236, s.scope = "ImportAnalyzer", s.docstring = "Extract Go import statements using regex.", s.signature = "def";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 208}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 209}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 211}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "single_match", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 215}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00389
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 217}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 223}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 228}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "pkg_match", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 231}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 233}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00390
MERGE (s:Method {name: "_analyze_rust_imports", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 239}) SET s.end_line = 255, s.scope = "ImportAnalyzer", s.docstring = "Extract Rust import statements using regex.", s.signature = "def";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 241}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 242}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 244}) SET s.end_line = -1, s.scope = "ImportAnalyzer";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", line_number: 252}) SET s.end_line = -1, s.scope = "ImportAnalyzer";

// BATCH 00391
MERGE (s:Method {name: "_create_import_relationships", filepath: "/app/workflows/index/src/index/operations/import_analyzer.py", start_line: 258}) SET s.end_line = 277, s.scope = "ImportAnalyzer", s.docstring = "Create import relationships in Neo4j.", s.signature = "async";
MERGE (f:File {filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/operations/relationship_extractor.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "RelationshipExtractor", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 10}) SET s.end_line = 337;
MERGE (s:Method {name: "extract_relationships", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 14}) SET s.end_line = 35, s.scope = "RelationshipExtractor", s.docstring = "Extract relationships between code symbols", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 19}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00392
MERGE (s:Variable {name: "symbol_map", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 23}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_internal_relationships", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 38}) SET s.end_line = 86, s.scope = "RelationshipExtractor", s.docstring = "Extract relationships between symbols within the same file", s.signature = "async";
MERGE (s:Variable {name: "symbol_type", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 44}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "symbol_name", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 45}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "line_number", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 46}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00393
MERGE (s:Variable {name: "base_symbol", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 52}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "base_type", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 53}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "called_symbol", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 72}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "called_type", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 73}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_file_imports", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 89}) SET s.end_line = 131, s.scope = "RelationshipExtractor", s.docstring = "Extract file import relationships", s.signature = "async";

// BATCH 00394
MERGE (s:Variable {name: "language", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 97}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "content", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 98}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "content_lines", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 104}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "imported_files", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 105}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_python_imports", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 134}) SET s.end_line = 171, s.scope = "RelationshipExtractor", s.docstring = "Extract Python import statements", s.signature = "async";

// BATCH 00395
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 137}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 146}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "possible_paths", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 153}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_js_imports", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 174}) SET s.end_line = 233, s.scope = "RelationshipExtractor", s.docstring = "Extract JavaScript/TypeScript import statements", s.signature = "async";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 177}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00396
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 188}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "current_dir", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 195}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "abs_path", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 196}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "possible_paths", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 201}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_java_imports", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 236}) SET s.end_line = 256, s.scope = "RelationshipExtractor", s.docstring = "Extract Java import statements", s.signature = "async";

// BATCH 00397
MERGE (s:Variable {name: "pattern", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 238}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 242}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_go_imports", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 259}) SET s.end_line = 310, s.scope = "RelationshipExtractor", s.docstring = "Extract Go import statements", s.signature = "async";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 261}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "import_line", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 262}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00398
MERGE (s:Variable {name: "single_match", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 266}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 268}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 286}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "import_line", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 287}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "in_import_block", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 292}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00399
MERGE (s:Variable {name: "pkg_match", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 295}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "package_path", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 297}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Method {name: "_extract_rust_imports", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", start_line: 313}) SET s.end_line = 337, s.scope = "RelationshipExtractor", s.docstring = "Extract Rust import statements", s.signature = "async";
MERGE (s:Variable {name: "patterns", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 315}) SET s.end_line = -1, s.scope = "RelationshipExtractor";
MERGE (s:Variable {name: "module_path", filepath: "/app/workflows/index/src/index/operations/relationship_extractor.py", line_number: 323}) SET s.end_line = -1, s.scope = "RelationshipExtractor";

// BATCH 00400
MERGE (f:File {filepath: "/app/workflows/index/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/workflows/index/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/workflows/index/src/index/services/neo4j_service.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/index/src/index/services/neo4j_service.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "Neo4jService", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 9}) SET s.end_line = 282;
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 12}) SET s.end_line = 39, s.scope = "Neo4jService", s.docstring = "Initialize Neo4jService with user and password.", s.signature = "def";
MERGE (s:Method {name: "create_neo4j_service", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 41}) SET s.end_line = 60, s.scope = "Neo4jService", s.docstring = "Create a Neo4j service as a Dagger service", s.signature = "async";

// BATCH 00401
MERGE (s:Method {name: "create_neo4j_client", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 62}) SET s.end_line = 82, s.scope = "Neo4jService", s.docstring = "Create a Neo4j client container with cypher-shell", s.signature = "async";
MERGE (s:Variable {name: "source", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 64}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "cypher_cli", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 70}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "run_query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 84}) SET s.end_line = 101, s.scope = "Neo4jService", s.docstring = "Run a query against the Neo4j service", s.signature = "async";
MERGE (s:Variable {name: "client", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 91}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00402
MERGE (s:Method {name: "test_connection", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 103}) SET s.end_line = 105, s.scope = "Neo4jService", s.docstring = "Test connection to Neo4j service", s.signature = "async";
MERGE (s:Method {name: "connect", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 107}) SET s.end_line = 115, s.scope = "Neo4jService", s.docstring = "Verify connection to Neo4j", s.signature = "def";
MERGE (s:Method {name: "clear_database", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 117}) SET s.end_line = 126, s.scope = "Neo4jService", s.docstring = "Clear all nodes and relationships from the database", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 121}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "add_file_node", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 128}) SET s.end_line = 141, s.scope = "Neo4jService", s.docstring = "Add a file node to the graph", s.signature = "async";

// BATCH 00403
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 132}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "language", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 133}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 136}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "add_symbol", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 143}) SET s.end_line = 193, s.scope = "Neo4jService", s.docstring = "Add a symbol node to the graph with connection to its file", s.signature = "async";
MERGE (s:Variable {name: "properties", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 147}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00404
MERGE (s:Variable {name: "name", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 151}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "filepath", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 152}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "end_line_str", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 155}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "start_line_str", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 156}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "props", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 159}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00405
MERGE (s:Variable {name: "escaped_v", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 167}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "properties_str", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 170}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 173}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "add_relationship", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 195}) SET s.end_line = 218, s.scope = "Neo4jService", s.docstring = "Add a relationship between two code elements", s.signature = "async";
MERGE (s:Variable {name: "from_name", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 201}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00406
MERGE (s:Variable {name: "from_filepath", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 202}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "to_name", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 203}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "to_filepath", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 204}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 207}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Method {name: "execute_query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", start_line: 220}) SET s.end_line = 282, s.scope = "Neo4jService", s.docstring = "Execute a parameterized Cypher query and return structured results.
        
        This method is used by the CodeGraphInterface to provide a clean API
        for LLMs to query the code graph.
        
        Args:
            query: Cypher query with parameter placeholders
            params: Dictionary of parameters to inject into the query
        
        Returns:
            List of result records as dictionaries
        ", s.signature = "async";

// BATCH 00407
MERGE (s:Variable {name: "params", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 235}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "formatted_query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 239}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "formatted_query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 242}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "formatted_query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 245}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "formatted_query", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 248}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00408
MERGE (s:Variable {name: "result_text", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 252}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 256}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "headers", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 262}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "results", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 265}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (s:Variable {name: "values", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 270}) SET s.end_line = -1, s.scope = "Neo4jService";

// BATCH 00409
MERGE (s:Variable {name: "result_dict", filepath: "/app/workflows/index/src/index/services/neo4j_service.py", line_number: 274}) SET s.end_line = -1, s.scope = "Neo4jService";
MERGE (f:File {filepath: "/app/workflows/cover/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/workflows/cover/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/src/reporter/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/src/reporter/main.py" ON MATCH SET f.language = "python";
MERGE (s:Variable {name: "switch_reporter", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", line_number: 10}) SET s.end_line = -1;

// BATCH 00410
MERGE (s:Class {name: "Reporter", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", start_line: 17}) SET s.end_line = 86;
MERGE (s:Variable {name: "name", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", line_number: 18}) SET s.end_line = -1, s.scope = "Reporter";
MERGE (s:Method {name: "__post_init__", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", start_line: 20}) SET s.end_line = 21, s.scope = "Reporter", s.signature = "def";
MERGE (s:Method {name: "get_code_under_test", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", start_line: 24}) SET s.end_line = 29, s.scope = "Reporter", s.docstring = "Extract code under test from the coverage HTML report", s.signature = "def";
MERGE (s:Method {name: "get_coverage_html", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", start_line: 32}) SET s.end_line = 38, s.scope = "Reporter", s.docstring = "Get the coverage HTML file from the report file", s.signature = "async";

// BATCH 00411
MERGE (s:Method {name: "get_coverage_reports", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", start_line: 41}) SET s.end_line = 57, s.scope = "Reporter", s.docstring = "Extract coverage data from the HTML input and create a JSON file with the data", s.signature = "def";
MERGE (s:Method {name: "parse_test_results", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", start_line: 60}) SET s.end_line = 68, s.scope = "Reporter", s.docstring = "Parse the test results JSON file and return a str with the failed tests", s.signature = "def";
MERGE (s:Method {name: "validate_config", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", start_line: 71}) SET s.end_line = 86, s.scope = "Reporter", s.docstring = "Validate the configuration file", s.signature = "def";
MERGE (s:Variable {name: "config_dict", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", line_number: 73}) SET s.end_line = -1, s.scope = "Reporter";
MERGE (s:Variable {name: "config_dict", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", line_number: 74}) SET s.end_line = -1, s.scope = "Reporter";

// BATCH 00412
MERGE (s:Variable {name: "current_dir", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", line_number: 78}) SET s.end_line = -1, s.scope = "Reporter";
MERGE (s:Variable {name: "schema", filepath: "/app/workflows/cover/plugins/reporter/src/reporter/main.py", line_number: 81}) SET s.end_line = -1, s.scope = "Reporter";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "find_index_html_files", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", start_line: 7}) SET s.end_line = 33, s.docstring = "Find the index.html files in the test container and return a list of (dir_path, file_path) tuples.", s.signature = "async";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 13}) SET s.end_line = -1;

// BATCH 00413
MERGE (s:Variable {name: "index_files", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 26}) SET s.end_line = -1;
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 28}) SET s.end_line = -1;
MERGE (s:Variable {name: "dir_path", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 29}) SET s.end_line = -1;
MERGE (s:Variable {name: "file_path", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 30}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_code", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", start_line: 39}) SET s.end_line = 65, s.docstring = "
    Extracts Python code lines from the HTML markup of a coverage report.

    Parameters:
        html_content (str): The HTML content of the coverage report.

    Returns:
        str: Extracted Python code as a single string.
    ", s.signature = "def";

// BATCH 00414
MERGE (s:Variable {name: "soup", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 49}) SET s.end_line = -1;
MERGE (s:Variable {name: "code_lines", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 50}) SET s.end_line = -1;
MERGE (s:Variable {name: "main_content", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 53}) SET s.end_line = -1;
MERGE (s:Variable {name: "code_span", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/utils.py", line_number: 59}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/__init__.py" ON MATCH SET f.language = "python";

// BATCH 00415
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "PytestReporterPlugin", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 13}) SET s.end_line = 168;
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 15}) SET s.end_line = 16, s.scope = "PytestReporterPlugin", s.signature = "def";
MERGE (s:Method {name: "base", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 18}) SET s.end_line = 25, s.scope = "PytestReporterPlugin", s.signature = "def";
MERGE (s:Method {name: "create_coverage_reports", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 27}) SET s.end_line = 29, s.scope = "PytestReporterPlugin", s.docstring = "Create CoverageReport instances from extracted data.", s.signature = "def";

// BATCH 00416
MERGE (s:Method {name: "extract_and_process_report", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 31}) SET s.end_line = 64, s.scope = "PytestReporterPlugin", s.docstring = "Extract coverage data from the given HTML and process it.", s.signature = "def";
MERGE (s:Variable {name: "soup", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 38}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "coverage_data", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 39}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "columns", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 42}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "file", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 44}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";

// BATCH 00417
MERGE (s:Variable {name: "path", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 46}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "coverage_report_path", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 48}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "coverage_percentage", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 50}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "data", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 53}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Method {name: "get_code_under_test", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 67}) SET s.end_line = 73, s.scope = "PytestReporterPlugin", s.docstring = "Extract code under test from the coverage HTML report", s.signature = "async";

// BATCH 00418
MERGE (s:Variable {name: "code", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 70}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Method {name: "get_coverage_html", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 76}) SET s.end_line = 84, s.scope = "PytestReporterPlugin", s.docstring = "Get the coverage HTML file from the report file", s.signature = "async";
MERGE (s:Variable {name: "coverage", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 82}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "coverage", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 83}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Method {name: "get_coverage_reports", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 87}) SET s.end_line = 117, s.scope = "PytestReporterPlugin", s.docstring = "Extract coverage data from the HTML input and create a JSON file with the data", s.signature = "async";

// BATCH 00419
MERGE (s:Variable {name: "index_files", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 94}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "index_html", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 97}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "coverage_reports_json", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 107}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "container", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 111}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Method {name: "parse_test_results", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", start_line: 120}) SET s.end_line = 168, s.scope = "PytestReporterPlugin", s.docstring = "
        Extracts any errors found in the coverage report HTML markup.

        Parameters:
            content (str): The HTML content of the coverage report.

        Returns:
            str: A string containing error details, if any.
        ", s.signature = "def";

// BATCH 00420
MERGE (s:Variable {name: "soup", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 130}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "errors", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 131}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "data_container", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 134}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "json_blob", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 141}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "report_data", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 145}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";

// BATCH 00421
MERGE (s:Variable {name: "tests", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 151}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "result_status", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 158}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (s:Variable {name: "log_message", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py", line_number: 160}) SET s.end_line = -1, s.scope = "PytestReporterPlugin";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "CoverageReport", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py", start_line: 4}) SET s.end_line = 19;

// BATCH 00422
MERGE (s:Variable {name: "file", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py", line_number: 13}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (s:Variable {name: "coverage_report_path", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py", line_number: 14}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (s:Variable {name: "coverage_percentage", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/coverage_report.py", line_number: 17}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "CodeModule", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py", start_line: 4}) SET s.end_line = 21;

// BATCH 00423
MERGE (s:Variable {name: "strategy", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py", line_number: 15}) SET s.end_line = -1, s.scope = "CodeModule";
MERGE (s:Variable {name: "imports", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py", line_number: 16}) SET s.end_line = -1, s.scope = "CodeModule";
MERGE (s:Variable {name: "code", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py", line_number: 17}) SET s.end_line = -1, s.scope = "CodeModule";
MERGE (s:Variable {name: "test_path", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py", line_number: 18}) SET s.end_line = -1, s.scope = "CodeModule";
MERGE (s:Variable {name: "error", filepath: "/app/workflows/cover/plugins/reporter/pytest/src/pytest_reporter_plugin/models/code_module.py", line_number: 19}) SET s.end_line = -1, s.scope = "CodeModule";

// BATCH 00424
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/pytest/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/workflows/cover/plugins/reporter/pytest/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "extract_coverage_data_from_table", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", start_line: 9}) SET s.end_line = 52, s.docstring = "Extract coverage data from HTML coverage report.", s.signature = "def";
MERGE (s:Variable {name: "soup", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 13}) SET s.end_line = -1;
MERGE (s:Variable {name: "coverage_data", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 14}) SET s.end_line = -1;

// BATCH 00425
MERGE (s:Variable {name: "columns", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 18}) SET s.end_line = -1;
MERGE (s:Variable {name: "file", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 20}) SET s.end_line = -1;
MERGE (s:Variable {name: "path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 21}) SET s.end_line = -1;
MERGE (s:Variable {name: "coverage_report_path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 22}) SET s.end_line = -1;
MERGE (s:Variable {name: "statements_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 29}) SET s.end_line = -1;

// BATCH 00426
MERGE (s:Variable {name: "branches_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 31}) SET s.end_line = -1;
MERGE (s:Variable {name: "functions_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 33}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 35}) SET s.end_line = -1;
MERGE (s:Variable {name: "coverage_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 38}) SET s.end_line = -1;
MERGE (s:Variable {name: "data", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 41}) SET s.end_line = -1;

// BATCH 00427
MERGE (s:Function {name: "extract_coverage_data_from_row", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", start_line: 55}) SET s.end_line = 85, s.docstring = "Extract coverage data from HTML coverage report.", s.signature = "def";
MERGE (s:Variable {name: "coverage_data", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 60}) SET s.end_line = -1;
MERGE (s:Variable {name: "columns", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 61}) SET s.end_line = -1;
MERGE (s:Variable {name: "file", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 63}) SET s.end_line = -1;
MERGE (s:Variable {name: "path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 64}) SET s.end_line = -1;

// BATCH 00428
MERGE (s:Variable {name: "coverage_report_path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 65}) SET s.end_line = -1;
MERGE (s:Variable {name: "statements_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 66}) SET s.end_line = -1;
MERGE (s:Variable {name: "branches_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 67}) SET s.end_line = -1;
MERGE (s:Variable {name: "functions_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 68}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 69}) SET s.end_line = -1;

// BATCH 00429
MERGE (s:Variable {name: "coverage_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 72}) SET s.end_line = -1;
MERGE (s:Variable {name: "data", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 74}) SET s.end_line = -1;
MERGE (s:Function {name: "find_index_html_files", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", start_line: 88}) SET s.end_line = 119, s.docstring = "Find the top-level index.html file in the coverage report directory.", s.signature = "async";
MERGE (s:Variable {name: "result", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 95}) SET s.end_line = -1;
MERGE (s:Variable {name: "index_files", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 111}) SET s.end_line = -1;

// BATCH 00430
MERGE (s:Variable {name: "parts", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 114}) SET s.end_line = -1;
MERGE (s:Variable {name: "dir_path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 115}) SET s.end_line = -1;
MERGE (s:Variable {name: "file_path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 116}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_code", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", start_line: 122}) SET s.end_line = 139, s.signature = "def";
MERGE (s:Variable {name: "soup", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 123}) SET s.end_line = -1;

// BATCH 00431
MERGE (s:Variable {name: "code_lines", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 126}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 133}) SET s.end_line = -1;
MERGE (s:Variable {name: "stripped_lines", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/utils.py", line_number: 136}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/__init__.py" ON MATCH SET f.language = "python";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py" ON MATCH SET f.language = "python";

// BATCH 00432
MERGE (s:Class {name: "JestReporterPlugin", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 15}) SET s.end_line = 137;
MERGE (s:Method {name: "__init__", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 17}) SET s.end_line = 18, s.scope = "JestReporterPlugin", s.signature = "def";
MERGE (s:Method {name: "base", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 20}) SET s.end_line = 29, s.scope = "JestReporterPlugin", s.signature = "def";
MERGE (s:Method {name: "create_coverage_reports", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 31}) SET s.end_line = 33, s.scope = "JestReporterPlugin", s.docstring = "Create CoverageReport instances from extracted data.", s.signature = "def";
MERGE (s:Method {name: "extract_and_process_report", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 35}) SET s.end_line = 70, s.scope = "JestReporterPlugin", s.docstring = "Extract coverage data from the given HTML and process it.", s.signature = "async";

// BATCH 00433
MERGE (s:Variable {name: "soup", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 39}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "columns", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 41}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "folder_or_file", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 43}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "link", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 44}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 46}) SET s.end_line = -1, s.scope = "JestReporterPlugin";

// BATCH 00434
MERGE (s:Variable {name: "coverage_report_data", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 49}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "next_index_html", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 53}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "coverage_report_data", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 56}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "coverage_report_data", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 60}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Method {name: "get_code_under_test", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 73}) SET s.end_line = 79, s.scope = "JestReporterPlugin", s.docstring = "Extract code under test from the coverage HTML report", s.signature = "async";

// BATCH 00435
MERGE (s:Variable {name: "code", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 76}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Method {name: "get_coverage_html", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 82}) SET s.end_line = 93, s.scope = "JestReporterPlugin", s.docstring = "Get the coverage HTML file from the report file", s.signature = "async";
MERGE (s:Variable {name: "coverage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 88}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "coverage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 90}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Method {name: "get_coverage_reports", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 96}) SET s.end_line = 126, s.scope = "JestReporterPlugin", s.docstring = "Extract coverage data from the HTML input and create a JSON file with the data", s.signature = "async";

// BATCH 00436
MERGE (s:Variable {name: "index_files", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 103}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "index_html", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 105}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "coverage_reports_json", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 116}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "container", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 120}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Method {name: "parse_test_results", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", start_line: 129}) SET s.end_line = 137, s.scope = "JestReporterPlugin", s.docstring = "Parse the test results JSON file and return a str with the failed tests", s.signature = "async";

// BATCH 00437
MERGE (s:Variable {name: "data", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 131}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (s:Variable {name: "message", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/main.py", line_number: 132}) SET s.end_line = -1, s.scope = "JestReporterPlugin";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "CodeModule", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py", start_line: 4}) SET s.end_line = 21;
MERGE (s:Variable {name: "strategy", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py", line_number: 15}) SET s.end_line = -1, s.scope = "CodeModule";

// BATCH 00438
MERGE (s:Variable {name: "imports", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py", line_number: 16}) SET s.end_line = -1, s.scope = "CodeModule";
MERGE (s:Variable {name: "code", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py", line_number: 17}) SET s.end_line = -1, s.scope = "CodeModule";
MERGE (s:Variable {name: "test_path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py", line_number: 18}) SET s.end_line = -1, s.scope = "CodeModule";
MERGE (s:Variable {name: "error", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/code_module.py", line_number: 19}) SET s.end_line = -1, s.scope = "CodeModule";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py"}) ON CREATE SET f.language = "python", f.path = "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py" ON MATCH SET f.language = "python";

// BATCH 00439
MERGE (s:Class {name: "CoverageReport", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py", start_line: 5}) SET s.end_line = 24;
MERGE (s:Variable {name: "file", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py", line_number: 18}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (s:Variable {name: "coverage_report_path", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py", line_number: 19}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (s:Variable {name: "coverage_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py", line_number: 20}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (s:Variable {name: "statements_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py", line_number: 21}) SET s.end_line = -1, s.scope = "CoverageReport";

// BATCH 00440
MERGE (s:Variable {name: "branches_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py", line_number: 22}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (s:Variable {name: "functions_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py", line_number: 23}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (s:Variable {name: "lines_percentage", filepath: "/app/workflows/cover/plugins/reporter/jest/src/jest_reporter_plugin/models/coverage_report.py", line_number: 24}) SET s.end_line = -1, s.scope = "CoverageReport";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/jest/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/workflows/cover/plugins/reporter/jest/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/workflows/cover/plugins/reporter/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/workflows/cover/plugins/reporter/pyproject.toml" ON MATCH SET f.language = "unknown";

// BATCH 00441
MERGE (f:File {filepath: "/app/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/simple_chalk/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/simple_chalk/__init__.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "_identity", filepath: "/app/simple_chalk/__init__.py", start_line: 6}) SET s.end_line = 7, s.signature = "def";
MERGE (s:Variable {name: "blue", filepath: "/app/simple_chalk/__init__.py", line_number: 9}) SET s.end_line = -1;
MERGE (s:Variable {name: "green", filepath: "/app/simple_chalk/__init__.py", line_number: 10}) SET s.end_line = -1;

// BATCH 00442
MERGE (s:Variable {name: "yellow", filepath: "/app/simple_chalk/__init__.py", line_number: 11}) SET s.end_line = -1;
MERGE (s:Variable {name: "red", filepath: "/app/simple_chalk/__init__.py", line_number: 12}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/services/query/src/query/utils/code_parser.py"}) ON CREATE SET f.language = "python", f.path = "/app/services/query/src/query/utils/code_parser.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "SymbolType", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 9}) SET s.end_line = 19;
MERGE (s:Constant {name: "VARIABLE", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 10}) SET s.end_line = -1, s.scope = "SymbolType";

// BATCH 00443
MERGE (s:Constant {name: "FUNCTION", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 11}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "CLASS", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 12}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "INTERFACE", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 13}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "ENUM", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 14}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "STRUCT", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 15}) SET s.end_line = -1, s.scope = "SymbolType";

// BATCH 00444
MERGE (s:Constant {name: "TRAIT", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 16}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "CONSTANT", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 17}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "METHOD", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 18}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Constant {name: "PROPERTY", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 19}) SET s.end_line = -1, s.scope = "SymbolType";
MERGE (s:Class {name: "CodeSymbol", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 23}) SET s.end_line = 33;

// BATCH 00445
MERGE (s:Variable {name: "name", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 25}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 26}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "line_number", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 27}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "column", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 28}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "end_line", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 29}) SET s.end_line = -1, s.scope = "CodeSymbol";

// BATCH 00446
MERGE (s:Variable {name: "end_column", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 30}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "scope", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 31}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "signature", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 32}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Variable {name: "visibility", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 33}) SET s.end_line = -1, s.scope = "CodeSymbol";
MERGE (s:Class {name: "CodeFile", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 37}) SET s.end_line = 55;

// BATCH 00447
MERGE (s:Variable {name: "content", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 39}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "filepath", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 40}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "language", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 41}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 42}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 43}) SET s.end_line = -1, s.scope = "CodeFile";

// BATCH 00448
MERGE (s:Method {name: "__post_init__", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 45}) SET s.end_line = 46, s.scope = "CodeFile", s.signature = "def";
MERGE (s:Method {name: "get_context_around_line", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 48}) SET s.end_line = 55, s.scope = "CodeFile", s.docstring = "Get a few lines of context around the specified line.", s.signature = "def";
MERGE (s:Variable {name: "start", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 50}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "end", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 51}) SET s.end_line = -1, s.scope = "CodeFile";
MERGE (s:Variable {name: "context", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 52}) SET s.end_line = -1, s.scope = "CodeFile";

// BATCH 00449
MERGE (s:Function {name: "detect_language", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 58}) SET s.end_line = 86, s.docstring = "Detect the programming language from the file extension.", s.signature = "def";
MERGE (s:Variable {name: "ext", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 60}) SET s.end_line = -1;
MERGE (s:Variable {name: "language_map", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 61}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_python_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 89}) SET s.end_line = 174, s.docstring = "Parse Python code to extract symbols using AST.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 91}) SET s.end_line = -1;

// BATCH 00450
MERGE (s:Variable {name: "tree", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 94}) SET s.end_line = -1;
MERGE (s:Variable {name: "current_scope", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 97}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 103}) SET s.end_line = -1;
MERGE (s:Variable {name: "args_list", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 106}) SET s.end_line = -1;
MERGE (s:Variable {name: "defaults", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 111}) SET s.end_line = -1;

// BATCH 00451
MERGE (s:Variable {name: "arg_signatures", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 115}) SET s.end_line = -1;
MERGE (s:Variable {name: "default_val", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 121}) SET s.end_line = -1;
MERGE (s:Variable {name: "signature", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 126}) SET s.end_line = -1;
MERGE (s:Variable {name: "full_name", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 128}) SET s.end_line = -1;
MERGE (s:Variable {name: "old_scope", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 142}) SET s.end_line = -1;

// BATCH 00452
MERGE (s:Variable {name: "current_scope", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 143}) SET s.end_line = -1;
MERGE (s:Variable {name: "current_scope", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 156}) SET s.end_line = -1;
MERGE (s:Variable {name: "is_constant", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 162}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_javascript_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 177}) SET s.end_line = 253, s.docstring = "Parse JavaScript/TypeScript code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 179}) SET s.end_line = -1;

// BATCH 00453
MERGE (s:Variable {name: "function_patterns", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 182}) SET s.end_line = -1;
MERGE (s:Variable {name: "class_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 193}) SET s.end_line = -1;
MERGE (s:Variable {name: "variable_patterns", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 194}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 206}) SET s.end_line = -1;
MERGE (s:Variable {name: "name", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 212}) SET s.end_line = -1;

// BATCH 00454
MERGE (s:Variable {name: "name", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 214}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 237}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 239}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 241}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 243}) SET s.end_line = -1;

// BATCH 00455
MERGE (s:Function {name: "parse_java_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 256}) SET s.end_line = 319, s.docstring = "Parse Java code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 258}) SET s.end_line = -1;
MERGE (s:Variable {name: "class_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 261}) SET s.end_line = -1;
MERGE (s:Variable {name: "interface_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 262}) SET s.end_line = -1;
MERGE (s:Variable {name: "enum_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 263}) SET s.end_line = -1;

// BATCH 00456
MERGE (s:Variable {name: "method_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 265}) SET s.end_line = -1;
MERGE (s:Variable {name: "field_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 266}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 269}) SET s.end_line = -1;
MERGE (s:Variable {name: "is_constant", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 310}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_c_cpp_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 322}) SET s.end_line = 393, s.docstring = "Parse C/C++ code using regex patterns.", s.signature = "def";

// BATCH 00457
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 324}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 327}) SET s.end_line = -1;
MERGE (s:Variable {name: "class_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 328}) SET s.end_line = -1;
MERGE (s:Variable {name: "variable_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 329}) SET s.end_line = -1;
MERGE (s:Variable {name: "enum_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 330}) SET s.end_line = -1;

// BATCH 00458
MERGE (s:Variable {name: "define_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 331}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 334}) SET s.end_line = -1;
MERGE (s:Variable {name: "line", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 337}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 351}) SET s.end_line = -1;
MERGE (s:Variable {name: "is_constant", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 384}) SET s.end_line = -1;

// BATCH 00459
MERGE (s:Function {name: "parse_go_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 396}) SET s.end_line = 471, s.docstring = "Parse Go code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 398}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 401}) SET s.end_line = -1;
MERGE (s:Variable {name: "method_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 402}) SET s.end_line = -1;
MERGE (s:Variable {name: "struct_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 403}) SET s.end_line = -1;

// BATCH 00460
MERGE (s:Variable {name: "interface_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 404}) SET s.end_line = -1;
MERGE (s:Variable {name: "const_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 405}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 406}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 409}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_rust_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 474}) SET s.end_line = 557, s.docstring = "Parse Rust code using regex patterns.", s.signature = "def";

// BATCH 00461
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 476}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 479}) SET s.end_line = -1;
MERGE (s:Variable {name: "struct_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 480}) SET s.end_line = -1;
MERGE (s:Variable {name: "trait_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 481}) SET s.end_line = -1;
MERGE (s:Variable {name: "enum_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 482}) SET s.end_line = -1;

// BATCH 00462
MERGE (s:Variable {name: "impl_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 483}) SET s.end_line = -1;
MERGE (s:Variable {name: "const_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 484}) SET s.end_line = -1;
MERGE (s:Variable {name: "let_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 485}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 488}) SET s.end_line = -1;
MERGE (s:Variable {name: "line", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 491}) SET s.end_line = -1;

// BATCH 00463
MERGE (s:Function {name: "parse_ruby_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 560}) SET s.end_line = 640, s.docstring = "Parse Ruby code using regex patterns.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 562}) SET s.end_line = -1;
MERGE (s:Variable {name: "class_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 565}) SET s.end_line = -1;
MERGE (s:Variable {name: "module_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 566}) SET s.end_line = -1;
MERGE (s:Variable {name: "method_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 567}) SET s.end_line = -1;

// BATCH 00464
MERGE (s:Variable {name: "constant_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 568}) SET s.end_line = -1;
MERGE (s:Variable {name: "attr_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 569}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 570}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 573}) SET s.end_line = -1;
MERGE (s:Variable {name: "line", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 576}) SET s.end_line = -1;

// BATCH 00465
MERGE (s:Variable {name: "var_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 625}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 627}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 629}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 631}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_php_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 643}) SET s.end_line = 750, s.docstring = "Parse PHP code using regex patterns.", s.signature = "def";

// BATCH 00466
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 645}) SET s.end_line = -1;
MERGE (s:Variable {name: "class_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 648}) SET s.end_line = -1;
MERGE (s:Variable {name: "interface_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 649}) SET s.end_line = -1;
MERGE (s:Variable {name: "trait_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 650}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 651}) SET s.end_line = -1;

// BATCH 00467
MERGE (s:Variable {name: "method_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 652}) SET s.end_line = -1;
MERGE (s:Variable {name: "property_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 653}) SET s.end_line = -1;
MERGE (s:Variable {name: "const_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 654}) SET s.end_line = -1;
MERGE (s:Variable {name: "var_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 655}) SET s.end_line = -1;
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 658}) SET s.end_line = -1;

// BATCH 00468
MERGE (s:Variable {name: "line", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 661}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 702}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 704}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 706}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 718}) SET s.end_line = -1;

// BATCH 00469
MERGE (s:Variable {name: "visibility", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 720}) SET s.end_line = -1;
MERGE (s:Variable {name: "visibility", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 722}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_generic_code", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 753}) SET s.end_line = 809, s.docstring = "Parse code generically using regex patterns for common symbols.", s.signature = "def";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 755}) SET s.end_line = -1;
MERGE (s:Variable {name: "function_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 758}) SET s.end_line = -1;

// BATCH 00470
MERGE (s:Variable {name: "class_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 759}) SET s.end_line = -1;
MERGE (s:Variable {name: "variable_pattern", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 760}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 777}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 779}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 781}) SET s.end_line = -1;

// BATCH 00471
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 783}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 785}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 798}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbol_type", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 800}) SET s.end_line = -1;
MERGE (s:Function {name: "parse_code_file", filepath: "/app/services/query/src/query/utils/code_parser.py", start_line: 812}) SET s.end_line = 842, s.docstring = "Parse a code file to extract symbols based on the language.", s.signature = "def";

// BATCH 00472
MERGE (s:Variable {name: "language", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 814}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 815}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 819}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 821}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 823}) SET s.end_line = -1;

// BATCH 00473
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 825}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 827}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 829}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 831}) SET s.end_line = -1;
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 833}) SET s.end_line = -1;

// BATCH 00474
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/utils/code_parser.py", line_number: 835}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/services/query/src/query/utils/embeddings.py"}) ON CREATE SET f.language = "python", f.path = "/app/services/query/src/query/utils/embeddings.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "generate_embeddings", filepath: "/app/services/query/src/query/utils/embeddings.py", start_line: 6}) SET s.end_line = 41, s.docstring = "
    Generate embeddings for the given text using OpenAI API.
    ", s.signature = "async";
MERGE (s:Variable {name: "api_key", filepath: "/app/services/query/src/query/utils/embeddings.py", line_number: 16}) SET s.end_line = -1;
MERGE (s:Variable {name: "client", filepath: "/app/services/query/src/query/utils/embeddings.py", line_number: 23}) SET s.end_line = -1;

// BATCH 00475
MERGE (s:Variable {name: "response", filepath: "/app/services/query/src/query/utils/embeddings.py", line_number: 26}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/services/query/src/query/utils/file.py"}) ON CREATE SET f.language = "python", f.path = "/app/services/query/src/query/utils/file.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "get_file_size", filepath: "/app/services/query/src/query/utils/file.py", start_line: 5}) SET s.end_line = 15, s.docstring = "Get the size of a file inside a container.", s.signature = "async";
MERGE (s:Variable {name: "size_str", filepath: "/app/services/query/src/query/utils/file.py", line_number: 9}) SET s.end_line = -1;
MERGE (f:File {filepath: "/app/services/query/src/query/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/services/query/src/query/__init__.py" ON MATCH SET f.language = "python";

// BATCH 00476
MERGE (f:File {filepath: "/app/services/query/src/query/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/services/query/src/query/main.py" ON MATCH SET f.language = "python";
MERGE (s:Class {name: "QueryService", filepath: "/app/services/query/src/query/main.py", start_line: 23}) SET s.end_line = 919;
MERGE (s:Variable {name: "config", filepath: "/app/services/query/src/query/main.py", line_number: 26}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "config_file", filepath: "/app/services/query/src/query/main.py", line_number: 27}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "open_router_api_key", filepath: "/app/services/query/src/query/main.py", line_number: 28}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00477
MERGE (s:Variable {name: "neo_data", filepath: "/app/services/query/src/query/main.py", line_number: 29}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "supabase_url", filepath: "/app/services/query/src/query/main.py", line_number: 30}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "supabase_key", filepath: "/app/services/query/src/query/main.py", line_number: 31}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "neo_password", filepath: "/app/services/query/src/query/main.py", line_number: 32}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "github_access_token", filepath: "/app/services/query/src/query/main.py", line_number: 33}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00478
MERGE (s:Variable {name: "neo_auth", filepath: "/app/services/query/src/query/main.py", line_number: 34}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "cache_enabled", filepath: "/app/services/query/src/query/main.py", line_number: 35}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "cache_ttl", filepath: "/app/services/query/src/query/main.py", line_number: 36}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "parallel_processing", filepath: "/app/services/query/src/query/main.py", line_number: 37}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "embedding_dimension", filepath: "/app/services/query/src/query/main.py", line_number: 38}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00479
MERGE (s:Variable {name: "_logger", filepath: "/app/services/query/src/query/main.py", line_number: 42}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Method {name: "_get_logger", filepath: "/app/services/query/src/query/main.py", start_line: 44}) SET s.end_line = 54, s.scope = "QueryService", s.docstring = "Get or create logger instance (cached)", s.signature = "def";
MERGE (s:Method {name: "create", filepath: "/app/services/query/src/query/main.py", start_line: 57}) SET s.end_line = 134, s.scope = "QueryService", s.docstring = "Initialize the QueryService with configuration", s.signature = "async";
MERGE (s:Variable {name: "config_str", filepath: "/app/services/query/src/query/main.py", line_number: 72}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "config_dict", filepath: "/app/services/query/src/query/main.py", line_number: 73}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00480
MERGE (s:Variable {name: "fallback", filepath: "/app/services/query/src/query/main.py", line_number: 79}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "config_dict", filepath: "/app/services/query/src/query/main.py", line_number: 82}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "config_dict", filepath: "/app/services/query/src/query/main.py", line_number: 86}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "integration_config", filepath: "/app/services/query/src/query/main.py", line_number: 94}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "cache_enabled", filepath: "/app/services/query/src/query/main.py", line_number: 95}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00481
MERGE (s:Variable {name: "cache_ttl", filepath: "/app/services/query/src/query/main.py", line_number: 96}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "parallel_processing", filepath: "/app/services/query/src/query/main.py", line_number: 97}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "supabase_url", filepath: "/app/services/query/src/query/main.py", line_number: 102}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "embedding_dimension", filepath: "/app/services/query/src/query/main.py", line_number: 107}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "instance", filepath: "/app/services/query/src/query/main.py", line_number: 111}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00482
MERGE (s:Method {name: "query", filepath: "/app/services/query/src/query/main.py", start_line: 137}) SET s.end_line = 248, s.scope = "QueryService", s.docstring = "
        Perform a unified query across both semantic and structural databases.

        Args:
            question: The natural language question to ask about the code
            similarity_threshold: Minimum similarity score for semantic matches
            max_results: Maximum number of results to return
            use_cache: Whether to use cached results if available

        Returns:
            Formatted results as a string
        ", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/services/query/src/query/main.py", line_number: 156}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "cache", filepath: "/app/services/query/src/query/main.py", line_number: 161}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "cache_timestamp", filepath: "/app/services/query/src/query/main.py", line_number: 162}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "start_time", filepath: "/app/services/query/src/query/main.py", line_number: 164}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00483
MERGE (s:Variable {name: "cache_key", filepath: "/app/services/query/src/query/main.py", line_number: 167}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "semantic_results", filepath: "/app/services/query/src/query/main.py", line_number: 176}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "file_paths", filepath: "/app/services/query/src/query/main.py", line_number: 180}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 186}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_error", filepath: "/app/services/query/src/query/main.py", line_number: 187}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00484
MERGE (s:Method {name: "get_structural", filepath: "/app/services/query/src/query/main.py", start_line: 190}) SET s.end_line = 197, s.scope = "QueryService", s.signature = "async";
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 193}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_error", filepath: "/app/services/query/src/query/main.py", line_number: 195}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 203}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "semantic_results", filepath: "/app/services/query/src/query/main.py", line_number: 208}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00485
MERGE (s:Variable {name: "file_paths", filepath: "/app/services/query/src/query/main.py", line_number: 212}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 218}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/main.py", line_number: 221}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "query_time_ms", filepath: "/app/services/query/src/query/main.py", line_number: 224}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "result", filepath: "/app/services/query/src/query/main.py", line_number: 228}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00486
MERGE (s:Method {name: "search", filepath: "/app/services/query/src/query/main.py", start_line: 251}) SET s.end_line = 298, s.scope = "QueryService", s.docstring = "
        Perform a semantic search for code relevant to the query.

        Args:
            query: Natural language query about code
            similarity_threshold: Minimum similarity threshold (0.0-1.0)
            max_results: Maximum number of results to return

        Returns:
            Formatted search results as a string
        ", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/services/query/src/query/main.py", line_number: 268}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "results", filepath: "/app/services/query/src/query/main.py", line_number: 272}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "output", filepath: "/app/services/query/src/query/main.py", line_number: 278}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "filepath", filepath: "/app/services/query/src/query/main.py", line_number: 281}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00487
MERGE (s:Variable {name: "score", filepath: "/app/services/query/src/query/main.py", line_number: 282}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "language", filepath: "/app/services/query/src/query/main.py", line_number: 283}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "content", filepath: "/app/services/query/src/query/main.py", line_number: 289}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "content", filepath: "/app/services/query/src/query/main.py", line_number: 291}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Method {name: "invalidate_cache", filepath: "/app/services/query/src/query/main.py", start_line: 301}) SET s.end_line = 312, s.scope = "QueryService", s.docstring = "
        Invalidate cache entries related to a specific file or all entries.

        Args:
            filepath: Optional file path to invalidate. If None, invalidate all.

        Returns:
            Message indicating the number of entries invalidated
        ", s.signature = "async";

// BATCH 00488
MERGE (s:Method {name: "get_file_details", filepath: "/app/services/query/src/query/main.py", start_line: 315}) SET s.end_line = 341, s.scope = "QueryService", s.docstring = "
        Get detailed information about a specific file, combining graph and vector data.

        Args:
            filepath: Path to the file to examine

        Returns:
            Formatted string with file details
        ", s.signature = "async";
MERGE (s:Method {name: "debug_query", filepath: "/app/services/query/src/query/main.py", start_line: 344}) SET s.end_line = 435, s.scope = "QueryService", s.docstring = "
        Perform a query with enhanced debugging output to inspect results.

        Args:
            question: The natural language question to ask about the code
            similarity_threshold: Minimum similarity score for semantic matches
            max_results: Maximum number of results to return
            include_raw_data: Whether to include complete raw data in output
            format: Output format (\"text\" or \"json\")

        Returns:
            Detailed debug information about the query execution and results
        ", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/services/query/src/query/main.py", line_number: 365}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "start_time", filepath: "/app/services/query/src/query/main.py", line_number: 368}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "debug_info", filepath: "/app/services/query/src/query/main.py", line_number: 369}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00489
MERGE (s:Variable {name: "semantic_start", filepath: "/app/services/query/src/query/main.py", line_number: 381}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "semantic_results", filepath: "/app/services/query/src/query/main.py", line_number: 382}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "semantic_time", filepath: "/app/services/query/src/query/main.py", line_number: 383}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "file_paths", filepath: "/app/services/query/src/query/main.py", line_number: 388}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_start", filepath: "/app/services/query/src/query/main.py", line_number: 395}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00490
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 396}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 401}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 406}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_time", filepath: "/app/services/query/src/query/main.py", line_number: 409}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "total_time", filepath: "/app/services/query/src/query/main.py", line_number: 415}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00491
MERGE (s:Method {name: "_format_debug_output", filepath: "/app/services/query/src/query/main.py", start_line: 437}) SET s.end_line = 534, s.scope = "QueryService", s.docstring = "Format debug information as readable text output", s.signature = "def";
MERGE (s:Variable {name: "logger", filepath: "/app/services/query/src/query/main.py", line_number: 439}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "output", filepath: "/app/services/query/src/query/main.py", line_number: 442}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "semantic_results", filepath: "/app/services/query/src/query/main.py", line_number: 471}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "content", filepath: "/app/services/query/src/query/main.py", line_number: 484}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00492
MERGE (s:Variable {name: "content", filepath: "/app/services/query/src/query/main.py", line_number: 486}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 491}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/main.py", line_number: 494}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "imports", filepath: "/app/services/query/src/query/main.py", line_number: 503}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "references", filepath: "/app/services/query/src/query/main.py", line_number: 512}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00493
MERGE (s:Method {name: "_semantic_search", filepath: "/app/services/query/src/query/main.py", start_line: 536}) SET s.end_line = 677, s.scope = "QueryService", s.docstring = "
        Execute semantic search using Supabase\'s vector search capabilities.

        Args:
            question: The search query
            similarity_threshold: Minimum similarity score (0.0-1.0)
            max_results: Maximum number of results to return

        Returns:
            List of matched documents with content and metadata
        ", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/services/query/src/query/main.py", line_number: 553}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "supabase_key_str", filepath: "/app/services/query/src/query/main.py", line_number: 558}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "supabase", filepath: "/app/services/query/src/query/main.py", line_number: 559}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "openai_key_str", filepath: "/app/services/query/src/query/main.py", line_number: 563}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00494
MERGE (s:Variable {name: "openai_client", filepath: "/app/services/query/src/query/main.py", line_number: 564}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "embedding_response", filepath: "/app/services/query/src/query/main.py", line_number: 569}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "query_embedding", filepath: "/app/services/query/src/query/main.py", line_number: 573}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "dimensions", filepath: "/app/services/query/src/query/main.py", line_number: 574}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "nonzero_values", filepath: "/app/services/query/src/query/main.py", line_number: 583}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00495
MERGE (s:Variable {name: "embedding_stats", filepath: "/app/services/query/src/query/main.py", line_number: 584}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "original_threshold", filepath: "/app/services/query/src/query/main.py", line_number: 594}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "fallback_threshold", filepath: "/app/services/query/src/query/main.py", line_number: 595}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "response", filepath: "/app/services/query/src/query/main.py", line_number: 600}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "results", filepath: "/app/services/query/src/query/main.py", line_number: 611}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00496
MERGE (s:Variable {name: "result", filepath: "/app/services/query/src/query/main.py", line_number: 613}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "fallback_response", filepath: "/app/services/query/src/query/main.py", line_number: 635}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "results", filepath: "/app/services/query/src/query/main.py", line_number: 645}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "result", filepath: "/app/services/query/src/query/main.py", line_number: 647}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Method {name: "_get_structural_data", filepath: "/app/services/query/src/query/main.py", start_line: 679}) SET s.end_line = 798, s.scope = "QueryService", s.docstring = "
        Execute structural queries on the graph database using Neo4j.

        Args:
            file_paths: List of file paths to query for structural data
            question: The original search question (for context)

        Returns:
            Dictionary with symbols, imports, and references information
        ", s.signature = "async";

// BATCH 00497
MERGE (s:Variable {name: "logger", filepath: "/app/services/query/src/query/main.py", line_number: 694}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "neo_service", filepath: "/app/services/query/src/query/main.py", line_number: 699}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "file_paths_str", filepath: "/app/services/query/src/query/main.py", line_number: 714}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "symbols_query", filepath: "/app/services/query/src/query/main.py", line_number: 717}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "imports_query", filepath: "/app/services/query/src/query/main.py", line_number: 725}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00498
MERGE (s:Variable {name: "references_query", filepath: "/app/services/query/src/query/main.py", line_number: 732}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/main.py", line_number: 741}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "imports", filepath: "/app/services/query/src/query/main.py", line_number: 742}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "references", filepath: "/app/services/query/src/query/main.py", line_number: 743}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "symbols_result", filepath: "/app/services/query/src/query/main.py", line_number: 747}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00499
MERGE (s:Variable {name: "symbols", filepath: "/app/services/query/src/query/main.py", line_number: 748}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "imports_result", filepath: "/app/services/query/src/query/main.py", line_number: 757}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "imports", filepath: "/app/services/query/src/query/main.py", line_number: 758}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "references_result", filepath: "/app/services/query/src/query/main.py", line_number: 767}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "references", filepath: "/app/services/query/src/query/main.py", line_number: 768}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00500
MERGE (s:Method {name: "_parse_cypher_result", filepath: "/app/services/query/src/query/main.py", start_line: 800}) SET s.end_line = 855, s.scope = "QueryService", s.docstring = "
        Parse cypher-shell output into structured data

        Args:
            result: String result from Neo4j query
            columns: Expected column names

        Returns:
            List of dictionaries with parsed data
        ", s.signature = "def";
MERGE (s:Variable {name: "logger", filepath: "/app/services/query/src/query/main.py", line_number: 811}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "lines", filepath: "/app/services/query/src/query/main.py", line_number: 817}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "parsed_data", filepath: "/app/services/query/src/query/main.py", line_number: 824}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "line", filepath: "/app/services/query/src/query/main.py", line_number: 827}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00501
MERGE (s:Variable {name: "parts", filepath: "/app/services/query/src/query/main.py", line_number: 829}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "row_data", filepath: "/app/services/query/src/query/main.py", line_number: 836}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "value", filepath: "/app/services/query/src/query/main.py", line_number: 840}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "value", filepath: "/app/services/query/src/query/main.py", line_number: 845}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Method {name: "_format_result", filepath: "/app/services/query/src/query/main.py", start_line: 857}) SET s.end_line = 887, s.scope = "QueryService", s.docstring = "Format query results into a human-readable string", s.signature = "def";

// BATCH 00502
MERGE (s:Variable {name: "logger", filepath: "/app/services/query/src/query/main.py", line_number: 859}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "output", filepath: "/app/services/query/src/query/main.py", line_number: 862}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "semantic_results", filepath: "/app/services/query/src/query/main.py", line_number: 866}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "content", filepath: "/app/services/query/src/query/main.py", line_number: 873}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Variable {name: "content", filepath: "/app/services/query/src/query/main.py", line_number: 875}) SET s.end_line = -1, s.scope = "QueryService";

// BATCH 00503
MERGE (s:Variable {name: "structural_data", filepath: "/app/services/query/src/query/main.py", line_number: 880}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (s:Method {name: "log_last_query", filepath: "/app/services/query/src/query/main.py", start_line: 890}) SET s.end_line = 919, s.scope = "QueryService", s.docstring = "
        Write the last query execution details to a log file for later inspection.
        Useful for debugging when immediate console output isn\'t practical.

        Args:
            log_file: Path to write the log file

        Returns:
            Path to the log file or error message
        ", s.signature = "async";
MERGE (s:Variable {name: "debug_info", filepath: "/app/services/query/src/query/main.py", line_number: 907}) SET s.end_line = -1, s.scope = "QueryService";
MERGE (f:File {filepath: "/app/services/query/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/services/query/pyproject.toml" ON MATCH SET f.language = "unknown";
MERGE (f:File {filepath: "/app/services/neo/src/neo/__init__.py"}) ON CREATE SET f.language = "python", f.path = "/app/services/neo/src/neo/__init__.py" ON MATCH SET f.language = "python";

// BATCH 00504
MERGE (f:File {filepath: "/app/services/neo/src/neo/main.py"}) ON CREATE SET f.language = "python", f.path = "/app/services/neo/src/neo/main.py" ON MATCH SET f.language = "python";
MERGE (s:Function {name: "green", filepath: "/app/services/neo/src/neo/main.py", start_line: 11}) SET s.end_line = 12, s.signature = "def";
MERGE (s:Class {name: "SymbolProperties", filepath: "/app/services/neo/src/neo/main.py", start_line: 18}) SET s.end_line = 44;
MERGE (s:Variable {name: "docstring", filepath: "/app/services/neo/src/neo/main.py", line_number: 21}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Variable {name: "signature", filepath: "/app/services/neo/src/neo/main.py", line_number: 22}) SET s.end_line = -1, s.scope = "SymbolProperties";

// BATCH 00505
MERGE (s:Variable {name: "scope", filepath: "/app/services/neo/src/neo/main.py", line_number: 23}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Variable {name: "parent", filepath: "/app/services/neo/src/neo/main.py", line_number: 24}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Variable {name: "json_data", filepath: "/app/services/neo/src/neo/main.py", line_number: 28}) SET s.end_line = -1, s.scope = "SymbolProperties";
MERGE (s:Method {name: "from_dict", filepath: "/app/services/neo/src/neo/main.py", start_line: 31}) SET s.end_line = 44, s.scope = "SymbolProperties", s.docstring = "Create a SymbolProperties from a dictionary", s.signature = "def";
MERGE (s:Variable {name: "props", filepath: "/app/services/neo/src/neo/main.py", line_number: 34}) SET s.end_line = -1, s.scope = "SymbolProperties";

// BATCH 00506
MERGE (s:Class {name: "RelationshipProperties", filepath: "/app/services/neo/src/neo/main.py", start_line: 48}) SET s.end_line = 63;
MERGE (s:Variable {name: "type", filepath: "/app/services/neo/src/neo/main.py", line_number: 50}) SET s.end_line = -1, s.scope = "RelationshipProperties";
MERGE (s:Variable {name: "name", filepath: "/app/services/neo/src/neo/main.py", line_number: 51}) SET s.end_line = -1, s.scope = "RelationshipProperties";
MERGE (s:Variable {name: "value", filepath: "/app/services/neo/src/neo/main.py", line_number: 52}) SET s.end_line = -1, s.scope = "RelationshipProperties";
MERGE (s:Variable {name: "weight", filepath: "/app/services/neo/src/neo/main.py", line_number: 53}) SET s.end_line = -1, s.scope = "RelationshipProperties";

// BATCH 00507
MERGE (s:Method {name: "from_dict", filepath: "/app/services/neo/src/neo/main.py", start_line: 56}) SET s.end_line = 63, s.scope = "RelationshipProperties", s.docstring = "Create a RelationshipProperties from a dictionary", s.signature = "def";
MERGE (s:Variable {name: "props", filepath: "/app/services/neo/src/neo/main.py", line_number: 58}) SET s.end_line = -1, s.scope = "RelationshipProperties";
MERGE (s:Class {name: "NeoService", filepath: "/app/services/neo/src/neo/main.py", start_line: 67}) SET s.end_line = 611;
MERGE (s:Variable {name: "config", filepath: "/app/services/neo/src/neo/main.py", line_number: 69}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "config_file", filepath: "/app/services/neo/src/neo/main.py", line_number: 70}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00508
MERGE (s:Variable {name: "password", filepath: "/app/services/neo/src/neo/main.py", line_number: 71}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "github_access_token", filepath: "/app/services/neo/src/neo/main.py", line_number: 72}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "neo_auth", filepath: "/app/services/neo/src/neo/main.py", line_number: 73}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "neo_service", filepath: "/app/services/neo/src/neo/main.py", line_number: 74}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "cypher_shell_client", filepath: "/app/services/neo/src/neo/main.py", line_number: 75}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00509
MERGE (s:Variable {name: "neo_data", filepath: "/app/services/neo/src/neo/main.py", line_number: 76}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "create", filepath: "/app/services/neo/src/neo/main.py", start_line: 79}) SET s.end_line = 96, s.scope = "NeoService", s.docstring = " Create ", s.signature = "async";
MERGE (s:Variable {name: "config_str", filepath: "/app/services/neo/src/neo/main.py", line_number: 88}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "config_dict", filepath: "/app/services/neo/src/neo/main.py", line_number: 89}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "create_neo_service", filepath: "/app/services/neo/src/neo/main.py", start_line: 99}) SET s.end_line = 133, s.scope = "NeoService", s.docstring = "Create a Neo4j service as a Dagger service", s.signature = "async";

// BATCH 00510
MERGE (s:Variable {name: "plugin_string", filepath: "/app/services/neo/src/neo/main.py", line_number: 107}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "create_neo_client", filepath: "/app/services/neo/src/neo/main.py", start_line: 136}) SET s.end_line = 168, s.scope = "NeoService", s.docstring = "Create a Neo4j client container with cypher-shell", s.signature = "async";
MERGE (s:Variable {name: "neo_service", filepath: "/app/services/neo/src/neo/main.py", line_number: 146}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "source", filepath: "/app/services/neo/src/neo/main.py", line_number: 149}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "ensure_client", filepath: "/app/services/neo/src/neo/main.py", start_line: 171}) SET s.end_line = 175, s.scope = "NeoService", s.docstring = "Ensure we have a client container, creating it if needed", s.signature = "async";

// BATCH 00511
MERGE (s:Method {name: "run_query", filepath: "/app/services/neo/src/neo/main.py", start_line: 178}) SET s.end_line = 196, s.scope = "NeoService", s.docstring = "Run a query against the Neo4j service", s.signature = "async";
MERGE (s:Variable {name: "client", filepath: "/app/services/neo/src/neo/main.py", line_number: 186}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "run_batch_queries", filepath: "/app/services/neo/src/neo/main.py", start_line: 199}) SET s.end_line = 208, s.scope = "NeoService", s.docstring = "Run multiple queries in a single transaction for better performance", s.signature = "async";
MERGE (s:Variable {name: "combined", filepath: "/app/services/neo/src/neo/main.py", line_number: 205}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "test_connection", filepath: "/app/services/neo/src/neo/main.py", start_line: 211}) SET s.end_line = 288, s.scope = "NeoService", s.docstring = "Test connection to Neo4j service using improved parsing", s.signature = "async";

// BATCH 00512
MERGE (s:Variable {name: "connection_result", filepath: "/app/services/neo/src/neo/main.py", line_number: 217}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "total_nodes_raw", filepath: "/app/services/neo/src/neo/main.py", line_number: 218}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "total_rels_raw", filepath: "/app/services/neo/src/neo/main.py", line_number: 219}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "node_stats_raw", filepath: "/app/services/neo/src/neo/main.py", line_number: 220}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "rel_stats_raw", filepath: "/app/services/neo/src/neo/main.py", line_number: 221}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00513
MERGE (s:Variable {name: "sample_rels_raw", filepath: "/app/services/neo/src/neo/main.py", line_number: 224}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "improved_simple_parse", filepath: "/app/services/neo/src/neo/main.py", start_line: 233}) SET s.end_line = 241, s.scope = "NeoService", s.signature = "def";
MERGE (s:Variable {name: "lines", filepath: "/app/services/neo/src/neo/main.py", line_number: 236}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "clean_line", filepath: "/app/services/neo/src/neo/main.py", line_number: 238}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "improved_parse_list", filepath: "/app/services/neo/src/neo/main.py", start_line: 243}) SET s.end_line = 257, s.scope = "NeoService", s.signature = "def";

// BATCH 00514
MERGE (s:Variable {name: "lines", filepath: "/app/services/neo/src/neo/main.py", line_number: 246}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "data_lines", filepath: "/app/services/neo/src/neo/main.py", line_number: 247}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "clean_line", filepath: "/app/services/neo/src/neo/main.py", line_number: 254}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "connection_status", filepath: "/app/services/neo/src/neo/main.py", line_number: 260}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "total_nodes", filepath: "/app/services/neo/src/neo/main.py", line_number: 261}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00515
MERGE (s:Variable {name: "total_rels", filepath: "/app/services/neo/src/neo/main.py", line_number: 262}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "node_types", filepath: "/app/services/neo/src/neo/main.py", line_number: 263}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "rel_types", filepath: "/app/services/neo/src/neo/main.py", line_number: 264}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "sample_rels", filepath: "/app/services/neo/src/neo/main.py", line_number: 267}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "connect", filepath: "/app/services/neo/src/neo/main.py", start_line: 291}) SET s.end_line = 300, s.scope = "NeoService", s.docstring = "Verify connection to Neo4j", s.signature = "def";

// BATCH 00516
MERGE (s:Variable {name: "logger", filepath: "/app/services/neo/src/neo/main.py", line_number: 298}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "clear_database", filepath: "/app/services/neo/src/neo/main.py", start_line: 303}) SET s.end_line = 313, s.scope = "NeoService", s.docstring = "Clear all nodes and relationships from the database", s.signature = "async";
MERGE (s:Variable {name: "query", filepath: "/app/services/neo/src/neo/main.py", line_number: 307}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "logger", filepath: "/app/services/neo/src/neo/main.py", line_number: 311}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "add_file_node", filepath: "/app/services/neo/src/neo/main.py", start_line: 316}) SET s.end_line = 334, s.scope = "NeoService", s.docstring = "Add a file node to the graph", s.signature = "async";

// BATCH 00517
MERGE (s:Variable {name: "filepath", filepath: "/app/services/neo/src/neo/main.py", line_number: 324}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "language", filepath: "/app/services/neo/src/neo/main.py", line_number: 325}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "query", filepath: "/app/services/neo/src/neo/main.py", line_number: 328}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "logger", filepath: "/app/services/neo/src/neo/main.py", line_number: 332}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "add_symbol", filepath: "/app/services/neo/src/neo/main.py", start_line: 337}) SET s.end_line = 423, s.scope = "NeoService", s.docstring = "Add a symbol node to the graph with connection to its file", s.signature = "async";

// BATCH 00518
MERGE (s:Variable {name: "logger", filepath: "/app/services/neo/src/neo/main.py", line_number: 349}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "name", filepath: "/app/services/neo/src/neo/main.py", line_number: 352}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "filepath", filepath: "/app/services/neo/src/neo/main.py", line_number: 353}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "end_line_str", filepath: "/app/services/neo/src/neo/main.py", line_number: 356}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "start_line_str", filepath: "/app/services/neo/src/neo/main.py", line_number: 357}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00519
MERGE (s:Variable {name: "props", filepath: "/app/services/neo/src/neo/main.py", line_number: 360}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "escaped_docstring", filepath: "/app/services/neo/src/neo/main.py", line_number: 365}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "escaped_signature", filepath: "/app/services/neo/src/neo/main.py", line_number: 370}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "extra_props", filepath: "/app/services/neo/src/neo/main.py", line_number: 384}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "escaped_v", filepath: "/app/services/neo/src/neo/main.py", line_number: 392}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00520
MERGE (s:Variable {name: "escaped_json", filepath: "/app/services/neo/src/neo/main.py", line_number: 396}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "properties_str", filepath: "/app/services/neo/src/neo/main.py", line_number: 399}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "query", filepath: "/app/services/neo/src/neo/main.py", line_number: 402}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "logger", filepath: "/app/services/neo/src/neo/main.py", line_number: 421}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "add_relationship", filepath: "/app/services/neo/src/neo/main.py", start_line: 426}) SET s.end_line = 477, s.scope = "NeoService", s.docstring = "Add a relationship between two files in the graph", s.signature = "async";

// BATCH 00521
MERGE (s:Variable {name: "start_filepath", filepath: "/app/services/neo/src/neo/main.py", line_number: 439}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "end_filepath", filepath: "/app/services/neo/src/neo/main.py", line_number: 440}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "relationship_type", filepath: "/app/services/neo/src/neo/main.py", line_number: 441}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "props_str", filepath: "/app/services/neo/src/neo/main.py", line_number: 444}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "props_parts", filepath: "/app/services/neo/src/neo/main.py", line_number: 446}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00522
MERGE (s:Variable {name: "props_str", filepath: "/app/services/neo/src/neo/main.py", line_number: 462}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "query", filepath: "/app/services/neo/src/neo/main.py", line_number: 465}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "logger", filepath: "/app/services/neo/src/neo/main.py", line_number: 474}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "debug_database", filepath: "/app/services/neo/src/neo/main.py", start_line: 480}) SET s.end_line = 514, s.scope = "NeoService", s.docstring = "Debug function to see raw query outputs", s.signature = "async";
MERGE (s:Variable {name: "logger", filepath: "/app/services/neo/src/neo/main.py", line_number: 482}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00523
MERGE (s:Variable {name: "count_query", filepath: "/app/services/neo/src/neo/main.py", line_number: 487}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "raw_count", filepath: "/app/services/neo/src/neo/main.py", line_number: 488}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "labels_query", filepath: "/app/services/neo/src/neo/main.py", line_number: 490}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "raw_labels", filepath: "/app/services/neo/src/neo/main.py", line_number: 491}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "rel_types_query", filepath: "/app/services/neo/src/neo/main.py", line_number: 493}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00524
MERGE (s:Variable {name: "raw_rel_types", filepath: "/app/services/neo/src/neo/main.py", line_number: 494}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "simple_test", filepath: "/app/services/neo/src/neo/main.py", start_line: 517}) SET s.end_line = 603, s.scope = "NeoService", s.docstring = "Simple test with improved parsing logic", s.signature = "async";
MERGE (s:Variable {name: "count_result", filepath: "/app/services/neo/src/neo/main.py", line_number: 523}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "labels_result", filepath: "/app/services/neo/src/neo/main.py", line_number: 524}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "rel_types_result", filepath: "/app/services/neo/src/neo/main.py", line_number: 525}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00525
MERGE (s:Variable {name: "debug_info", filepath: "/app/services/neo/src/neo/main.py", line_number: 528}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "improved_simple_parse", filepath: "/app/services/neo/src/neo/main.py", start_line: 541}) SET s.end_line = 557, s.scope = "NeoService", s.docstring = "Parse a single value result more robustly", s.signature = "def";
MERGE (s:Variable {name: "lines", filepath: "/app/services/neo/src/neo/main.py", line_number: 546}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "clean_line", filepath: "/app/services/neo/src/neo/main.py", line_number: 552}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "improved_parse_list", filepath: "/app/services/neo/src/neo/main.py", start_line: 559}) SET s.end_line = 583, s.scope = "NeoService", s.docstring = "Parse list results more robustly", s.signature = "def";

// BATCH 00526
MERGE (s:Variable {name: "lines", filepath: "/app/services/neo/src/neo/main.py", line_number: 564}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "data_lines", filepath: "/app/services/neo/src/neo/main.py", line_number: 568}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "clean_line", filepath: "/app/services/neo/src/neo/main.py", line_number: 579}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "node_count", filepath: "/app/services/neo/src/neo/main.py", line_number: 585}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Variable {name: "node_types", filepath: "/app/services/neo/src/neo/main.py", line_number: 586}) SET s.end_line = -1, s.scope = "NeoService";

// BATCH 00527
MERGE (s:Variable {name: "rel_types", filepath: "/app/services/neo/src/neo/main.py", line_number: 587}) SET s.end_line = -1, s.scope = "NeoService";
MERGE (s:Method {name: "_get_logger", filepath: "/app/services/neo/src/neo/main.py", start_line: 605}) SET s.end_line = 611, s.scope = "NeoService", s.docstring = "Get a logger for this service", s.signature = "def";
MERGE (f:File {filepath: "/app/services/neo/pyproject.toml"}) ON CREATE SET f.language = "unknown", f.path = "/app/services/neo/pyproject.toml" ON MATCH SET f.language = "unknown";
