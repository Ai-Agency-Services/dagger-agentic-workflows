// BATCH 00001
MERGE (s:Variable {name: "Icon", filepath: "/app/src/components/ui/anime-navbar.tsx", line_number: 53}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "isActive", filepath: "/app/src/components/ui/anime-navbar.tsx", line_number: 54}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "isHovered", filepath: "/app/src/components/ui/anime-navbar.tsx", line_number: 55}) SET s.end_line = -1;

// BATCH 00004
MERGE (f:File {filepath: "/app/src/components/ui/calendar.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/calendar.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00005
MERGE (s:Function {name: "Calendar", filepath: "/app/src/components/ui/calendar.tsx", start_line: 10}) SET s.end_line = 61;

// BATCH 00006
MERGE (f:File {filepath: "/app/src/components/ui/resizable.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/resizable.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00007
MERGE (f:File {filepath: "/app/src/components/ui/sidebar.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/sidebar.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00008
MERGE (s:Variable {name: "SIDEBAR_COOKIE_NAME", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 20}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Variable {name: "SIDEBAR_COOKIE_MAX_AGE", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 21}) SET s.end_line = -1;

// BATCH 00010
MERGE (s:Variable {name: "SIDEBAR_WIDTH", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 22}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Variable {name: "SIDEBAR_WIDTH_MOBILE", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 23}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "SIDEBAR_WIDTH_ICON", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 24}) SET s.end_line = -1;

// BATCH 00013
MERGE (s:Variable {name: "SIDEBAR_KEYBOARD_SHORTCUT", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 25}) SET s.end_line = -1;

// BATCH 00014
MERGE (s:Variable {name: "SidebarContext", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 37}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Function {name: "useSidebar", filepath: "/app/src/components/ui/sidebar.tsx", start_line: 39}) SET s.end_line = 46;

// BATCH 00016
MERGE (s:Variable {name: "context", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 40}) SET s.end_line = -1;

// BATCH 00017
MERGE (s:Variable {name: "isMobile", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 68}) SET s.end_line = -1;

// BATCH 00018
MERGE (s:Variable {name: "open", filepath: "/app/src/components/ui/sidebar.tsx", line_number: 74}) SET s.end_line = -1;
