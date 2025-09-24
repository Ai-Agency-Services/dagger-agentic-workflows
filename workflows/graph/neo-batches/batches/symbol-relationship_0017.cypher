// BATCH 00001
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "useChart" AND s1.filepath = "/app/src/components/ui/chart.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "ChartContext" AND s2.filepath = "/app/src/components/ui/chart.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00002
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "useChart" AND s1.filepath = "/app/src/components/ui/chart.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "context" AND s2.filepath = "/app/src/components/ui/chart.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00003
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "useChart" AND s1.filepath = "/app/src/components/ui/chart.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "context" AND s2.filepath = "/app/src/components/ui/chart.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00004
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "Footerdemo" AND s1.filepath = "/app/src/components/ui/footer-section.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "handleNewsletterSignup" AND s2.filepath = "/app/src/components/ui/footer-section.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00005
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "verifyCaptcha" AND s1.filepath = "/app/supabase/functions/send-contact-email/index.ts"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "recaptchaSecret" AND s2.filepath = "/app/supabase/functions/send-contact-email/index.ts"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00006
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "verifyCaptcha" AND s1.filepath = "/app/supabase/functions/send-contact-email/index.ts"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "recaptchaSecret" AND s2.filepath = "/app/supabase/functions/send-contact-email/index.ts"
MERGE (s1)-[:REFERENCES]->(s2);
