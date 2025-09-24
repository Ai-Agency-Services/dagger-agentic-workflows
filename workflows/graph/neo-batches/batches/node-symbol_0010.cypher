// BATCH 00001
MERGE (s:Variable {name: "MenubarRadioGroup", filepath: "/app/src/components/ui/menubar.tsx", line_number: 15}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "Menubar", filepath: "/app/src/components/ui/menubar.tsx", line_number: 17}) SET s.end_line = -1;

// BATCH 00003
MERGE (f:File {filepath: "/app/src/components/ui/switch.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/switch.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00004
MERGE (f:File {filepath: "/app/src/components/ui/popover.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/popover.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00005
MERGE (s:Variable {name: "Popover", filepath: "/app/src/components/ui/popover.tsx", line_number: 6}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "PopoverTrigger", filepath: "/app/src/components/ui/popover.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00007
MERGE (f:File {filepath: "/app/src/components/ui/button.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/button.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00008
MERGE (s:Variable {name: "buttonVariants", filepath: "/app/src/components/ui/button.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Interface {name: "ButtonProps", filepath: "/app/src/components/ui/button.tsx", start_line: 36}) SET s.end_line = 40;

// BATCH 00010
MERGE (s:Variable {name: "Button", filepath: "/app/src/components/ui/button.tsx", line_number: 42}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Variable {name: "Comp", filepath: "/app/src/components/ui/button.tsx", line_number: 44}) SET s.end_line = -1;

// BATCH 00012
MERGE (f:File {filepath: "/app/src/components/ui/textarea.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/textarea.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00013
MERGE (s:Interface {name: "TextareaProps", filepath: "/app/src/components/ui/textarea.tsx", start_line: 5}) SET s.end_line = 6;

// BATCH 00014
MERGE (s:Variable {name: "Textarea", filepath: "/app/src/components/ui/textarea.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00015
MERGE (f:File {filepath: "/app/src/components/ui/label.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/label.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00016
MERGE (s:Variable {name: "labelVariants", filepath: "/app/src/components/ui/label.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00017
MERGE (f:File {filepath: "/app/src/components/ui/use-toast.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/use-toast.ts" ON MATCH SET f.language = "typescript";

// BATCH 00018
MERGE (f:File {filepath: "/app/src/components/ui/context-menu.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/context-menu.tsx" ON MATCH SET f.language = "typescript";
