// BATCH 00001
MERGE (from:File {filepath: "/app/src/main.tsx"}) MERGE (to:File {filepath: "/app/src/App.js"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00002
MERGE (from:File {filepath: "/app/src/components/ui/toggle-group.tsx"}) MERGE (to:File {filepath: "@/components/ui/toggle"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00003
MERGE (from:File {filepath: "/app/src/pages/AboutUs.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00004
MERGE (from:File {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00005
MERGE (from:File {filepath: "/app/src/components/ui/tubelight-navbar.tsx"}) MERGE (to:File {filepath: "framer-motion"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00006
MERGE (from:File {filepath: "/app/src/components/ui/pagination.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00007
MERGE (from:File {filepath: "/app/src/components/ui/anime-navbar.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00008
MERGE (from:File {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MERGE (to:File {filepath: "/app/src/pages/contact/types.js"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00009
MERGE (from:File {filepath: "/app/src/components/Navigation.tsx"}) MERGE (to:File {filepath: "@/components/ui/anime-navbar"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00010
MERGE (from:File {filepath: "/app/src/components/ui/accordion.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-accordion"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00011
MERGE (from:File {filepath: "/app/src/pages/Contact.tsx"}) MERGE (to:File {filepath: "@/components/ui/footer-section"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00012
MERGE (from:File {filepath: "/app/src/components/ui/navigation-menu.tsx"}) MERGE (to:File {filepath: "class-variance-authority"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00013
MERGE (from:File {filepath: "/app/src/components/ui/alert-dialog.tsx"}) MERGE (to:File {filepath: "@/components/ui/button"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00014
MERGE (from:File {filepath: "/app/src/components/ui/navigation-menu.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00015
MERGE (from:File {filepath: "/app/src/components/ui/radio-group.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-radio-group"}) MERGE (from)-[:IMPORTS]->(to);
