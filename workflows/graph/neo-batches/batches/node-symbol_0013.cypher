// BATCH 00001
MERGE (s:Variable {name: "SelectGroup", filepath: "/app/src/components/ui/select.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00002
MERGE (s:Variable {name: "SelectValue", filepath: "/app/src/components/ui/select.tsx", line_number: 11}) SET s.end_line = -1;

// BATCH 00003
MERGE (s:Variable {name: "SelectTrigger", filepath: "/app/src/components/ui/select.tsx", line_number: 13}) SET s.end_line = -1;

// BATCH 00004
MERGE (s:Variable {name: "SelectScrollUpButton", filepath: "/app/src/components/ui/select.tsx", line_number: 33}) SET s.end_line = -1;

// BATCH 00005
MERGE (s:Variable {name: "SelectScrollDownButton", filepath: "/app/src/components/ui/select.tsx", line_number: 50}) SET s.end_line = -1;

// BATCH 00006
MERGE (f:File {filepath: "/app/src/components/ui/accordion.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/accordion.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00007
MERGE (s:Variable {name: "Accordion", filepath: "/app/src/components/ui/accordion.tsx", line_number: 7}) SET s.end_line = -1;

// BATCH 00008
MERGE (s:Variable {name: "AccordionItem", filepath: "/app/src/components/ui/accordion.tsx", line_number: 9}) SET s.end_line = -1;

// BATCH 00009
MERGE (s:Variable {name: "AccordionTrigger", filepath: "/app/src/components/ui/accordion.tsx", line_number: 21}) SET s.end_line = -1;

// BATCH 00010
MERGE (f:File {filepath: "/app/src/components/ui/input.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/input.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00011
MERGE (s:Variable {name: "Input", filepath: "/app/src/components/ui/input.tsx", line_number: 5}) SET s.end_line = -1;

// BATCH 00012
MERGE (f:File {filepath: "/app/src/components/ui/slider.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/slider.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00013
MERGE (s:Variable {name: "Slider", filepath: "/app/src/components/ui/slider.tsx", line_number: 6}) SET s.end_line = -1;

// BATCH 00014
MERGE (f:File {filepath: "/app/src/components/ui/carousel.tsx"}) ON CREATE SET f.language = "typescript", f.path = "/app/src/components/ui/carousel.tsx" ON MATCH SET f.language = "typescript";

// BATCH 00015
MERGE (s:Variable {name: "CarouselContext", filepath: "/app/src/components/ui/carousel.tsx", line_number: 31}) SET s.end_line = -1;

// BATCH 00016
MERGE (s:Function {name: "useCarousel", filepath: "/app/src/components/ui/carousel.tsx", start_line: 33}) SET s.end_line = 41;

// BATCH 00017
MERGE (s:Variable {name: "context", filepath: "/app/src/components/ui/carousel.tsx", line_number: 34}) SET s.end_line = -1;

// BATCH 00018
MERGE (s:Variable {name: "onSelect", filepath: "/app/src/components/ui/carousel.tsx", line_number: 69}) SET s.end_line = -1;
