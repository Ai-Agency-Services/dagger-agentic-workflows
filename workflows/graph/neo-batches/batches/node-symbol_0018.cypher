// BATCH 00001
MERGE (s:Variable {name: "navigate", filepath: "/app/src/pages/Index.tsx", line_number: 14}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Function {name: "handleNavigation", filepath: "/app/src/pages/Index.tsx", start_line: 16}) SET s.end_line = -1;

// BATCH 00003
MERGE (f:File {filepath: "/app/src/pages/Contact.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/Contact.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00004
MERGE (s:Interface {name: "Window", filepath: "/app/src/pages/Contact.tsx", start_line: 8}) SET s.end_line = 13;

// BATCH 00005
MERGE (s:Variable {name: "RECAPTCHA_SITE_KEY", filepath: "/app/src/pages/Contact.tsx", line_number: 16}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "script", filepath: "/app/src/pages/Contact.tsx", line_number: 23}) SET s.end_line = -1;

// BATCH 00007
MERGE (f:File {filepath: "/app/src/pages/PrivacyPolicy.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/PrivacyPolicy.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00008
MERGE (f:File {filepath: "/app/src/pages/contact/types.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/contact/types.ts" ON MATCH SET f.language = "typescript";

// BATCH 00009
MERGE (f:File {filepath: "/app/src/pages/contact/ContactForm.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/contact/ContactForm.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00010
MERGE (s:Variable {name: "RECAPTCHA_SITE_KEY", filepath: "/app/src/pages/contact/ContactForm.tsx", line_number: 10}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Variable {name: "executeRecaptcha", filepath: "/app/src/pages/contact/ContactForm.tsx", line_number: 15}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Function {name: "onSubmit", filepath: "/app/src/pages/contact/ContactForm.tsx", start_line: 29}) SET s.end_line = -1;

// BATCH 00013
MERGE (s:Variable {name: "token", filepath: "/app/src/pages/contact/ContactForm.tsx", line_number: 31}) SET s.end_line = -1;

// BATCH 00014
MERGE (f:File {filepath: "/app/src/pages/contact/ContactHero.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/contact/ContactHero.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00015
MERGE (s:Function {name: "ContactHero", filepath: "/app/src/pages/contact/ContactHero.tsx", start_line: 4}) SET s.end_line = -1;

// BATCH 00016
MERGE (f:File {filepath: "/app/src/pages/AgentTask.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/AgentTask.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00017
MERGE (s:Function {name: "AgentTask", filepath: "/app/src/pages/AgentTask.tsx", start_line: 7}) SET s.end_line = -1;

// BATCH 00018
MERGE (s:Function {name: "handleSubmit", filepath: "/app/src/pages/AgentTask.tsx", start_line: 11}) SET s.end_line = -1;
