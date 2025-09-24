// BATCH 00001
MATCH (s:Function {filepath: "/app/src/hooks/use-mobile.tsx"}) MATCH (f:File {filepath: "/app/src/hooks/use-mobile.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/components/ui/badge.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/badge.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/tabs.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/tabs.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/textarea.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/textarea.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/components/blocks/PromoVideo.tsx"}) MATCH (f:File {filepath: "/app/src/components/blocks/PromoVideo.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
