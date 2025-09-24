// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/spotlight.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/spotlight.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Interface {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/table.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/table.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/supabase/functions/send-contact-email/index.ts"}) MATCH (f:File {filepath: "/app/supabase/functions/send-contact-email/index.ts"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Function {filepath: "/app/src/components/ui/chart.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/chart.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
