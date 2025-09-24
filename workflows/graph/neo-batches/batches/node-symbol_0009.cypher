// BATCH 00001
MERGE (s:Variable {name: "setOpen", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 75}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "openState", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 77}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "toggleSidebar", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 91}) SET s.end_line = -1;

// BATCH 00004
MERGE (s:Function {name: "handleKeyDown", filepath: "/app/src/components/ui/sidebar.tsx", start_line: 99}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "state", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 115}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "contextValue", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 117}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "Comp", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 433}) SET s.end_line = -1;

// BATCH 00008
MERGE (s:Variable {name: "Comp", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 454}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Variable {name: "Comp", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 554}) SET s.end_line = -1;

// BATCH 00010
MERGE (s:Variable {name: "Comp", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 600}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Variable {name: "width", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 652}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "Comp", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 714}) SET s.end_line = -1;

// BATCH 00013
MERGE (f:File {filepath: "/app/src/components/ui/toaster.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/toaster.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00014
MERGE (f:File {filepath: "/app/src/components/ui/menubar.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/menubar.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00015
MERGE (s:Variable {name: "MenubarMenu", filepath: "/app/src/components/ui/menubar.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Variable {name: "MenubarGroup", filepath: "/app/src/components/ui/menubar.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00017
MERGE (s:Variable {name: "MenubarPortal", filepath: "/app/src/components/ui/menubar.tsx", line_number: 11}) SET s.end_line = -1;

// BATCH 00018
MERGE (s:Variable {name: "MenubarSub", filepath: "/app/src/components/ui/menubar.tsx", line_number: 13}) SET s.end_line = -1;
