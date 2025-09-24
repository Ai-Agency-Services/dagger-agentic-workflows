// BATCH 00001
MERGE (s:Variable {name: "Sheet", filepath: "/app/src/components/ui/sheet.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "SheetTrigger", filepath: "/app/src/components/ui/sheet.tsx", line_number: 10}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "SheetClose", filepath: "/app/src/components/ui/sheet.tsx", line_number: 12}) SET s.end_line = -1;

// BATCH 00004
MERGE (s:Variable {name: "SheetPortal", filepath: "/app/src/components/ui/sheet.tsx", line_number: 14}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "childArray", filepath: "/app/src/components/ui/sheet.tsx", line_number: 58}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "hasSheetTitle", filepath: "/app/src/components/ui/sheet.tsx", line_number: 61}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "hasSheetDescription", filepath: "/app/src/components/ui/sheet.tsx", line_number: 80}) SET s.end_line = -1;

// BATCH 00008
MERGE (f:File {filepath: "/app/src/components/ui/skeleton.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/skeleton.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00009
MERGE (s:Function {name: "Skeleton", filepath: "/app/src/components/ui/skeleton.tsx", start_line: 3}) SET s.end_line = 13;

// BATCH 00010
MERGE (f:File {filepath: "/app/src/components/ui/dropdown-menu.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/dropdown-menu.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00011
MERGE (s:Variable {name: "DropdownMenu", filepath: "/app/src/components/ui/dropdown-menu.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "DropdownMenuTrigger", filepath: "/app/src/components/ui/dropdown-menu.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00013
MERGE (s:Variable {name: "DropdownMenuGroup", filepath: "/app/src/components/ui/dropdown-menu.tsx", line_number: 11}) SET s.end_line = -1;

// BATCH 00014
MERGE (s:Variable {name: "DropdownMenuPortal", filepath: "/app/src/components/ui/dropdown-menu.tsx", line_number: 13}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Variable {name: "DropdownMenuSub", filepath: "/app/src/components/ui/dropdown-menu.tsx", line_number: 15}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Variable {name: "DropdownMenuRadioGroup", filepath: "/app/src/components/ui/dropdown-menu.tsx", line_number: 17}) SET s.end_line = -1;

// BATCH 00017
MERGE (s:Variable {name: "DropdownMenuSubTrigger", filepath: "/app/src/components/ui/dropdown-menu.tsx", line_number: 19}) SET s.end_line = -1;

// BATCH 00018
MERGE (f:File {filepath: "/app/src/components/ui/spotlight.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/spotlight.tsx" ON MATCH SET f.language = "typescript";
