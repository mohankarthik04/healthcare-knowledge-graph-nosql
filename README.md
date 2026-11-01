# Healthcare Knowledge Graph using NoSQL

A small educational project using **Neo4j**, **Cypher**, **Python** and **Streamlit** to represent healthcare entities and their relationships as a knowledge graph.

## Features
- Patient, Doctor, Disease and Medicine nodes.
- `CONSULTED`, `DIAGNOSED_WITH` and `TREATED_WITH` relationships.
- Patient search and connected healthcare information.
- Interactive graph visualization.
- Add a fictional patient and optionally connect a doctor.
- One-click loading of sample records.

## Architecture
Browser → Streamlit UI → Neo4j Python Driver → Neo4j Graph Database

## Requirements
- Python 3.10+
- Docker Desktop with Docker Compose

## Run locally

1. Clone or download this repository.
2. Start Neo4j in the project directory:

   ```bash
   docker compose up -d
   ```

3. Create and activate a virtual environment:

   **Windows**
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:

   ```bash
   streamlit run app.py
   ```

6. Open `http://localhost:8501` and click **Load demo records** in the sidebar.

Neo4j Browser: `http://localhost:7474`  
Username: `neo4j`  
Password: `healthgraph123`

Change the demo password before using this beyond a local classroom demonstration. Do not expose the database publicly.

## Graph model

| Node | Properties |
|---|---|
| Patient | id, name, age, gender |
| Doctor | id, name, specialty |
| Disease | name |
| Medicine | name |

| Relationship | Meaning |
|---|---|
| Patient → Doctor (`CONSULTED`) | Patient consulted a doctor |
| Patient → Disease (`DIAGNOSED_WITH`) | Sample diagnosis |
| Disease → Medicine (`TREATED_WITH`) | Illustrative association |

## Example Cypher

```cypher
MATCH (p:Patient)-[:DIAGNOSED_WITH]->(d:Disease)
RETURN p.name, d.name;
```

## Limitations and safety
- All included records are fictional.
- Medicine relationships are illustrative, not treatment recommendations.
- No authentication, clinical validation or access-control system is implemented.
- This prototype is not suitable for real patient data or clinical decisions.

## Future enhancements
FHIR import, terminology mapping, authentication, role-based access, audit logs, consent-aware access and additional healthcare entities.

## Technology stack
Python • Streamlit • Neo4j Community Edition • Cypher • PyVis
