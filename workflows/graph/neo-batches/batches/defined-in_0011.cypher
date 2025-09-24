// BATCH 00001
MATCH (s:Function {filepath: "/app/src/components/ui/form.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/form.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00002
MATCH (s:Variable {filepath: "/app/src/components/ui/tooltip.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/tooltip.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00003
MATCH (s:Variable {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MATCH (f:File {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00004
MATCH (s:Variable {filepath: "/app/src/pages/Index.tsx"}) MATCH (f:File {filepath: "/app/src/pages/Index.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);

// BATCH 00005
MATCH (s:Variable {filepath: "/app/src/components/ui/sheet.tsx"}) MATCH (f:File {filepath: "/app/src/components/ui/sheet.tsx"}) MERGE (s)-[:DEFINED_IN]->(f);
