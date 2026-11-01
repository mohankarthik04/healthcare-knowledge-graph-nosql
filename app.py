import os
import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Healthcare Knowledge Graph", page_icon="🩺", layout="wide")
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "healthgraph123")

@st.cache_resource
def driver():
    return GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def query(cypher, params=None):
    with driver().session() as session:
        return list(session.run(cypher, params or {}))

def seed():
    statements = [
        "CREATE CONSTRAINT patient_id IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT doctor_id IF NOT EXISTS FOR (d:Doctor) REQUIRE d.id IS UNIQUE",
        "CREATE CONSTRAINT disease_name IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
        "CREATE CONSTRAINT medicine_name IF NOT EXISTS FOR (m:Medicine) REQUIRE m.name IS UNIQUE",
        """
        MERGE (p1:Patient {id:'P001'}) SET p1.name='Aarav Kumar', p1.age=32, p1.gender='Male'
        MERGE (p2:Patient {id:'P002'}) SET p2.name='Diya Sharma', p2.age=45, p2.gender='Female'
        MERGE (p3:Patient {id:'P003'}) SET p3.name='Kabir Nair', p3.age=27, p3.gender='Male'
        MERGE (d1:Doctor {id:'D001'}) SET d1.name='Dr. Meera Iyer', d1.specialty='Cardiology'
        MERGE (d2:Doctor {id:'D002'}) SET d2.name='Dr. Arjun Rao', d2.specialty='Endocrinology'
        MERGE (x1:Disease {name:'Hypertension'})
        MERGE (x2:Disease {name:'Type 2 Diabetes'})
        MERGE (x3:Disease {name:'Asthma'})
        MERGE (m1:Medicine {name:'Amlodipine'})
        MERGE (m2:Medicine {name:'Metformin'})
        MERGE (m3:Medicine {name:'Salbutamol'})
        MERGE (p1)-[:CONSULTED]->(d1)
        MERGE (p2)-[:CONSULTED]->(d2)
        MERGE (p3)-[:CONSULTED]->(d1)
        MERGE (p1)-[:DIAGNOSED_WITH]->(x1)
        MERGE (p2)-[:DIAGNOSED_WITH]->(x2)
        MERGE (p3)-[:DIAGNOSED_WITH]->(x3)
        MERGE (x1)-[:TREATED_WITH]->(m1)
        MERGE (x2)-[:TREATED_WITH]->(m2)
        MERGE (x3)-[:TREATED_WITH]->(m3)
        """
    ]
    with driver().session() as s:
        for statement in statements:
            s.run(statement)

st.title("🩺 Healthcare Knowledge Graph using NoSQL")
st.caption("Educational prototype • Python + Streamlit + Neo4j")
with st.sidebar:
    st.subheader("Neo4j database")
    st.code(URI)
    if st.button("Load demo records", use_container_width=True):
        try:
            seed()
            st.success("Fictional demo graph loaded.")
        except Exception as e:
            st.error(str(e))
    st.caption("Use fictional data only. Not a clinical decision-support system.")

try:
    driver().verify_connectivity()
except Exception as e:
    st.error("Neo4j is not reachable. Start it with `docker compose up -d`, then refresh.")
    st.code(str(e))
    st.stop()

