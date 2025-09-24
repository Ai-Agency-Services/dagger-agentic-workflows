// BATCH 00001
MERGE (s:Function {name: "dismiss", filepath: "/app/src/hooks/use-toast.ts", start_line: 150}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Function {name: "useToast", filepath: "/app/src/hooks/use-toast.ts", start_line: 171}) SET s.end_line = 189;

// BATCH 00003
MERGE (s:Variable {name: "index", filepath: "/app/src/hooks/use-toast.ts", line_number: 177}) SET s.end_line = -1;

// BATCH 00004
MERGE (f:File {filepath: "/app/src/components/blocks/PromoVideo.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/blocks/PromoVideo.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00005
MERGE (s:Function {name: "PromoVideo", filepath: "/app/src/components/blocks/PromoVideo.tsx", start_line: 6}) SET s.end_line = 64;

// BATCH 00006
MERGE (s:Variable {name: "videoRef", filepath: "/app/src/components/blocks/PromoVideo.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00007
MERGE (s:Variable {name: "videoId", filepath: "/app/src/components/blocks/PromoVideo.tsx", line_number: 12}) SET s.end_line = -1;

// BATCH 00008
MERGE (s:Function {name: "togglePlay", filepath: "/app/src/components/blocks/PromoVideo.tsx", start_line: 13}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Function {name: "toggleMute", filepath: "/app/src/components/blocks/PromoVideo.tsx", start_line: 25}) SET s.end_line = -1;

// BATCH 00010
MERGE (s:Variable {name: "embedUrl", filepath: "/app/src/components/blocks/PromoVideo.tsx", line_number: 39}) SET s.end_line = -1;

// BATCH 00011
MERGE (f:File {filepath: "/app/vite.config.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/vite.config.ts" ON MATCH SET f.language = "typescript";

// BATCH 00012
MERGE (f:File {filepath: "/app/vite.config.ts"}) MERGE (f)-[:EXPORTS]->(:ConfigExport {type: "configuration"});

// BATCH 00013
MERGE (f:File {filepath: "/app/src/hooks/use-mobile.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/hooks/use-mobile.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00014
MERGE (s:Variable {name: "MOBILE_BREAKPOINT", filepath: "/app/src/hooks/use-mobile.tsx", line_number: 3}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Function {name: "useIsMobile", filepath: "/app/src/hooks/use-mobile.tsx", start_line: 5}) SET s.end_line = 19;

// BATCH 00016
MERGE (s:Variable {name: "mql", filepath: "/app/src/hooks/use-mobile.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00017
MERGE (s:Function {name: "onChange", filepath: "/app/src/hooks/use-mobile.tsx", start_line: 10}) SET s.end_line = -1;

// BATCH 00018
MERGE (f:File {filepath: "/app/src/components/blocks/VideoControls.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/blocks/VideoControls.tsx" ON MATCH SET f.language = "typescript";
