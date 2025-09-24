// BATCH 00001
MERGE (s:Variable {name: "data", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 54}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Function {name: "handler", filepath: "/app/supabase/functions/send-contact-email/index.ts", start_line: 76}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "formData", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 84}) SET s.end_line = -1;

// BATCH 00004
MERGE (s:Variable {name: "isValidCaptcha", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 87}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "msg", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 114}) SET s.end_line = -1;

// BATCH 00006
MERGE (f:File {filepath: "/app/jest.config.js"}) ON CREATE SET f.language = "javascript", f.path = "/app/jest.config.js" ON MATCH SET f.language = "javascript";

// BATCH 00007
MERGE (f:File {filepath: "/app/jest.config.js"}) MERGE (f)-[:EXPORTS]->(:ConfigExport {type: "configuration"});

// BATCH 00008
MERGE (f:File {filepath: "/app/tailwind.config.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/tailwind.config.ts" ON MATCH SET f.language = "typescript";

// BATCH 00009
MERGE (f:File {filepath: "/app/tailwind.config.ts"}) MERGE (f)-[:EXPORTS]->(:ConfigExport {type: "configuration"});
