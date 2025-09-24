// BATCH 00001
MERGE (s:Variable {name: "ContextMenu", filepath: "/app/src/components/ui/context-menu.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "ContextMenuTrigger", filepath: "/app/src/components/ui/context-menu.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "ContextMenuGroup", filepath: "/app/src/components/ui/context-menu.tsx", line_number: 11}) SET s.end_line = -1;

// BATCH 00004
MERGE (s:Variable {name: "ContextMenuPortal", filepath: "/app/src/components/ui/context-menu.tsx", line_number: 13}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "ContextMenuSub", filepath: "/app/src/components/ui/context-menu.tsx", line_number: 15}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "ContextMenuRadioGroup", filepath: "/app/src/components/ui/context-menu.tsx", line_number: 17}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "ContextMenuSubTrigger", filepath: "/app/src/components/ui/context-menu.tsx", line_number: 19}) SET s.end_line = -1;

// BATCH 00008
MERGE (f:File {filepath: "/app/src/components/ui/separator.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/separator.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00009
MERGE (f:File {filepath: "/app/src/components/ui/checkbox.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/checkbox.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00010
MERGE (f:File {filepath: "/app/src/components/ui/card.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/card.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00011
MERGE (s:Variable {name: "Card", filepath: "/app/src/components/ui/card.tsx", line_number: 5}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "CardHeader", filepath: "/app/src/components/ui/card.tsx", line_number: 20}) SET s.end_line = -1;

// BATCH 00013
MERGE (s:Variable {name: "CardTitle", filepath: "/app/src/components/ui/card.tsx", line_number: 32}) SET s.end_line = -1;

// BATCH 00014
MERGE (s:Variable {name: "CardDescription", filepath: "/app/src/components/ui/card.tsx", line_number: 47}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Variable {name: "CardContent", filepath: "/app/src/components/ui/card.tsx", line_number: 59}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Variable {name: "CardFooter", filepath: "/app/src/components/ui/card.tsx", line_number: 67}) SET s.end_line = -1;

// BATCH 00017
MERGE (f:File {filepath: "/app/src/components/ui/tabs.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/tabs.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00018
MERGE (s:Variable {name: "Tabs", filepath: "/app/src/components/ui/tabs.tsx", line_number: 6}) SET s.end_line = -1;
