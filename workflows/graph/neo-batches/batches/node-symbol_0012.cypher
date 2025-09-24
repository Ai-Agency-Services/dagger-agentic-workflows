// BATCH 00001
MERGE (s:Variable {name: "TabsList", filepath: "/app/src/components/ui/tabs.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00002
MERGE (f:File {filepath: "/app/src/components/ui/progress.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/progress.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00003
MERGE (f:File {filepath: "/app/src/components/ui/alert.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/alert.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00004
MERGE (s:Variable {name: "alertVariants", filepath: "/app/src/components/ui/alert.tsx", line_number: 6}) SET s.end_line = -1;

// BATCH 00005
MERGE (f:File {filepath: "/app/src/components/ui/scroll-area.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/scroll-area.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00006
MERGE (s:Variable {name: "ScrollArea", filepath: "/app/src/components/ui/scroll-area.tsx", line_number: 6}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "ScrollBar", filepath: "/app/src/components/ui/scroll-area.tsx", line_number: 24}) SET s.end_line = -1;

// BATCH 00008
MERGE (f:File {filepath: "/app/src/components/ui/drawer.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/drawer.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00009
MERGE (f:File {filepath: "/app/src/components/ui/pagination.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/pagination.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00010
MERGE (s:Function {name: "Pagination", filepath: "/app/src/components/ui/pagination.tsx", start_line: 7}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Variable {name: "PaginationContent", filepath: "/app/src/components/ui/pagination.tsx", line_number: 17}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "PaginationItem", filepath: "/app/src/components/ui/pagination.tsx", line_number: 29}) SET s.end_line = -1;

// BATCH 00013
MERGE (f:File {filepath: "/app/src/components/ui/splite.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/splite.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00014
MERGE (s:Variable {name: "Spline", filepath: "/app/src/components/ui/splite.tsx", line_number: 4}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Interface {name: "SplineSceneProps", filepath: "/app/src/components/ui/splite.tsx", start_line: 6}) SET s.end_line = 9;

// BATCH 00016
MERGE (s:Function {name: "SplineScene", filepath: "/app/src/components/ui/splite.tsx", start_line: 11}) SET s.end_line = 26;

// BATCH 00017
MERGE (f:File {filepath: "/app/src/components/ui/select.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/select.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00018
MERGE (s:Variable {name: "Select", filepath: "/app/src/components/ui/select.tsx", line_number: 7}) SET s.end_line = -1;
