// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/alert.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/alert.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Interface {filepath: "/app/src/components/ui/badge.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/badge.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/collapsible.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/collapsible.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Function {filepath: "/app/src/pages/Index.tsx"}) MATCH (f:File {filepath: "/app/src/pages/Index.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Function {filepath: "/app/src/hooks/use-toast.ts"}) MATCH (f:File {filepath: "/app/src/hooks/use-toast.ts"}) MERGE (s)-[:DEFINED_IN]->(f);
