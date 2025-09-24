// BATCH 00001
MERGE (s:Interface {name: "VideoControlsProps", filepath: "/app/src/components/blocks/VideoControls.tsx", start_line: 3}) SET s.end_line = 8;

// BATCH 00002
MERGE (s:Function {name: "VideoControls", filepath: "/app/src/components/blocks/VideoControls.tsx", start_line: 9}) SET s.end_line = 19;

// BATCH 00003
MERGE (f:File {filepath: "/app/src/components/ui/dialog.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/dialog.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00004
MERGE (s:Variable {name: "Dialog", filepath: "/app/src/components/ui/dialog.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "DialogTrigger", filepath: "/app/src/components/ui/dialog.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "DialogPortal", filepath: "/app/src/components/ui/dialog.tsx", line_number: 11}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "DialogClose", filepath: "/app/src/components/ui/dialog.tsx", line_number: 13}) SET s.end_line = -1;

// BATCH 00008
MERGE (f:File {filepath: "/app/src/components/blocks/hero.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/blocks/hero.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00009
MERGE (s:Interface {name: "HeroProps", filepath: "/app/src/components/blocks/hero.tsx", start_line: 10}) SET s.end_line = 24;

// BATCH 00010
MERGE (f:File {filepath: "/app/src/components/ui/avatar.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/avatar.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00011
MERGE (s:Variable {name: "Avatar", filepath: "/app/src/components/ui/avatar.tsx", line_number: 6}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "AvatarImage", filepath: "/app/src/components/ui/avatar.tsx", line_number: 21}) SET s.end_line = -1;

// BATCH 00013
MERGE (s:Variable {name: "AvatarFallback", filepath: "/app/src/components/ui/avatar.tsx", line_number: 33}) SET s.end_line = -1;

// BATCH 00014
MERGE (f:File {filepath: "/app/src/components/blocks/CoverAiIntroduction.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/blocks/CoverAiIntroduction.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00015
MERGE (s:Function {name: "CoverAiIntroduction", filepath: "/app/src/components/blocks/CoverAiIntroduction.tsx", start_line: 7}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Function {name: "handleGetStarted", filepath: "/app/src/components/blocks/CoverAiIntroduction.tsx", start_line: 8}) SET s.end_line = -1;

// BATCH 00017
MERGE (f:File {filepath: "/app/src/components/ui/form.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/form.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00018
MERGE (s:Variable {name: "Form", filepath: "/app/src/components/ui/form.tsx", line_number: 17}) SET s.end_line = -1;
