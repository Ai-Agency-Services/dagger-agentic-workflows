// BATCH 00001
MERGE (s:Variable {name: "RadioGroupItem", filepath: "/app/src/components/ui/radio-group.tsx", line_number: 21}) SET s.end_line = -1;

// BATCH 00002
MERGE (f:File {filepath: "/app/src/components/ui/breadcrumb.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/breadcrumb.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00003
MERGE (s:Variable {name: "Comp", filepath: "/app/src/components/ui/breadcrumb.tsx", line_number: 48}) SET s.end_line = -1;

// BATCH 00004
MERGE (f:File {filepath: "/app/src/components/ui/aspect-ratio.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/aspect-ratio.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00005
MERGE (s:Variable {name: "AspectRatio", filepath: "/app/src/components/ui/aspect-ratio.tsx", line_number: 3}) SET s.end_line = -1;

// BATCH 00006
MERGE (f:File {filepath: "/app/src/components/ui/sonner.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/sonner.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00007
MERGE (s:Function {name: "Toaster", filepath: "/app/src/components/ui/sonner.tsx", start_line: 6}) SET s.end_line = -1;

// BATCH 00008
MERGE (f:File {filepath: "/app/src/components/ui/toggle-group.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/toggle-group.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00009
MERGE (s:Variable {name: "ToggleGroupContext", filepath: "/app/src/components/ui/toggle-group.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00010
MERGE (s:Variable {name: "ToggleGroup", filepath: "/app/src/components/ui/toggle-group.tsx", line_number: 15}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Variable {name: "ToggleGroupItem", filepath: "/app/src/components/ui/toggle-group.tsx", line_number: 33}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "context", filepath: "/app/src/components/ui/toggle-group.tsx", line_number: 38}) SET s.end_line = -1;

// BATCH 00013
MERGE (f:File {filepath: "/app/src/components/ui/table.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/table.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00014
MERGE (s:Variable {name: "Table", filepath: "/app/src/components/ui/table.tsx", line_number: 5}) SET s.end_line = -1;

// BATCH 00015
MERGE (f:File {filepath: "/app/src/components/ui/anime-navbar.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/anime-navbar.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00016
MERGE (s:Interface {name: "NavItem", filepath: "/app/src/components/ui/anime-navbar.tsx", start_line: 7}) SET s.end_line = 11;

// BATCH 00017
MERGE (s:Interface {name: "NavBarProps", filepath: "/app/src/components/ui/anime-navbar.tsx", start_line: 13}) SET s.end_line = 17;

// BATCH 00018
MERGE (s:Function {name: "handleResize", filepath: "/app/src/components/ui/anime-navbar.tsx", start_line: 30}) SET s.end_line = -1;
