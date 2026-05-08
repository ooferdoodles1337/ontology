# Subskill: Query the Ontology Database

Use this subskill for exact, structural, or countable questions about the graph:
listing nodes, finding relations, checking connectivity, counting entries, detecting
duplicates, or validating IDs.

Before querying, ensure the DB is fresh:
```bash
uv run python scripts/build_db.py 2>/dev/null || true
```

Then run queries with `sqlite-utils query ontology.db "..." --table`.

---

## Common Query Patterns

**All concepts in a module:**
```bash
sqlite-utils query ontology.db "
  SELECT id, label, description
  FROM nodes
  WHERE node_type = 'concept' AND module = 3
  ORDER BY label
" --table
```

**Find a concept by keyword:**
```bash
sqlite-utils query ontology.db "
  SELECT id, label, module, description
  FROM nodes
  WHERE node_type = 'concept'
    AND (label LIKE '%keyword%' OR description LIKE '%keyword%')
" --table
```

**All relations for a node (both directions):**
```bash
sqlite-utils query ontology.db "
  SELECT rel_type, source_id, target_id, note
  FROM relations
  WHERE source_id = 'node_id' OR target_id = 'node_id'
" --table
```

**Outgoing relations (what does X cause/require/enable):**
```bash
sqlite-utils query ontology.db "
  SELECT r.rel_type, n.label AS target_label, r.note
  FROM relations r
  JOIN nodes n ON n.id = r.target_id
  WHERE r.source_id = 'node_id'
  ORDER BY r.rel_type
" --table
```

**Incoming relations (what IS-A or REQUIRES points to X):**
```bash
sqlite-utils query ontology.db "
  SELECT r.rel_type, n.label AS source_label, r.note
  FROM relations r
  JOIN nodes n ON n.id = r.source_id
  WHERE r.target_id = 'node_id'
  ORDER BY r.rel_type
" --table
```

**All people and institutions:**
```bash
sqlite-utils query ontology.db "
  SELECT id, label, node_type, description
  FROM nodes
  WHERE node_type IN ('person', 'institution')
  ORDER BY label
" --table
```

**Examples illustrating a concept:**
```bash
sqlite-utils query ontology.db "
  SELECT n.id, n.label, n.description
  FROM relations r
  JOIN nodes n ON n.id = r.source_id
  WHERE r.rel_type = 'EXAMPLE-OF' AND r.target_id = 'concept_id'
" --table
```

**Does a relation exist between two nodes?**
```bash
sqlite-utils query ontology.db "
  SELECT rel_type, note, quote
  FROM relations
  WHERE (source_id = 'a' AND target_id = 'b')
     OR (source_id = 'b' AND target_id = 'a')
" --table
```

**Most-connected concepts (by degree):**
```bash
sqlite-utils query ontology.db "
  SELECT n.label, COUNT(*) AS degree
  FROM nodes n
  JOIN (
      SELECT source_id AS id FROM relations
      UNION ALL
      SELECT target_id AS id FROM relations
  ) r ON r.id = n.id
  GROUP BY n.id
  ORDER BY degree DESC
  LIMIT 20
" --table
```

**All nodes from a specific document:**
```bash
sqlite-utils query ontology.db "
  SELECT n.id, n.label, n.node_type
  FROM nodes n
  JOIN source_documents sd ON sd.node_id = n.id
  WHERE sd.doc_id = 'notes_search'
  ORDER BY n.node_type, n.label
" --table
```

**All relation types and how often each is used:**
```bash
sqlite-utils query ontology.db "
  SELECT rel_type, COUNT(*) AS count
  FROM relations
  GROUP BY rel_type
  ORDER BY count DESC
" --table
```

**Referential integrity check (broken references):**
```bash
sqlite-utils query ontology.db "
  SELECT r.source_id, r.target_id, r.rel_type
  FROM relations r
  LEFT JOIN nodes ns ON ns.id = r.source_id
  LEFT JOIN nodes nt ON nt.id = r.target_id
  WHERE ns.id IS NULL OR nt.id IS NULL
" --table
```
No rows = all references valid.

---

## Presenting Results

- For small result sets (< 20 rows), display as a markdown table with the most useful columns.
- For large result sets, summarise counts and show a representative sample.
- Always include the `note` field when showing individual relations — it explains *why* the relation holds.
- When the user asks about a concept, show its description, module, and a count of its relations by type as a quick orientation before listing the edges.
