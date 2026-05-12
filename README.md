# FAB 2026 Ontology

Course ontology for FAB Spring 2026. Concepts, relations, and a SQLite database for querying.

## Files

- `knowledge-base/nodes.yaml` — node vocabulary (concepts, people, examples)
- `knowledge-base/documents.yaml` — source document registry and canonical doc IDs
- `knowledge-base/relations.yaml` — directed relations between nodes
- `knowledge-base/relation-schema.yaml` — relation type vocabulary
- `ontology_core/` — shared Python helpers for paths, YAML I/O, KB access, notes, and the local server
- `web/` — Study Hub browser UI, with HTML, styles, and scripts split by concern
- `scripts/` — command-line tools for DB builds, RAG, study planning, flashcards, and serving the UI
- `ontology.db` — compiled SQLite database (built from the YAML files)

## Running the Study Hub

```bash
uv run python scripts/serve.py
```

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
