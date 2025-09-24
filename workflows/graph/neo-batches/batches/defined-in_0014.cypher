// BATCH 00001
MATCH (s:Function {filepath: "/app/src/components/ui/skeleton.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/skeleton.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Function {filepath: "/app/src/components/ui/splite.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/splite.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/toggle.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/toggle.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/popover.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/popover.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/components/ui/input.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/input.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
