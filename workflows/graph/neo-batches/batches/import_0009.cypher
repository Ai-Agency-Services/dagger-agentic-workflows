// BATCH 00001
MERGE (from:File {filepath: "/app/src/components/blocks/hero.tsx"}) MERGE (to:File {filepath: "framer-motion"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00002
MERGE (from:File {filepath: "/app/src/components/ui/dropdown-menu.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-dropdown-menu"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00003
MERGE (from:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00004
MERGE (from:File {filepath: "/app/src/components/ui/hover-card.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-hover-card"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00005
MERGE (from:File {filepath: "/app/vite.config.ts"}) MERGE (to:File {filepath: "@vitejs/plugin-react-swc"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00006
MERGE (from:File {filepath: "/app/src/components/ui/spotlight.tsx"}) MERGE (to:File {filepath: "framer-motion"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00007
MERGE (from:File {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MERGE (to:File {filepath: "react-router-dom"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00008
MERGE (from:File {filepath: "/app/src/components/ui/badge.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00009
MERGE (from:File {filepath: "/app/src/components/ui/textarea.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00010
MERGE (from:File {filepath: "/app/src/components/ui/anime-navbar.tsx"}) MERGE (to:File {filepath: "react-router-dom"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00011
MERGE (from:File {filepath: "/app/src/components/ui/tabs.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00012
MERGE (from:File {filepath: "/app/src/components/ui/slider.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-slider"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00013
MERGE (from:File {filepath: "/app/src/components/ui/input-otp.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00014
MERGE (from:File {filepath: "/app/src/components/ui/command.tsx"}) MERGE (to:File {filepath: "@/components/ui/dialog"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00015
MERGE (from:File {filepath: "/app/src/pages/AboutUs.tsx"}) MERGE (to:File {filepath: "react-router-dom"}) MERGE (from)-[:IMPORTS]->(to);
