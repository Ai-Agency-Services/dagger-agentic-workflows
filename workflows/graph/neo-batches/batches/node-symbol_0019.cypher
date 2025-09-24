// BATCH 00001
MERGE (f:File {filepath: "/app/src/lib/utils.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/lib/utils.ts" ON MATCH SET f.language = "typescript";

// BATCH 00002
MERGE (s:Function {name: "cn", filepath: "/app/src/lib/utils.ts", start_line: 4}) SET s.end_line = 6;

// BATCH 00003
MERGE (f:File {filepath: "/app/postcss.config.js"}) ON CREATE SET f.language = "javascript", f.path = "/app/postcss.config.js" ON MATCH SET f.language = "javascript";

// BATCH 00004
MERGE (f:File {filepath: "/app/postcss.config.js"}) MERGE (f)-[:EXPORTS]->(:ConfigExport {type: "configuration"});

// BATCH 00005
MERGE (f:File {filepath: "/app/jest.setup.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/jest.setup.ts" ON MATCH SET f.language = "typescript";

// BATCH 00006
MERGE (s:Interface {name: "Matchers", filepath: "/app/jest.setup.ts", start_line: 7}) SET s.end_line = 15;

// BATCH 00007
MERGE (f:File {filepath: "/app/eslint.config.js"}) ON CREATE SET f.language = "javascript", f.path = "/app/eslint.config.js" ON MATCH SET f.language = "javascript";

// BATCH 00008
MERGE (f:File {filepath: "/app/eslint.config.js"}) MERGE (f)-[:EXPORTS]->(:ConfigExport {type: "configuration"});

// BATCH 00009
MERGE (f:File {filepath: "/app/supabase/functions/send-contact-email/index.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/supabase/functions/send-contact-email/index.ts" ON MATCH SET f.language = "typescript";

// BATCH 00010
MERGE (s:Variable {name: "sendgridApiKey", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 6}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Variable {name: "recaptchaSecret", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 7}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "supabaseUrl", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 8}) SET s.end_line = -1;

// BATCH 00013
MERGE (s:Variable {name: "supabaseServiceRoleKey", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 9}) SET s.end_line = -1;

// BATCH 00014
MERGE (s:Variable {name: "supabase", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 12}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Variable {name: "corsHeaders", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 16}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Interface {name: "ContactFormData", filepath: "/app/supabase/functions/send-contact-email/index.ts", start_line: 22}) SET s.end_line = 31;

// BATCH 00017
MERGE (s:Function {name: "verifyCaptcha", filepath: "/app/supabase/functions/send-contact-email/index.ts", start_line: 33}) SET s.end_line = 74;

// BATCH 00018
MERGE (s:Variable {name: "response", filepath: "/app/supabase/functions/send-contact-email/index.ts", line_number: 46}) SET s.end_line = -1;
