// BATCH 00001
MERGE (from:File {filepath: "/app/src/components/ui/pagination.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00002
MERGE (from:File {filepath: "/app/src/components/ui/splite.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00003
MERGE (from:File {filepath: "/app/src/pages/TermsOfService.tsx"}) MERGE (to:File {filepath: "@/components/ui/footer-section"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00004
MERGE (from:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (to:File {filepath: "@/hooks/use-mobile"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00005
MERGE (from:File {filepath: "/app/src/components/ui/sidebar.tsx"}) MERGE (to:File {filepath: "@/components/ui/skeleton"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00006
MERGE (from:File {filepath: "/app/src/integrations/supabase/client.ts"}) MERGE (to:File {filepath: "/app/src/integrations/supabase/types.js"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00007
MERGE (from:File {filepath: "/app/src/components/ui/command.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-dialog"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00008
MERGE (from:File {filepath: "/app/src/pages/contact/ContactForm.tsx"}) MERGE (to:File {filepath: "@/components/ui/textarea"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00009
MERGE (from:File {filepath: "/app/src/components/ui/menubar.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-menubar"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00010
MERGE (from:File {filepath: "/app/src/pages/TermsOfService.tsx"}) MERGE (to:File {filepath: "react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00011
MERGE (from:File {filepath: "/app/src/components/ui/sheet.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00012
MERGE (from:File {filepath: "/app/src/components/ui/menubar.tsx"}) MERGE (to:File {filepath: "@/lib/utils"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00013
MERGE (from:File {filepath: "/app/src/components/ui/breadcrumb.tsx"}) MERGE (to:File {filepath: "lucide-react"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00014
MERGE (from:File {filepath: "/app/src/components/ui/use-toast.ts"}) MERGE (to:File {filepath: "@/hooks/use-toast"}) MERGE (from)-[:IMPORTS]->(to);

// BATCH 00015
MERGE (from:File {filepath: "/app/src/components/ui/popover.tsx"}) MERGE (to:File {filepath: "@radix-ui/react-popover"}) MERGE (from)-[:IMPORTS]->(to);
