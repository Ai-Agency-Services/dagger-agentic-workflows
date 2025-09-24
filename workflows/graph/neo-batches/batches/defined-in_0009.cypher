// BATCH 00001
MATCH (s:Function {filepath: "/app/src/components/ui/anime-navbar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/anime-navbar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/components/ui/aspect-ratio.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/aspect-ratio.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Interface {filepath: "/app/src/components/ui/button.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/button.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/hover-card.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/hover-card.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/components/ui/carousel.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/carousel.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
