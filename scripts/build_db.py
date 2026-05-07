#!/usr/bin/env python3
"""Convert YAML ontology files into a SQLite database."""

import sqlite3
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "ontology.db"
NODES_YAML = ROOT / "knowledge-base" / "nodes.yaml"
RELATIONS_YAML = ROOT / "knowledge-base" / "relations.yaml"


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def build_db():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")

    cur.execute("""
        CREATE TABLE nodes (
            id          TEXT PRIMARY KEY,
            label       TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            node_type   TEXT NOT NULL CHECK(node_type IN ('concept','person','example'))
        )
    """)
    cur.execute("""
        CREATE TABLE relations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            rel_type    TEXT NOT NULL,
            source_id   TEXT NOT NULL REFERENCES nodes(id),
            target_id   TEXT NOT NULL REFERENCES nodes(id),
            note        TEXT NOT NULL DEFAULT '',
            quote       TEXT,
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

    nodes_data = load_yaml(NODES_YAML)
    rels_data  = load_yaml(RELATIONS_YAML)

    inserted = set()

    def insert_node(nid, node_type, md):
        if nid in inserted:
            return
        md = md or {}
        label       = md.get("label", nid.replace("_", " ").title())
        description = md.get("description", "")
        cur.execute("""
            INSERT OR IGNORE INTO nodes (id, label, description, node_type)
            VALUES (?,?,?,?)
        """, (nid, label, description, node_type))
        inserted.add(nid)
        for doc_id in md.get("source_documents", []):
            cur.execute("INSERT OR IGNORE INTO source_documents (node_id, doc_id) VALUES (?,?)",
                        (nid, doc_id))

    for entry in nodes_data.get("concepts", []):
        insert_node(entry["id"], "concept", entry)

    for entry in nodes_data.get("people_and_institutions", []):
        insert_node(entry["id"], "person", entry)

    for entry in nodes_data.get("examples_and_metaphors", []):
        insert_node(entry["id"], "example", entry)

    for r in (rels_data.get("relations") or []):
        cur.execute("""
            INSERT OR IGNORE INTO relations (rel_type, source_id, target_id, note, quote)
            VALUES (?,?,?,?,?)
        """, (r["type"], r["source"], r["target"], r.get("note", ""), r.get("quote")))

    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")
    print(f"  Nodes:     {len(inserted)}")
    print(f"  Relations: {len((rels_data.get('relations') or []))}")


if __name__ == "__main__":
    build_db()
