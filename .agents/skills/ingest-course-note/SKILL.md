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

This skill runs the full two-phase pipeline defined in CLAUDE.md. It delegates each phase
to a subskill — read the relevant subskill file before starting that phase.

## Subskills

| File | Phase | What it does |
|------|-------|--------------|
| `subskills/extract-vocabulary.md` | Phase 1 | Parse PDF → extract new nodes → write `ontology.yaml` + `metadata.yaml` |
| `subskills/build-connections.md`  | Phase 2 | Re-read doc → query existing graph → write `relations.yaml` |

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

For a document not in this list, derive a short, descriptive snake_case suffix yourself and
confirm it with the user before proceeding.

### 1. Extract vocabulary (read `subskills/extract-vocabulary.md`)

Run the full vocabulary extraction phase. When the subskill is complete:
- `ontology.yaml` has all new node IDs appended under the correct section
- `metadata.yaml` has a metadata entry for every new node, with `source_documents` set
- **Rebuild the database**: `uv run python scripts/build_db.py`
- Confirm the output reports the expected new node count
- Commit: `git add ontology.yaml knowledge-base/metadata.yaml && git commit -m "vocab: add nodes from <doc_id>"`

### 2. Build connections (read `subskills/build-connections.md`)

Run the full connection-building phase. When the subskill is complete:
- `relations.yaml` has new relation entries appended under a labelled comment block
- **Rebuild the database**: `uv run python scripts/build_db.py`
- Commit: `git add knowledge-base/relations.yaml && git commit -m "relations: add edges from <doc_id>"`

### 3. Validate

Run the full CLAUDE.md validation checklist:

```bash
# YAML validity
uv run python -c "import yaml; yaml.safe_load(open('ontology.yaml'))" && echo "ontology OK"
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relations.yaml'))" && echo "relations OK"
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/metadata.yaml'))" && echo "metadata OK"

# Referential integrity — every source/target must exist as a node
uv run python -c "
import yaml, sys
ont = yaml.safe_load(open('ontology.yaml'))
ids = {e['id'] for section in ['concepts','people_and_institutions','examples_and_metaphors']
       for e in ont.get(section, [])}
rels = yaml.safe_load(open('knowledge-base/relations.yaml'))
bad = [(r['source'], r['target'], r['type']) for r in rels.get('relations', [])
       if r['source'] not in ids or r['target'] not in ids]
if bad:
    print('BROKEN REFS:', bad); sys.exit(1)
else:
    print('All refs valid')
"

# Graph regeneration
uv run python visualize.py && echo "visualizer OK"
```

Fix any errors before reporting the ingestion as complete.
