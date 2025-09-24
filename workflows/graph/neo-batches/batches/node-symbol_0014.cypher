// BATCH 00001
MERGE (s:Variable {name: "scrollPrev", filepath: "/app/src/components/ui/carousel.tsx", line_number: 78}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "scrollNext", filepath: "/app/src/components/ui/carousel.tsx", line_number: 82}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "handleKeyDown", filepath: "/app/src/components/ui/carousel.tsx", line_number: 86}) SET s.end_line = -1;

// BATCH 00004
MERGE (f:File {filepath: "/app/src/components/ui/navigation-menu.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/navigation-menu.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00005
MERGE (s:Variable {name: "NavigationMenu", filepath: "/app/src/components/ui/navigation-menu.tsx", line_number: 8}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Variable {name: "NavigationMenuList", filepath: "/app/src/components/ui/navigation-menu.tsx", line_number: 26}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "NavigationMenuItem", filepath: "/app/src/components/ui/navigation-menu.tsx", line_number: 41}) SET s.end_line = -1;

// BATCH 00008
MERGE (s:Variable {name: "navigationMenuTriggerStyle", filepath: "/app/src/components/ui/navigation-menu.tsx", line_number: 43}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Variable {name: "NavigationMenuTrigger", filepath: "/app/src/components/ui/navigation-menu.tsx", line_number: 47}) SET s.end_line = -1;

// BATCH 00010
MERGE (f:File {filepath: "/app/src/components/ui/chart.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/chart.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00011
MERGE (s:Variable {name: "THEMES", filepath: "/app/src/components/ui/chart.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "ChartContext", filepath: "/app/src/components/ui/chart.tsx", line_number: 23}) SET s.end_line = -1;

// BATCH 00013
MERGE (s:Function {name: "useChart", filepath: "/app/src/components/ui/chart.tsx", start_line: 25}) SET s.end_line = 33;

// BATCH 00014
MERGE (s:Variable {name: "context", filepath: "/app/src/components/ui/chart.tsx", line_number: 26}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Variable {name: "uniqueId", filepath: "/app/src/components/ui/chart.tsx", line_number: 44}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Variable {name: "chartId", filepath: "/app/src/components/ui/chart.tsx", line_number: 45}) SET s.end_line = -1;

// BATCH 00017
MERGE (s:Variable {name: "colorConfig", filepath: "/app/src/components/ui/chart.tsx", line_number: 69}) SET s.end_line = -1;

// BATCH 00018
MERGE (s:Variable {name: "color", filepath: "/app/src/components/ui/chart.tsx", line_number: 86}) SET s.end_line = -1;
