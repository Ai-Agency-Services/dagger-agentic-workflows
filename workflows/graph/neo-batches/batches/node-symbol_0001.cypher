// BATCH 00001
MERGE (f:File {filepath: "/app/src/hooks/use-toast.ts"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/hooks/use-toast.ts" ON MATCH SET f.language = "typescript";

// BATCH 00002
MERGE (s:Variable {name: "TOAST_LIMIT", filepath: "/app/src/hooks/use-toast.ts", line_number: 8}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "TOAST_REMOVE_DELAY", filepath: "/app/src/hooks/use-toast.ts", line_number: 9}) SET s.end_line = -1;

// BATCH 00004
MERGE (s:Variable {name: "actionTypes", filepath: "/app/src/hooks/use-toast.ts", line_number: 18}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "count", filepath: "/app/src/hooks/use-toast.ts", line_number: 25}) SET s.end_line = -1;

// BATCH 00006
MERGE (s:Function {name: "genId", filepath: "/app/src/hooks/use-toast.ts", start_line: 27}) SET s.end_line = 30;

// BATCH 00007
MERGE (s:Interface {name: "State", filepath: "/app/src/hooks/use-toast.ts", start_line: 52}) SET s.end_line = 54;

// BATCH 00008
MERGE (s:Variable {name: "toastTimeouts", filepath: "/app/src/hooks/use-toast.ts", line_number: 56}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Function {name: "addToRemoveQueue", filepath: "/app/src/hooks/use-toast.ts", start_line: 58}) SET s.end_line = -1;

// BATCH 00010
MERGE (s:Variable {name: "timeout", filepath: "/app/src/hooks/use-toast.ts", line_number: 63}) SET s.end_line = -1;

// BATCH 00011
MERGE (s:Function {name: "reducer", filepath: "/app/src/hooks/use-toast.ts", start_line: 74}) SET s.end_line = -1;

// BATCH 00012
MERGE (s:Variable {name: "action", filepath: "/app/src/hooks/use-toast.ts", line_number: 91}) SET s.end_line = -1;

// BATCH 00013
MERGE (s:Variable {name: "listeners", filepath: "/app/src/hooks/use-toast.ts", line_number: 129}) SET s.end_line = -1;

// BATCH 00014
MERGE (s:Variable {name: "memoryState", filepath: "/app/src/hooks/use-toast.ts", line_number: 131}) SET s.end_line = -1;

// BATCH 00015
MERGE (s:Function {name: "dispatch", filepath: "/app/src/hooks/use-toast.ts", start_line: 133}) SET s.end_line = 138;

// BATCH 00016
MERGE (s:Function {name: "toast", filepath: "/app/src/hooks/use-toast.ts", start_line: 142}) SET s.end_line = 169;

// BATCH 00017
MERGE (s:Variable {name: "id", filepath: "/app/src/hooks/use-toast.ts", line_number: 143}) SET s.end_line = -1;

// BATCH 00018
MERGE (s:Function {name: "update", filepath: "/app/src/hooks/use-toast.ts", start_line: 145}) SET s.end_line = -1;
