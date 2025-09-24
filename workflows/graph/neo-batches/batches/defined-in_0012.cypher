// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/menubar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/menubar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Function {filepath: "/app/src/components/ui/carousel.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/carousel.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Function {filepath: "/app/src/components/ui/spotlight.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/spotlight.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/integrations/supabase/types.ts"}) MATCH (f:File {filepath: "/app/src/integrations/supabase/types.ts"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/App.tsx"}) MATCH (f:File {filepath: "/app/src/App.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
