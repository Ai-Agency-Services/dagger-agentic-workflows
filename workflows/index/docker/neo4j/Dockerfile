FROM neo4j:5.12

# Set environment variables
ENV NEO4J_AUTH=neo4j/password
ENV NEO4J_dbms_memory_pagecache_size=1G
ENV NEO4J_dbms_memory_heap_initial__size=1G
ENV NEO4J_dbms_memory_heap_max__size=1G

# Expose ports
EXPOSE 7474 7687

# Add plugins
# Add APOC plugin
RUN wget -P /plugins/ https://github.com/neo4j/apoc/releases/download/5.12.0/apoc-5.12.0-core.jar

# Enable plugins
RUN echo 'dbms.security.procedures.unrestricted=apoc.*' >> /conf/neo4j.conf
RUN echo 'dbms.security.procedures.allowlist=apoc.*' >> /conf/neo4j.conf

# Add initialization script
COPY init.cypher /docker-entrypoint-initdb.d/