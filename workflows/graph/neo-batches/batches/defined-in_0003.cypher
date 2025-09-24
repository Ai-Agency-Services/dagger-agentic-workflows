// BATCH 00001
MATCH (s:Interface {filepath: "/app/jest.setup.ts"}) MATCH (f:File {filepath: "/app/jest.setup.ts"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/hooks/use-mobile.tsx"}) MATCH (f:File {filepath: "/app/src/hooks/use-mobile.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/components/ui/alert-dialog.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/alert-dialog.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/components/ui/navigation-menu.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/navigation-menu.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Interface {filepath: "/app/supabase/functions/send-contact-email/index.ts"}) MATCH (f:File {filepath: "/app/supabase/functions/send-contact-email/index.ts"}) MERGE (s)-[:DEFINED_IN]->(f);
