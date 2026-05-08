# Subskill: Ingest a Course Document

This subskill runs the full two-phase ingestion pipeline for a new course-note PDF.
It delegates to two sub-subskills — read them before starting each phase.

---

## Step 0 — Identify the document

Confirm the target PDF is in `docs/course-notes/`. Derive its `doc_id`:

| Filename contains | doc_id |
|---|---|
| Credit Assignment / Ch. 1 | `notes_credit_assignment` |
| Information Processing | `notes_information_processing` |
| Evolutionary Strategies | `notes_evolutionary_strategies` |
| Knowledge Representation | `notes_krr` |
| Representation | `notes_representation` |
| Search | `notes_search` |

For a document not in this list, derive a short descriptive snake_case suffix (`notes_<topic>`)
and confirm with the user before proceeding.

Then add or update the document's entry in `knowledge-base/documents.yaml` with its
canonical `doc_id`, title, path, aliases, and course order before touching any other file.

---

## Phase 1 — Extract vocabulary

Read `subskills/extract-vocabulary/SKILL.md` and complete that phase in full.

When finished:
- `knowledge-base/nodes.yaml` has all new nodes appended under the correct section
- Rebuild: `uv run python scripts/build_db.py`
- Confirm output reports the expected new node count
- Commit: `git add knowledge-base/nodes.yaml && git commit -m "vocab: add nodes from <doc_id>"`

---

## Phase 2 — Build connections

Read `subskills/build-connections/SKILL.md` and complete that phase in full.

**CRITICAL RULE: Read exactly one source document, then immediately update
`knowledge-base/relations.yaml`. Never read two or more documents before writing.**

When finished:
- `knowledge-base/relations.yaml` has new relation entries appended under a labelled block
- `knowledge-base/relation-schema.yaml` has any new relation types appended
- Rebuild: `uv run python scripts/build_db.py`
- Commit: `git add knowledge-base/relations.yaml knowledge-base/relation-schema.yaml && git commit -m "relations: add edges from <doc_id>"`

---

## Step 3 — Validate

```bash
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/nodes.yaml'))" && echo "nodes OK"
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relations.yaml'))" && echo "relations OK"
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relation-schema.yaml'))" && echo "schema OK"

sqlite-utils query ontology.db "
  SELECT r.source_id, r.target_id, r.rel_type
  FROM relations r
  LEFT JOIN nodes ns ON ns.id = r.source_id
  LEFT JOIN nodes nt ON nt.id = r.target_id
  WHERE ns.id IS NULL OR nt.id IS NULL
" --table

uv run python scripts/build_db.py && echo "DB OK"
```

Fix any errors before reporting the ingestion as complete.

---

## Step 4 — Refresh RAG index

```bash
uv run python scripts/rag.py sections --write
uv run python scripts/rag.py review-sections --doc-id <doc_id> --write
# Review .rag/reviews/<doc_id>.section-review.md; edit manifest if needed
uv run python scripts/rag.py index
```
