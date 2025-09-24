// BATCH 00001
MERGE (from:File {filepath: "/app/src/components/ui/calendar.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00002
MERGE (from:File {filepath: "/app/src/components/ui/context-menu.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00003
MERGE (from:File {filepath: "/app/src/components/ui/dropdown-menu.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00004
MERGE (from:File {filepath: "/app/src/components/Navigation.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00005
MERGE (from:File {filepath: "/app/src/components/ui/sonner.tsx"}) MERGE (to:File {filepath: "next-themes"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00006
MERGE (from:File {filepath: "/app/src/components/ui/button.tsx"}) MERGE (to:File {filepath: "class-variance-authority"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00007
MERGE (from:File {filepath: "/app/src/components/ui/resizable.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00008
MERGE (from:File {filepath: "/app/src/lib/utils.ts"}) MERGE (to:File {filepath: "clsx"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00009
MERGE (from:File {filepath: "/app/src/components/ui/progress.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-progress"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00010
MERGE (from:File {filepath: "/app/eslint.config.js"}) MERGE (to:File {filepath: "globals"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00011
MERGE (from:File {filepath: "/app/src/components/ui/radio-group.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00012
MERGE (from:File {filepath: "/app/src/components/ui/toast.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00013
MERGE (from:File {filepath: "/app/eslint.config.js"}) MERGE (to:File {filepath: "typescript-eslint"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00014
MERGE (from:File {filepath: "/app/src/components/ui/chart.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00015
MERGE (from:File {filepath: "/app/src/components/ui/skeleton.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);
