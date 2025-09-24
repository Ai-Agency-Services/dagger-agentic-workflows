// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/pagination.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/pagination.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/components/ui/splite.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/splite.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Function {filepath: "/app/src/components/ui/calendar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/calendar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Interface {filepath: "/app/src/components/ui/textarea.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/textarea.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Interface {filepath: "/app/src/components/blocks/VideoControls.tsx"}) MATCH (f:File {filepath: "/app/src/components/blocks/VideoControls.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
