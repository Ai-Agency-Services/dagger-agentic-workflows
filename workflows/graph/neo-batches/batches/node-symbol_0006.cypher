// BATCH 00001
MERGE (s:Function {name: "Spotlight", filepath: "/app/src/components/ui/spotlight.tsx", start_line: 13}) SET s.end_line = 82;

// BATCH 00002
MERGE (s:Variable {name: "containerRef", filepath: "/app/src/components/ui/spotlight.tsx", line_number: 19}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "mouseX", filepath: "/app/src/components/ui/spotlight.tsx", line_number: 23}) SET s.end_line = -1;

// BATCH 00004
MERGE (s:Variable {name: "mouseY", filepath: "/app/src/components/ui/spotlight.tsx", line_number: 24}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "spotlightLeft", filepath: "/app/src/components/ui/spotlight.tsx", line_number: 26}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "spotlightTop", filepath: "/app/src/components/ui/spotlight.tsx", line_number: 27}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "parent", filepath: "/app/src/components/ui/spotlight.tsx", line_number: 31}) SET s.end_line = -1;

// BATCH 00008
MERGE (s:Variable {name: "handleMouseMove", filepath: "/app/src/components/ui/spotlight.tsx", line_number: 40}) SET s.end_line = -1;

// BATCH 00009
MERGE (f:File {filepath: "/app/src/components/ui/badge.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/badge.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00010
MERGE (s:Variable {name: "badgeVariants", filepath: "/app/src/components/ui/badge.tsx", line_number: 6}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Interface {name: "BadgeProps", filepath: "/app/src/components/ui/badge.tsx", start_line: 26}) SET s.end_line = 28;

// BATCH 00012
MERGE (s:Function {name: "Badge", filepath: "/app/src/components/ui/badge.tsx", start_line: 30}) SET s.end_line = 34;

// BATCH 00013
MERGE (f:File {filepath: "/app/src/components/ui/tooltip.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/tooltip.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00014
MERGE (s:Variable {name: "TooltipProvider", filepath: "/app/src/components/ui/tooltip.tsx", line_number: 6}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Variable {name: "Tooltip", filepath: "/app/src/components/ui/tooltip.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Variable {name: "TooltipTrigger", filepath: "/app/src/components/ui/tooltip.tsx", line_number: 10}) SET s.end_line = -1;

// BATCH 00017
MERGE (f:File {filepath: "/app/src/components/ui/radio-group.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/radio-group.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00018
MERGE (s:Variable {name: "RadioGroup", filepath: "/app/src/components/ui/radio-group.tsx", line_number: 7}) SET s.end_line = -1;
