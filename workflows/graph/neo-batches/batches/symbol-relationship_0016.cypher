// BATCH 00001
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "SplineScene" AND s1.filepath = "/app/src/components/ui/splite.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "Spline" AND s2.filepath = "/app/src/components/ui/splite.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00002
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "SplineScene" AND s1.filepath = "/app/src/components/ui/splite.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "SplineSceneProps" AND s2.filepath = "/app/src/components/ui/splite.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00003
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "SplineScene" AND s1.filepath = "/app/src/components/ui/splite.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "Spline" AND s2.filepath = "/app/src/components/ui/splite.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00004
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "useCarousel" AND s1.filepath = "/app/src/components/ui/carousel.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "CarouselContext" AND s2.filepath = "/app/src/components/ui/carousel.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00005
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "useCarousel" AND s1.filepath = "/app/src/components/ui/carousel.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "context" AND s2.filepath = "/app/src/components/ui/carousel.tsx"
MERGE (s1)-[:REFERENCES]->(s2);

// BATCH 00006
MATCH (s1) WHERE (s1:Function OR s1:Class OR s1:Variable OR s1:Method OR s1:Interface) 
AND s1.name = "useCarousel" AND s1.filepath = "/app/src/components/ui/carousel.tsx"
MATCH (s2) WHERE (s2:Function OR s2:Class OR s2:Variable OR s2:Method OR s2:Interface) 
AND s2.name = "context" AND s2.filepath = "/app/src/components/ui/carousel.tsx"
MERGE (s1)-[:REFERENCES]->(s2);
