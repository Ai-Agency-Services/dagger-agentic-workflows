// BATCH 00001
MATCH (s:Function {filepath: "/app/src/pages/AgentTask.tsx"}) MATCH (f:File {filepath: "/app/src/pages/AgentTask.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Function {filepath: "/app/src/components/ui/sidebar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Function {filepath: "/app/src/components/blocks/CoverAiIntroduction.tsx"}) MATCH (f:File {filepath: "/app/src/components/blocks/CoverAiIntroduction.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/input-otp.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/input-otp.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Function {filepath: "/app/src/components/ui/badge.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/badge.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
