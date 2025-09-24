// BATCH 00001
MATCH (s:Function {filepath: "/app/src/components/ui/sonner.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/sonner.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/components/ui/chart.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/chart.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/form.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/form.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/integrations/supabase/client.ts"}) MATCH (f:File {filepath: "/app/src/integrations/supabase/client.ts"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/components/ui/accordion.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/accordion.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
