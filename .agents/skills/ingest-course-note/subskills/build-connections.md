# Subskill: Build Connections

**Purpose:** Using the full parsed text already in context (from the extract-vocabulary phase),
identify every relationship between nodes and append them to `knowledge-base/relations.yaml`.
Relation types are not predefined — they come from a shared vocabulary in
`knowledge-base/relation-schema.yaml` that grows across documents.

---

## Step 0 — Load the relation-type vocabulary

Read `knowledge-base/relation-schema.yaml` directly. Internalise every entry: its name,
description, and direction. You will match new relations against this vocabulary before
inventing anything new.

If the file has no entries yet (first document), you will build the initial vocabulary from scratch.

---

## Step 1 — Orient yourself in the existing graph

Read `knowledge-base/nodes.yaml` directly to see what nodes exist — no script needed.
Grep or skim for the `doc_id` you are working on to identify which nodes belong to this document.

For queries that require a JOIN (e.g., "all nodes with this source document"), use `sqlite-utils`:

```bash
sqlite-utils query ontology.db "
SELECT n.id, n.label, n.node_type
FROM nodes n
JOIN source_documents sd ON sd.node_id = n.id
WHERE sd.doc_id = '<doc_id>'
ORDER BY n.node_type, n.label
" --table
```

**Check whether a relation already exists (avoid duplicates)** — read `relations.yaml` directly
and search for the pair, or use `sqlite-utils` for precision:

```bash
sqlite-utils query ontology.db "
SELECT rel_type, note FROM relations
WHERE (source_id = 'a' AND target_id = 'b')
   OR (source_id = 'b' AND target_id = 'a')
" --table
```

---

## Step 2 — Identify relationships from the text

Re-read the document. For each pair of nodes where the text explicitly states or strongly implies
a meaningful relationship, draft a candidate relation:

1. **Check the existing vocabulary** — does any existing type fit?
   Use it if there's a reasonable match. Consistency across documents matters more than precision.
2. **Invent a new type** only if no existing one captures the relationship without distorting it.
   Guidelines for new types:
   - Short verb phrase in UPPER-CASE, hyphenated: `ENABLES`, `MOTIVATES`, `OPERATIONALISES`, `SCALES-WITH`
   - Precise enough to be reusable across multiple concept pairs from different documents
   - Avoid single-use types — if it would only ever apply to this one pair, put the nuance in `note` instead

**Quote discipline:** As you identify each relation, locate the exact supporting sentence in the
document and copy it verbatim — you'll need it for the `quote` field. If the relation is
structurally implied (e.g., section ordering implies prerequisite) rather than stated outright,
flag it so you can write `quote: ~` later.

---

## Step 3 — Refactor the vocabulary (optional, but encouraged)

Before writing, ask: does this document expose any inconsistency or redundancy in existing types?
For example:
- Two types that mean nearly the same thing and should be merged
- A type whose name is ambiguous now that you've seen more examples
- A type that should be split into two more precise concepts

If so, refactor:
1. Update the entry in `relation-schema.yaml` — change the `name` and add the old name to `aliases`
2. Rename all existing instances in `relations.yaml`:
   ```bash
   uv run python scripts/rename_relation_type.py "OLD-NAME" "NEW-NAME"
   ```
3. Rebuild the DB: `uv run python scripts/build_db.py`

Only refactor when the improvement is clear. Don't rename types just for style.

---

## Step 4 — Verify node IDs

Read `knowledge-base/nodes.yaml` directly and confirm both `source` and `target` IDs exist
before writing any relation. If you need to check many IDs at once, grep for them:

```bash
grep -E "^- id: (id1|id2|id3)$" knowledge-base/nodes.yaml
```

Any ID not found is missing — fix the spelling or add the node in `knowledge-base/nodes.yaml`
first (then rebuild the DB with `uv run python scripts/build_db.py`) before writing the relation.

---

## Step 5 — Update the relation-type vocabulary

For every **new** type coined in Step 2, append an entry to `knowledge-base/relation-schema.yaml`:

```yaml
- name: NEW-TYPE
  description: "One sentence: what this relation means, what it captures."
  direction: "A → B (role of A → role of B)"
  first_seen: <doc_id>
  aliases: []
```

Add only types not already present. Keep `description` crisp — it should let a future reader
decide whether to reuse this type.

---

## Step 6 — Append relations to `relations.yaml`

Add a clearly labelled block at the end of `knowledge-base/relations.yaml`:

```yaml
  # =========================================================
  # <Document Title>
  # Source: <filename>
  # =========================================================

  - type: RELATION-TYPE
    source: source_node
    target: target_node
    note: >
      One or two sentences explaining why this relation holds,
      citing the text where possible.
    quote: >
      "verbatim excerpt from the document that directly supports this relation"
```

Group relations by type within each document block. Every relation needs a non-empty `note`
and a `quote` field. Use `quote: ~` only when the relation is structurally implied.
Keep quotes ≤ 2 sentences; use `…` to trim middle text.

---

## Step 7 — Validate YAML and referential integrity

```bash
# Parse check
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
```

Fix any errors before returning control to the parent skill.
