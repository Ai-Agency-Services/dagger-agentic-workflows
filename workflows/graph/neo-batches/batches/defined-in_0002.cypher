// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/button.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/button.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Interface {filepath: "/app/src/components/blocks/hero.tsx"}) MATCH (f:File {filepath: "/app/src/components/blocks/hero.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/anime-navbar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/anime-navbar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Function {filepath: "/app/src/pages/contact/ContactHero.tsx"}) MATCH (f:File {filepath: "/app/src/pages/contact/ContactHero.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
