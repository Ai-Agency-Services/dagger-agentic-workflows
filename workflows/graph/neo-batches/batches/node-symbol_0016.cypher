// BATCH 00001
MERGE (s:Variable {name: "hasAlertDialogDescription", filepath: "/app/src/components/ui/alert-dialog.tsx", line_number: 57}) SET s.end_line = -1;

// BATCH 00002
MERGE (f:File {filepath: "/app/src/components/ui/footer-section.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/footer-section.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00003
MERGE (s:Function {name: "Footerdemo", filepath: "/app/src/components/ui/footer-section.tsx", start_line: 17}) SET s.end_line = 174;

// BATCH 00004
MERGE (s:Function {name: "handleNewsletterSignup", filepath: "/app/src/components/ui/footer-section.tsx", start_line: 21}) SET s.end_line = -1;

// BATCH 00005
MERGE (f:File {filepath: "/app/src/components/ui/input-otp.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/input-otp.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00006
MERGE (s:Variable {name: "inputOTPContext", filepath: "/app/src/components/ui/input-otp.tsx", line_number: 35}) SET s.end_line = -1;

// BATCH 00007
MERGE (f:File {filepath: "/app/src/components/ui/collapsible.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/collapsible.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00008
MERGE (s:Variable {name: "Collapsible", filepath: "/app/src/components/ui/collapsible.tsx", line_number: 3}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Variable {name: "CollapsibleTrigger", filepath: "/app/src/components/ui/collapsible.tsx", line_number: 5}) SET s.end_line = -1;

// BATCH 00010
MERGE (s:Variable {name: "CollapsibleContent", filepath: "/app/src/components/ui/collapsible.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00011
MERGE (f:File {filepath: "/app/src/components/ui/toggle.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/toggle.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00012
MERGE (s:Variable {name: "toggleVariants", filepath: "/app/src/components/ui/toggle.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00013
MERGE (f:File {filepath: "/app/src/components/ui/hover-card.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/hover-card.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00014
MERGE (s:Variable {name: "HoverCard", filepath: "/app/src/components/ui/hover-card.tsx", line_number: 6}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Variable {name: "HoverCardTrigger", filepath: "/app/src/components/ui/hover-card.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00016
MERGE (f:File {filepath: "/app/src/components/ui/command.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/command.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00017
MERGE (f:File {filepath: "/app/src/components/Navigation.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/Navigation.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00018
MERGE (s:Function {name: "Navigation", filepath: "/app/src/components/Navigation.tsx", start_line: 7}) SET s.end_line = -1;
