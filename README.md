# FAB 2026 Ontology

Course ontology for FAB Spring 2026. Concepts, relations, and a SQLite database for querying.

## Files

- `knowledge-base/nodes.yaml` — node vocabulary (concepts, people, examples)
- `knowledge-base/documents.yaml` — source document registry and canonical doc IDs
- `knowledge-base/relations.yaml` — directed relations between nodes
- `knowledge-base/relation-schema.yaml` — relation type vocabulary
- `ontology.db` — compiled SQLite database (built from the YAML files)

## Rebuilding the database

```bash
uv run python scripts/build_db.py
```

## RAG chunk manifests

Draft section manifests, generate LLM review packets, then index:

```bash
uv run python scripts/rag.py sections --write
uv run python scripts/rag.py review-sections --write
uv run python scripts/rag.py index
```
