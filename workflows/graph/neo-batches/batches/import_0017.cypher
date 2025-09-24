// BATCH 00001
MERGE (from:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (to:File {filepath: "@/components/ui/input"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00002
MERGE (from:File {filepath: "/app/supabase/functions/send-contact-email/index.ts"}) MERGE (to:File {filepath: "npm:@sendgrid/mail"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00003
MERGE (from:File {filepath: "/app/src/components/ui/command.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00004
MERGE (from:File {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MERGE (to:File {filepath: "sonner"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00005
MERGE (from:File {filepath: "/app/src/pages/contact/ContactHero.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00006
MERGE (from:File {filepath: "/app/src/components/ui/dropdown-menu.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00007
MERGE (from:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (to:File {filepath: "@/components/ui/button"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00008
MERGE (from:File {filepath: "/app/src/components/ui/avatar.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-avatar"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00009
MERGE (from:File {filepath: "/app/src/components/ui/toggle.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00010
MERGE (from:File {filepath: "/app/src/main.tsx"}) MERGE (to:File {filepath: "react-dom/client"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00011
MERGE (from:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00012
MERGE (from:File {filepath: "/app/src/components/ui/alert-dialog.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-alert-dialog"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00013
MERGE (from:File {filepath: "/app/src/pages/Index.tsx"}) MERGE (to:File {filepath: "react-router-dom"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00014
MERGE (from:File {filepath: "/app/src/App.tsx"}) MERGE (to:File {filepath: "/app/src/pages/Contact.js"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00015
MERGE (from:File {filepath: "/app/src/components/blocks/CoverAiIntroduction.tsx"}) MERGE (to:File {filepath: "@/components/ui/button"}) MERGE (from)-[:IMPORTS]->(to);
