#!/usr/bin/env python3
"""Convert YAML ontology files into a SQLite database."""

import sqlite3
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "ontology.db"
ONTOLOGY_YAML = ROOT / "ontology.yaml"
RELATIONS_YAML = ROOT / "knowledge-base" / "relations.yaml"
METADATA_YAML = ROOT / "knowledge-base" / "metadata.yaml"


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def build_db():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")

    # Schema — execute each statement separately
    cur.execute("""
        CREATE TABLE nodes (
            id          TEXT PRIMARY KEY,
            label       TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            node_type   TEXT NOT NULL CHECK(node_type IN ('concept','person','institution','example')),
            module      INTEGER,
            tags        TEXT NOT NULL DEFAULT '[]',
            person_type TEXT CHECK(person_type IN ('person','institution')),
            era         TEXT,
            affiliation TEXT,
            example_source TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE relations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            rel_type    TEXT NOT NULL CHECK(rel_type IN (
                            'IS-A','PART-OF','CAUSES','CONTRASTS-WITH',
                            'EXAMPLE-OF','REQUIRES','ATTRIBUTED-TO'
                        )),
            source_id   TEXT NOT NULL REFERENCES nodes(id),
            target_id   TEXT NOT NULL REFERENCES nodes(id),
            note        TEXT NOT NULL DEFAULT '',
            UNIQUE(rel_type, source_id, target_id)
        )
    """)
    cur.execute("""
        CREATE TABLE source_documents (
            node_id     TEXT NOT NULL REFERENCES nodes(id),
            doc_id      TEXT NOT NULL,
            PRIMARY KEY (node_id, doc_id)
        )
    """)
    cur.execute("CREATE INDEX idx_rel_source ON relations(source_id)")
    cur.execute("CREATE INDEX idx_rel_target ON relations(target_id)")
    cur.execute("CREATE INDEX idx_rel_type   ON relations(rel_type)")
    conn.commit()

    # --- Load YAML ---
    ont = load_yaml(ONTOLOGY_YAML)
    meta = load_yaml(METADATA_YAML)
    rels = load_yaml(RELATIONS_YAML)

    # Build metadata lookup
    concept_meta = {m["id"]: m for m in meta.get("concepts", [])}
    person_meta  = {m["id"]: m for m in meta.get("people_and_institutions", [])}
    example_meta = {m["id"]: m for m in meta.get("examples_and_metaphors", [])}

    inserted = set()

    def insert_node(nid, node_type, md):
        if nid in inserted:
            return
        md = md or {}
        label = md.get("label", nid.replace("_", " ").title())
        description = md.get("description", "")
        module = md.get("module") if node_type == "concept" else None
        tags = md.get("tags", [])
        tags_json = str(tags) if tags else "[]"
        person_type = md.get("type") if node_type in ("person", "institution") else None
        era = md.get("era") if node_type in ("person", "institution") else None
        affiliation = md.get("affiliation") if node_type in ("person", "institution") else None
        example_source = md.get("source") if node_type == "example" else None
        cur.execute("""
            INSERT OR IGNORE INTO nodes
                (id, label, description, node_type, module, tags,
                 person_type, era, affiliation, example_source)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (nid, label, description, node_type, module, tags_json,
              person_type, era, affiliation, example_source))
        inserted.add(nid)
        # source documents
        for doc_id in md.get("source_documents", []):
            cur.execute("INSERT OR IGNORE INTO source_documents (node_id, doc_id) VALUES (?,?)",
                        (nid, doc_id))

    # Insert all nodes
    for entry in ont.get("concepts", []):
        nid = entry["id"]
        insert_node(nid, "concept", concept_meta.get(nid, {}))

    for entry in ont.get("people_and_institutions", []):
        nid = entry["id"]
        md = person_meta.get(nid, {})
        ptype = md.get("type", "person")  # default if unspecified
        insert_node(nid, ptype, md)

    for entry in ont.get("examples_and_metaphors", []):
        nid = entry["id"]
        insert_node(nid, "example", example_meta.get(nid, {}))

    # Insert relations
    for r in rels.get("relations", []):
        cur.execute("""
            INSERT OR IGNORE INTO relations (rel_type, source_id, target_id, note)
            VALUES (?,?,?,?)
        """, (r["type"], r["source"], r["target"], r.get("note", "")))

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")
    print(f"  Nodes:     {len(inserted)}")
    print(f"  Relations: {len(rels.get('relations', []))}")


if __name__ == "__main__":
    build_db()
