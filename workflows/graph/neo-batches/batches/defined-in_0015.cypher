// BATCH 00001
MATCH (s:Interface {filepath: "/app/src/components/ui/anime-navbar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/anime-navbar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/components/Navigation.tsx"}) MATCH (f:File {filepath: "/app/src/components/Navigation.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/dropdown-menu.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/dropdown-menu.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/avatar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/avatar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/pages/Contact.tsx"}) MATCH (f:File {filepath: "/app/src/pages/Contact.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
