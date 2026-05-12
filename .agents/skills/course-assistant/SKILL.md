---
name: course-assistant
description: >
  The unified assistant for the FAB 2026 ontology project. Use this skill for any task
  related to the course knowledge base — querying concepts, people, examples, and relations;
  answering natural-language questions from course notes; ingesting new documents into the
  graph; or generating study quizzes. Triggers include: "what concepts are in module 3?", "what does the course say
  about X?", "who are the people in the graph?", "how are X and Y connected?", "ingest this
  document", "add the new course note", "make a quiz on search", "quiz me on module 3".
---

# FAB 2026 Course Assistant

This skill is the single entry point for all work on the FAB 2026 concept graph.
Read the shared context below, then load the appropriate subskill.

---

## Task Routing

Read the task, pick one subskill, load it, then follow its instructions.

| If the user wants… | Load subskill |
|---|---|
| List or explore nodes, relations, people, examples, counts, connectivity | `subskills/query-db/SKILL.md` |
| Understand what the course *means* by a concept; fuzzy semantic question; source passage | `subskills/query-rag/SKILL.md` |
| Ingest a new course-note document | `subskills/ingest-document/SKILL.md` |
| Generate a study artifact (quiz, flashcards, etc.) | `subskills/artifacts/SKILL.md` |
| Rank concepts by importance; prioritise what to study; select top concepts for a time budget | `subskills/concept-ranker/SKILL.md` |
| Build a day-by-day study schedule; show today's sessions; mark a concept as mastered | `subskills/study-planner/SKILL.md` |
| Remember the student, update goals, inspect struggles/mastery, explain recommendations | `subskills/learner-model/SKILL.md` |

When the task spans two concerns (e.g. "answer a course question and then make a quiz about it"),
complete them sequentially: finish the first, then load the second subskill.

---

## Shared Context

The following context is authoritative for all subskills. Subskills do not restate it.

---

### File Roles

| File | Purpose |
|---|---|
| `knowledge-base/documents.yaml` | Source-document registry: canonical `doc_id`, title, path, aliases, course order |
| `knowledge-base/nodes.yaml` | All nodes — concepts, people, examples. Single source of truth for vocabulary |
| `knowledge-base/relations.yaml` | Every edge in the graph with source, target, type, note, and quote |
| `knowledge-base/relation-schema.yaml` | Evolving vocabulary of relation types. Read before extracting; update after coining new types |
| `docs/course-notes/` | Source PDFs to extract from |
| `ontology.db` | SQLite database built from the YAML files. Rebuild with `uv run python scripts/build_db.py` |
| `artifacts/` | Output directory for generated files (quizzes, exports) |
| `.rag/manifests/*.sections.json` | Durable RAG section-boundary manifests |
| `.rag/reviews/*.section-review.md` | LLM-facing packets for checking section boundaries |

---

### Database Schema

```sql
nodes (
    id           TEXT PRIMARY KEY,   -- snake_case identifier
    label        TEXT,               -- human-readable name
    description  TEXT,               -- definition or bio
    node_type    TEXT,               -- 'concept' | 'person' | 'institution' | 'example'
    module       INTEGER             -- 1–6 (concepts only)
)

relations (
    id         INTEGER PRIMARY KEY,
    rel_type   TEXT,     -- from relation-schema.yaml vocabulary
    source_id  TEXT,     -- REFERENCES nodes(id)
    target_id  TEXT,     -- REFERENCES nodes(id)
    note       TEXT,     -- explanation of why this relation holds
    quote      TEXT      -- verbatim excerpt supporting this relation, or NULL
)

source_documents (
    node_id  TEXT,
    doc_id   TEXT
)
```

Always query via `sqlite-utils`:
```bash
sqlite-utils query ontology.db "SELECT ..." --table
```

Do not write inline Python scripts to query SQLite.

---

### Node ID Conventions

- Always `snake_case`, lowercase.
- Concepts: plain noun phrase — `credit_assignment`, `constraint_propagation`
- People / institutions: `firstname_lastname` or institution name — `herbert_simon`, `carnegie_mellon`
- Examples / metaphors: always prefixed `ex_` — `ex_checkers_game`, `ex_watchmaker_parable`

---

### Entry Formats

**Uniform schema rule:** Every node uses exactly four fields. No others.

```yaml
# knowledge-base/nodes.yaml
- id: node_id
  label: Human Readable Name
  description: >
    One or two sentences. For people, include era and affiliation.
    For examples, mention what it illustrates and its source.
  source_documents:
  - doc_id
```

```yaml
# knowledge-base/relations.yaml
- type: RELATION-TYPE
  source: source_node
  target: target_node
  note: >
    One or two sentences explaining why this relation holds.
  quote: >
    "verbatim excerpt from the source document"
```
Use `quote: ~` when the relation is strongly implied but not explicitly stated.

```yaml
# knowledge-base/relation-schema.yaml
- name: RELATION-TYPE
  description: "One sentence: what A→B means."
  direction: "A → B (role of A → role of B)"
  first_seen: doc_id
  aliases: []
```

---

### Question Routing: RAG vs SQLite vs Source Documents

Choose the smallest source that can answer accurately.

| Question type | Use |
|---|---|
| "What does the course mean by X?", fuzzy comparison, source passage | RAG (`subskills/query-rag.md`) |
| List nodes/relations, count, connectivity, exact ID lookup | SQLite (`subskills/query-db.md`) |
| Exact wording, quotes, new/unindexed document, ingestion | Read source file directly |

Default sequence for ambiguous questions:
1. Natural-language course question → RAG first
2. Answer depends on exact graph facts → verify with SQLite
3. Exact quotes or ingestion-quality evidence needed → read source document
4. Question about code or file structure → read files directly

---

### Validation Checklist

Run before finishing any session that modifies YAML or the database:

- [ ] Every `source` and `target` in `relations.yaml` exists as an `id` in `nodes.yaml`
- [ ] No duplicate relations (same type + source + target)
- [ ] All new node IDs follow `snake_case` and `ex_` prefix rules
- [ ] Each relation has a non-empty `note` and a `quote` field (verbatim or `~`)
- [ ] All new relation types in `relations.yaml` have an entry in `relation-schema.yaml`
- [ ] YAML parses without error:
  ```bash
  uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/documents.yaml'))" && echo "documents OK"
  uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/nodes.yaml'))" && echo "nodes OK"
  uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relations.yaml'))" && echo "relations OK"
  uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relation-schema.yaml'))" && echo "schema OK"
  ```
- [ ] DB rebuilds cleanly: `uv run python scripts/build_db.py`
