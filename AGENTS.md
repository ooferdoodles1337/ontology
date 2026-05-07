# Ontology Maintenance Instructions

> **`.agents/` is the primary source of truth** — all settings, skills, and configuration live here.
> **`.claude/` is a symlink to `.agents/`** for tool compatibility. Do not edit `.claude/` directly; make all changes in `.agents/`.

This project builds a concept graph for a course (FAB 2026). The graph is stored in YAML files and a SQLite database (`ontology.db`).

## File Roles

| File | Purpose |
|------|---------|
| `knowledge-base/nodes.yaml` | All nodes (concepts, people, examples) with their metadata. Single source of truth for vocabulary and node descriptions. |
| `knowledge-base/relations.yaml` | Relation instances — every edge in the graph with source, target, type, and note. |
| `knowledge-base/relation-schema.yaml` | The evolving vocabulary of relation types. Read before extracting relations; update after coining new types. |
| `docs/course-notes/` | Source documents to extract from. |

---

## Node ID Conventions

- Always `snake_case`, lowercase.
- Concepts: plain noun phrase — `credit_assignment`, `constraint_propagation`
- People / institutions: `firstname_lastname` or institution name — `herbert_simon`, `carnegie_mellon`
- Examples / metaphors: always prefixed with `ex_` — `ex_checkers_game`, `ex_watchmaker_parable_1000_parts`

---

## Relation Types

Relation types are **not predefined**. They are maintained in `knowledge-base/relation-schema.yaml`
and grow as documents are processed.

**Rules when extracting relations:**
1. Read `relation-schema.yaml` first. Reuse an existing type whenever it reasonably fits —
   consistency across documents matters more than precision.
2. Invent a new type only when no existing one captures the relationship without distorting it.
   Use a short UPPER-CASE verb phrase: `ENABLES`, `MOTIVATES`, `OPERATIONALISES`, `SCALES-WITH`.
3. After writing relations, append any new types to `relation-schema.yaml`.
4. If a later document reveals a better way to name or structure existing types, refactor:
   update the schema entry and run `python scripts/rename_relation_type.py OLD NEW` to
   propagate the rename across all of `relations.yaml`.

---

## Process: Adding a New Document

When one or more new documents are placed in `docs/`, follow these steps **strictly in order**.

### Step 1 — Extract new vocabulary (before touching any existing document)

Read the new document and collect every term that does not already appear as a node in
`knowledge-base/nodes.yaml`. Categorise each as concept, person/institution, or example.

Add all new entries to `knowledge-base/nodes.yaml` under the correct section, grouped under
a comment naming the module or document they came from.

Also add the `doc_id` to the `source_documents` list of any existing nodes re-introduced
by this document.

Commit this vocabulary update before proceeding to Step 2.

---

### Step 2 — Extract relations, one document at a time

**CRITICAL RULE: Read exactly one source document, then immediately update `knowledge-base/relations.yaml`. Never read two or more documents before writing.**

For each document (working through them in module order):

1. Read `knowledge-base/relation-schema.yaml` to load the current type vocabulary.
2. Read the document in full.
3. Identify every relationship that is explicitly stated or strongly implied.
4. Append relations to `relations.yaml` under a labelled comment block.
5. Append any new relation types to `relation-schema.yaml`.
6. Rebuild the DB and validate before moving to the next document.

---

## Entry Formats

**Uniform schema rule:** Every node uses exactly four fields — `id`, `label`, `description`,
`source_documents` — and nothing else. Do not add `type`, `era`, `affiliation`, `source`,
`illustrates`, `module`, or any other field. Encode affiliation, era, and what an example
illustrates in the `description` text.

### knowledge-base/nodes.yaml — adding any node
```yaml
- id: node_id
  label: Human Readable Name
  description: >
    One or two sentences. For people, include era and affiliation here.
    For examples, mention what the example illustrates and its source.
  source_documents:
  - doc_id
```

### knowledge-base/relations.yaml — adding a relation
```yaml
- type: RELATION-TYPE         # from relation-schema.yaml vocabulary
  source: source_node
  target: target_node
  note: >
    One or two sentences explaining why this relation holds, citing
    the text if possible. This becomes the edge tooltip in the graph.
  quote: >
    "verbatim excerpt from the source document that directly supports this relation"
```

`quote` is a short verbatim passage (≤ 2 sentences) copied exactly from the source PDF. Use
ellipsis (`…`) to trim irrelevant middle text. If the relation is strongly implied but not
explicitly stated, write `quote: ~` (null).

### knowledge-base/relation-schema.yaml — adding a relation type
```yaml
- name: RELATION-TYPE
  description: "One sentence: what A→B means."
  direction: "A → B (role of A → role of B)"
  first_seen: doc_id
  aliases: []
```

---

## Validation Checklist

Before finishing any update session, verify:

- [ ] Every `source` and `target` in `relations.yaml` exists as an `id` in `nodes.yaml`.
- [ ] No duplicate relation entries (same type + source + target pair).
- [ ] All new node IDs follow `snake_case` and `ex_` prefix rules.
- [ ] Each relation has a non-empty `note`.
- [ ] Each relation has a `quote` field (verbatim excerpt or `~` for implied relations).
- [ ] All new relation types in `relations.yaml` have an entry in `relation-schema.yaml`.
- [ ] YAML parses without error:
  ```bash
  uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/nodes.yaml'))"
  uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relations.yaml'))"
  uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relation-schema.yaml'))"
  ```
- [ ] DB rebuilds cleanly: `uv run python scripts/build_db.py`

---

## What NOT to Do

- Do not invent relations that are not supported by the course documents.
- Do not add a node ID that is a near-duplicate of an existing one (check before adding).
- Do not read all documents first and then batch-write relations. Process one document, write, then move to the next.
- Do not write YAML files programmatically using `cat` heredocs or shell redirects. Use the Edit/Write tools to modify YAML files directly — this is safer, avoids escaping issues, and produces clean diffs.
- Do not query or inspect the SQLite database by writing inline Python scripts. Use the `sqlite-utils` CLI instead (e.g. `sqlite-utils query ontology.db "SELECT ..." --table`).
