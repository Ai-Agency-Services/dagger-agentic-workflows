// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/slider.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/slider.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Function {filepath: "/app/src/components/ui/pagination.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/pagination.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/toggle-group.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/toggle-group.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/dialog.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/dialog.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Function {filepath: "/app/src/lib/utils.ts"}) MATCH (f:File {filepath: "/app/src/lib/utils.ts"}) MERGE (s)-[:DEFINED_IN]->(f);