try:
    counts = query("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS total")
    count_map = {r["label"]: r["total"] for r in counts}
    edges = query("MATCH ()-[r]->() RETURN count(r) AS n")[0]["n"]
    a,b,c,d = st.columns(4)
    a.metric("Nodes", sum(count_map.values()))
    b.metric("Relationships", edges)
    c.metric("Patients", count_map.get("Patient", 0))
    d.metric("Doctors", count_map.get("Doctor", 0))

    t1,t2,t3 = st.tabs(["Patient explorer", "Graph visualization", "Add patient"])
    with t1:
        patients = query("MATCH (p:Patient) RETURN p.id AS id, p.name AS name ORDER BY name")
        if patients:
            selected = st.selectbox("Select a patient", patients, format_func=lambda p: f'{p["name"]} ({p["id"]})')
            rows = query("""
                MATCH (p:Patient {id:$id})
                OPTIONAL MATCH (p)-[:CONSULTED]->(doc:Doctor)
                OPTIONAL MATCH (p)-[:DIAGNOSED_WITH]->(d:Disease)
                OPTIONAL MATCH (d)-[:TREATED_WITH]->(m:Medicine)
                RETURN p, collect(DISTINCT doc) AS doctors,
                       collect(DISTINCT d) AS diseases, collect(DISTINCT m) AS medicines
            """, {"id": selected["id"]})
            row = rows[0]
            st.subheader(row["p"]["name"])
            st.write(f'ID: {row["p"]["id"]}  |  Age: {row["p"].get("age","—")}  |  Gender: {row["p"].get("gender","—")}')
            x,y,z = st.columns(3)
            x.markdown("**Doctors**")
            for item in row["doctors"]:
                if item: x.write(f'- {item["name"]} ({item.get("specialty","—")})')
            y.markdown("**Diagnoses**")
            for item in row["diseases"]:
                if item: y.write(f'- {item["name"]}')
            z.markdown("**Related medicines**")
            for item in row["medicines"]:
                if item: z.write(f'- {item["name"]}')
        else:
            st.info("Load demo records from the sidebar first.")
    with t2:
        records = query("""
            MATCH (a)-[r]->(b)
            RETURN labels(a)[0] AS at, coalesce(a.name,a.id) AS a,
                   type(r) AS rel, labels(b)[0] AS bt, coalesce(b.name,b.id) AS b
        """)
        if records:
            net = Network(height="560px", width="100%", directed=True, bgcolor="#ffffff", font_color="#222222")
            net.barnes_hut()
            colors = {"Patient":"#8ecae6","Doctor":"#ffb703","Disease":"#90be6d","Medicine":"#f4a6a6"}
            for r in records:
                net.add_node(r["a"], label=r["a"], title=r["at"], color=colors.get(r["at"],"#cccccc"))
                net.add_node(r["b"], label=r["b"], title=r["bt"], color=colors.get(r["bt"],"#cccccc"))
                net.add_edge(r["a"], r["b"], label=r["rel"])
            components.html(net.generate_html(), height=580, scrolling=True)
        else:
            st.info("No graph records yet. Load demo records first.")
    with t3:
        st.write("Add a fictional patient node and optionally connect an existing doctor.")
        doctors = query("MATCH (d:Doctor) RETURN d.id AS id, d.name AS name ORDER BY name")
        with st.form("patient_form"):
            pid = st.text_input("Patient ID")
            name = st.text_input("Patient name")
            age = st.number_input("Age", 0, 120, 30)
            gender = st.selectbox("Gender", ["Female","Male","Other","Prefer not to say"])
            doctor_options = ["None"] + [f'{v["id"]} — {v["name"]}' for v in doctors]
            doctor = st.selectbox("Consulting doctor", doctor_options)
            submitted = st.form_submit_button("Save patient")
        if submitted:
            if not pid.strip() or not name.strip():
                st.warning("Enter both patient ID and name.")
            else:
                try:
                    query("CREATE (p:Patient {id:$id,name:$name,age:$age,gender:$gender})",
                          {"id":pid.strip(),"name":name.strip(),"age":int(age),"gender":gender})
                    if doctor != "None":
                        query("MATCH (p:Patient {id:$pid}),(d:Doctor {id:$did}) MERGE (p)-[:CONSULTED]->(d)",
                              {"pid":pid.strip(),"did":doctor.split(" — ")[0]})
                    st.success("Patient added.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save patient. Patient IDs must be unique. {e}")
except Exception as e:
    st.error(f"Database operation failed: {e}")

st.divider()
st.caption("Fictional sample data only. Not for diagnosis, prescribing or real patient records.")
