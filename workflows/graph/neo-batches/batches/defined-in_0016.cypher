// BATCH 00001
MATCH (s:Variable {filepath: "/app/src/components/ui/toast.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/toast.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/hooks/use-toast.ts"}) MATCH (f:File {filepath: "/app/src/hooks/use-toast.ts"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Function {filepath: "/app/supabase/functions/send-contact-email/index.ts"}) MATCH (f:File {filepath: "/app/supabase/functions/send-contact-email/index.ts"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Function {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MATCH (f:File {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Function {filepath: "/app/src/components/Navigation.tsx"}) MATCH (f:File {filepath: "/app/src/components/Navigation.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
