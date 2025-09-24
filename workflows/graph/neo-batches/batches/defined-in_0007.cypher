// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/context-menu.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/context-menu.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/components/ui/select.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/select.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Function {filepath: "/app/src/components/blocks/PromoVideo.tsx"}) MATCH (f:File {filepath: "/app/src/components/blocks/PromoVideo.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Function {filepath: "/app/src/components/blocks/VideoControls.tsx"}) MATCH (f:File {filepath: "/app/src/components/blocks/VideoControls.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/components/ui/radio-group.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/radio-group.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
