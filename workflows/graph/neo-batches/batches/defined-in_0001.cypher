// BATCH 00001
MATCH (s:Interface {filepath: "/app/src/components/ui/splite.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/splite.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/main.tsx"}) MATCH (f:File {filepath: "/app/src/main.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/label.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/label.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Function {filepath: "/app/src/components/ui/footer-section.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/footer-section.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/components/ui/breadcrumb.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/breadcrumb.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
