// BATCH 00001
MERGE (from:File {filepath: "/app/src/components/ui/select.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-select"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00002
MERGE (from:File {filepath: "/app/src/components/ui/toggle-group.tsx"}) MERGE (to:File {filepath: "class-variance-authority"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00003
MERGE (from:File {filepath: "/app/src/components/ui/scroll-area.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00004
MERGE (from:File {filepath: "/app/src/App.tsx"}) MERGE (to:File {filepath: "@/components/ui/sonner"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00005
MERGE (from:File {filepath: "/app/src/components/blocks/PromoVideo.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00006
MERGE (from:File {filepath: "/app/src/App.tsx"}) MERGE (to:File {filepath: "/app/src/pages/TermsOfService.js"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00007
MERGE (from:File {filepath: "/app/src/components/ui/sonner.tsx"}) MERGE (to:File {filepath: "sonner"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00008
MERGE (from:File {filepath: "/app/src/components/ui/form.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-label"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00009
MERGE (from:File {filepath: "/app/vite.config.ts"}) MERGE (to:File {filepath: "vite"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00010
MERGE (from:File {filepath: "/app/src/components/ui/sheet.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-dialog"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00011
MERGE (from:File {filepath: "/app/src/components/ui/calendar.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00012
MERGE (from:File {filepath: "/app/src/components/blocks/hero.tsx"}) MERGE (to:File {filepath: "@/components/ui/button"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00013
MERGE (from:File {filepath: "/app/src/components/ui/footer-section.tsx"}) MERGE (to:File {filepath: "@/integrations/supabase/client"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00014
MERGE (from:File {filepath: "/app/src/integrations/supabase/client.ts"}) MERGE (to:File {filepath: "@supabase/supabase-js"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00015
MERGE (from:File {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MERGE (to:File {filepath: "@/components/ui/input"}) MERGE (from)-[:IMPORTS]->(to);
