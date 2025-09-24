// BATCH 00001
MERGE (from:File {filepath: "/app/src/components/ui/separator.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-separator"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00002
MERGE (from:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (to:File {filepath: "@/components/ui/separator"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00003
MERGE (from:File {filepath: "/app/src/components/ui/spotlight.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00004
MERGE (from:File {filepath: "/app/src/pages/AgentTask.tsx"}) MERGE (to:File {filepath: "@/components/ui/button"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00005
MERGE (from:File {filepath: "/app/src/components/ui/chart.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00006
MERGE (from:File {filepath: "/app/src/components/ui/drawer.tsx"}) MERGE (to:File {filepath: "vaul"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00007
MERGE (from:File {filepath: "/app/src/components/ui/table.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00008
MERGE (from:File {filepath: "/app/src/components/ui/tooltip.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-tooltip"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00009
MERGE (from:File {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00010
MERGE (from:File {filepath: "/app/src/components/ui/tooltip.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00011
MERGE (from:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (to:File {filepath: "class-variance-authority"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00012
MERGE (from:File {filepath: "/app/src/components/blocks/CoverAiIntroduction.tsx"}) MERGE (to:File {filepath: "@/components/ui/card"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00013
MERGE (from:File {filepath: "/app/src/components/ui/switch.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00014
MERGE (from:File {filepath: "/app/src/lib/utils.ts"}) MERGE (to:File {filepath: "tailwind-merge"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00015
MERGE (from:File {filepath: "/app/src/components/ui/footer-section.tsx"}) MERGE (to:File {filepath: "@/components/ui/button"}) MERGE (from)-[:IMPORTS]->(to);
