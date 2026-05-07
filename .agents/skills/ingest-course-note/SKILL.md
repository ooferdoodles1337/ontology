---
name: ingest-course-note
description: >
  Full pipeline for adding a new FAB 2026 course note PDF to the ontology. Use this skill
  whenever a new document has been placed in docs/course-notes/ and needs to be processed —
  "ingest this document", "add the new course note", "process the search PDF", "update the
  ontology with module 4" — even if the user doesn't say "ingest" or "pipeline". Any task
  that involves reading a course document and updating the YAML files or database should
  use this skill.
---

# Ingesting a New Course Note

This skill runs the full two-phase pipeline. It delegates each phase to a subskill — read
the relevant subskill file before starting that phase.

## Subskills

| File | Phase | What it does |
|------|-------|--------------|
| `subskills/extract-vocabulary.md` | Phase 1 | Parse PDF → extract new nodes → write `knowledge-base/nodes.yaml` |
| `subskills/build-connections.md`  | Phase 2 | Re-read doc → query existing graph → write `relations.yaml` + update `relation-schema.yaml` |

## Pipeline

### 0. Identify the document

Confirm the target PDF is in `docs/course-notes/`. Derive its `doc_id` by taking the
subject-matter portion of the filename, lowercasing, and snake_casing with a `notes_` prefix:

| Filename contains | doc_id |
|---|---|
| Credit Assignment / Ch. 1 | `notes_credit_assignment` |
| Information Processing | `notes_information_processing` |
| Evolutionary Strategies | `notes_evolutionary_strategies` |
| Knowledge Representation | `notes_krr` |
| Representation | `notes_representation` |
| Search | `notes_search` |

For a document not in this list, derive a short, descriptive snake_case suffix and confirm
with the user before proceeding.

### 1. Extract vocabulary (read `subskills/extract-vocabulary.md`)

Run the full vocabulary extraction phase. When complete:
- `knowledge-base/nodes.yaml` has all new nodes appended under the correct section
- **Rebuild the database**: `uv run python scripts/build_db.py`
- Confirm output reports the expected new node count
- Commit: `git add knowledge-base/nodes.yaml && git commit -m "vocab: add nodes from <doc_id>"`

### 2. Build connections (read `subskills/build-connections.md`)

Run the full connection-building phase. When complete:
- `knowledge-base/relations.yaml` has new relation entries appended under a labelled block
- `knowledge-base/relation-schema.yaml` has any new relation types appended
- **Rebuild the database**: `uv run python scripts/build_db.py`
- Commit: `git add knowledge-base/relations.yaml knowledge-base/relation-schema.yaml && git commit -m "relations: add edges from <doc_id>"`

### 3. Validate

```bash
# YAML validity
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/nodes.yaml'))" && echo "nodes OK"
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relations.yaml'))" && echo "relations OK"
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relation-schema.yaml'))" && echo "schema OK"

# Referential integrity — every source/target must exist as a node
# (no rows = all refs valid; any rows = broken references that must be fixed)
sqlite-utils query ontology.db "
  SELECT r.source_id, r.target_id, r.rel_type
  FROM relations r
  LEFT JOIN nodes ns ON ns.id = r.source_id
  LEFT JOIN nodes nt ON nt.id = r.target_id
  WHERE ns.id IS NULL OR nt.id IS NULL
" --table

# Graph regeneration
uv run python visualize.py && echo "visualizer OK"
```

Fix any errors before reporting the ingestion as complete.
