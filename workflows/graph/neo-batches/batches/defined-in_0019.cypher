// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/card.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/card.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
