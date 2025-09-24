// BATCH 00001
MERGE (s:Variable {name: "FormFieldContext", filepath: "/app/src/components/ui/form.tsx", line_number: 27}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "FormField", filepath: "/app/src/components/ui/form.tsx", line_number: 29}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "FormItemContext", filepath: "/app/src/components/ui/form.tsx", line_number: 47}) SET s.end_line = -1;

// BATCH 00004
MERGE (s:Function {name: "useFormField", filepath: "/app/src/components/ui/form.tsx", start_line: 49}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "fieldContext", filepath: "/app/src/components/ui/form.tsx", line_number: 58}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "itemContext", filepath: "/app/src/components/ui/form.tsx", line_number: 59}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "fieldState", filepath: "/app/src/components/ui/form.tsx", line_number: 69}) SET s.end_line = -1;

// BATCH 00008
MERGE (s:Variable {name: "id", filepath: "/app/src/components/ui/form.tsx", line_number: 85}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Variable {name: "body", filepath: "/app/src/components/ui/form.tsx", line_number: 156}) SET s.end_line = -1;

// BATCH 00010
MERGE (f:File {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/tubelight-navbar.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00011
MERGE (s:Interface {name: "NavItem", filepath: "/app/src/components/ui/tubelight-navbar.tsx", start_line: 7}) SET s.end_line = 11;

// BATCH 00012
MERGE (s:Interface {name: "NavBarProps", filepath: "/app/src/components/ui/tubelight-navbar.tsx", start_line: 13}) SET s.end_line = 16;

// BATCH 00013
MERGE (s:Function {name: "handleResize", filepath: "/app/src/components/ui/tubelight-navbar.tsx", start_line: 23}) SET s.end_line = -1;

// BATCH 00014
MERGE (s:Variable {name: "Icon", filepath: "/app/src/components/ui/tubelight-navbar.tsx", line_number: 41}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Variable {name: "isActive", filepath: "/app/src/components/ui/tubelight-navbar.tsx", line_number: 42}) SET s.end_line = -1;

// BATCH 00016
MERGE (f:File {filepath: "/app/src/components/ui/toast.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/toast.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00017
MERGE (s:Variable {name: "ToastProvider", filepath: "/app/src/components/ui/toast.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00018
MERGE (f:File {filepath: "/app/src/components/ui/sheet.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/sheet.tsx" ON MATCH SET f.language = "typescript";
