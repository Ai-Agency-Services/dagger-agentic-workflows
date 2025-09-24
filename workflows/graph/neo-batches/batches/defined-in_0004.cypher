// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/scroll-area.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/scroll-area.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Function {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Interface {filepath: "/app/src/pages/Contact.tsx"}) MATCH (f:File {filepath: "/app/src/pages/Contact.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/sidebar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Interface {filepath: "/app/src/hooks/use-toast.ts"}) MATCH (f:File {filepath: "/app/src/hooks/use-toast.ts"}) MERGE (s)-[:DEFINED_IN]->(f);
