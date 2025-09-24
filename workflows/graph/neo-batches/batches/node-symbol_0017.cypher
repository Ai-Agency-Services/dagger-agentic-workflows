// BATCH 00001
MERGE (s:Variable {name: "navItems", filepath: "/app/src/components/Navigation.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "isLegalPage", filepath: "/app/src/components/Navigation.tsx", line_number: 16}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "activeItem", filepath: "/app/src/components/Navigation.tsx", line_number: 20}) SET s.end_line = -1;

// BATCH 00004
MERGE (f:File {filepath: "/app/src/vite-env.d.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/vite-env.d.ts" ON MATCH SET f.language = "typescript";

// BATCH 00005
MERGE (f:File {filepath: "/app/src/main.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/main.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00006
MERGE (s:Variable {name: "rootElement", filepath: "/app/src/main.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00007
MERGE (f:File {filepath: "/app/src/App.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/App.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00008
MERGE (s:Variable {name: "queryClient", filepath: "/app/src/App.tsx", line_number: 14}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Variable {name: "App", filepath: "/app/src/App.tsx", line_number: 16}) SET s.end_line = -1;

// BATCH 00010
MERGE (f:File {filepath: "/app/src/integrations/supabase/types.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/integrations/supabase/types.ts" ON MATCH SET f.language = "typescript";

// BATCH 00011
MERGE (s:Variable {name: "Constants", filepath: "/app/src/integrations/supabase/types.ts", line_number: 353}) SET s.end_line = -1;

// BATCH 00012
MERGE (f:File {filepath: "/app/src/pages/AboutUs.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/AboutUs.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00013
MERGE (f:File {filepath: "/app/src/integrations/supabase/client.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/integrations/supabase/client.ts" ON MATCH SET f.language = "typescript";

// BATCH 00014
MERGE (s:Variable {name: "SUPABASE_URL", filepath: "/app/src/integrations/supabase/client.ts", line_number: 5}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Variable {name: "SUPABASE_PUBLISHABLE_KEY", filepath: "/app/src/integrations/supabase/client.ts", line_number: 6}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Variable {name: "supabase", filepath: "/app/src/integrations/supabase/client.ts", line_number: 11}) SET s.end_line = -1;

// BATCH 00017
MERGE (f:File {filepath: "/app/src/pages/TermsOfService.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/TermsOfService.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00018
MERGE (f:File {filepath: "/app/src/pages/Index.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/pages/Index.tsx" ON MATCH SET f.language = "typescript";
