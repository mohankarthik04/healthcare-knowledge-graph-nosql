// View the graph
MATCH (n)-[r]->(m) RETURN n, r, m;

// Diseases linked to patients
MATCH (p:Patient)-[:DIAGNOSED_WITH]->(d:Disease)
RETURN p.name, d.name;

// Illustrative medicine associations
MATCH (d:Disease)-[:TREATED_WITH]->(m:Medicine)
RETURN d.name, m.name;

// Explore one patient's connected information
MATCH (p:Patient {id:'P001'})
OPTIONAL MATCH (p)-[:CONSULTED]->(doc:Doctor)
OPTIONAL MATCH (p)-[:DIAGNOSED_WITH]->(d:Disease)
OPTIONAL MATCH (d)-[:TREATED_WITH]->(m:Medicine)
RETURN p, doc, d, m;
