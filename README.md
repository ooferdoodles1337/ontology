# FAB 2026 Ontology

Course ontology for FAB Spring 2026. Concepts, relations, and a SQLite database for querying.

## Files

- `knowledge-base/nodes.yaml` — node vocabulary (concepts, people, examples)
- `knowledge-base/relations.yaml` — directed relations between nodes
- `knowledge-base/relation-schema.yaml` — relation type vocabulary
- `ontology.db` — compiled SQLite database (built from the YAML files)

## Rebuilding the database

```bash
uv run python scripts/build_db.py
```
