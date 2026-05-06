---
name: query-ontology
description: >
  Query the ontology SQLite database (ontology.db) to answer questions about concepts,
  people, examples, relations, and modules in the FAB 2026 concept graph. Use this skill
  whenever the user asks anything about what's in the ontology — "what concepts are in
  module 3?", "show me everything related to reinforcement learning", "who are the people
  in the graph?", "what does X require?", "find examples of Y", "how are X and Y connected?"
  — even if they don't say "database" or "query". Any lookup or exploration of ontology
  content should use this skill.
---

# Querying the Ontology Database

The ontology is stored in `ontology.db` (project root) as a SQLite database.
Since `sqlite3` CLI may not be installed, always run queries via Python.

**Before every query, ensure the DB is fresh:**

```bash
uv run python -c "
import os, pathlib
root = pathlib.Path('.')
db = root / 'ontology.db'
yamls = [root / 'ontology.yaml',
         root / 'knowledge-base' / 'relations.yaml',
         root / 'knowledge-base' / 'metadata.yaml']
if not db.exists() or any(y.stat().st_mtime > db.stat().st_mtime for y in yamls if y.exists()):
    print('DB stale — rebuilding...')
    import subprocess; subprocess.run(['uv', 'run', 'python', 'scripts/build_db.py'], check=True)
else:
    print('DB is fresh.')
"
```

Then run your query:

```bash
uv run python -c "
import sqlite3
conn = sqlite3.connect('ontology.db')
cur = conn.cursor()
cur.execute(\"\"\"YOUR SQL HERE\"\"\")
for row in cur.fetchall():
    print(row)
conn.close()
"
```

## Schema

```sql
nodes (
    id           TEXT PRIMARY KEY,   -- snake_case identifier
    label        TEXT,               -- human-readable name
    description  TEXT,               -- one-sentence definition
    node_type    TEXT,               -- 'concept' | 'person' | 'institution' | 'example'
    module       INTEGER,            -- 1–6 (concepts only)
    tags         TEXT,               -- JSON array as string
    person_type  TEXT,               -- 'person' | 'institution' (people only)
    era          TEXT,               -- e.g. "1950s–1970s" (people only)
    affiliation  TEXT,               -- university/org (people only)
    example_source TEXT              -- citation (examples only)
)

relations (
    id         INTEGER PRIMARY KEY,
    rel_type   TEXT,     -- IS-A | PART-OF | CAUSES | CONTRASTS-WITH | EXAMPLE-OF | REQUIRES | ATTRIBUTED-TO
    source_id  TEXT,     -- REFERENCES nodes(id)
    target_id  TEXT,     -- REFERENCES nodes(id)
    note       TEXT      -- explanation of why this relation holds
)

source_documents (
    node_id  TEXT,
    doc_id   TEXT
)
```

## Common Query Patterns

**Find a concept by keyword:**
```sql
SELECT id, label, module, description
FROM nodes
WHERE node_type = 'concept'
  AND (label LIKE '%keyword%' OR description LIKE '%keyword%')
```

**All concepts in a module:**
```sql
SELECT id, label, description
FROM nodes
WHERE node_type = 'concept' AND module = 3
ORDER BY label
```

**All relations for a node (both directions):**
```sql
SELECT r.rel_type, r.source_id, r.target_id, r.note
FROM relations r
WHERE r.source_id = 'node_id' OR r.target_id = 'node_id'
```

**Outgoing relations only (what does X cause/require/etc.):**
```sql
SELECT r.rel_type, n.label AS target_label, r.note
FROM relations r
JOIN nodes n ON n.id = r.target_id
WHERE r.source_id = 'node_id'
ORDER BY r.rel_type
```

**Incoming relations (what IS-A or PART-OF points to X):**
```sql
SELECT r.rel_type, n.label AS source_label, r.note
FROM relations r
JOIN nodes n ON n.id = r.source_id
WHERE r.target_id = 'node_id'
ORDER BY r.rel_type
```

**All people and institutions:**
```sql
SELECT id, label, person_type, era, affiliation, description
FROM nodes
WHERE node_type IN ('person', 'institution')
ORDER BY label
```

**Examples illustrating a concept:**
```sql
SELECT n.id, n.label, n.description
FROM relations r
JOIN nodes n ON n.id = r.source_id
WHERE r.rel_type = 'EXAMPLE-OF' AND r.target_id = 'concept_id'
```

**Path / connectivity — does a relation exist between two nodes?**
```sql
SELECT rel_type, note
FROM relations
WHERE (source_id = 'a' AND target_id = 'b')
   OR (source_id = 'b' AND target_id = 'a')
```

**Most-connected concepts (by degree):**
```sql
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
```

## Presenting Results

- For small result sets (< 20 rows), display as a clean markdown table with the most useful columns.
- For large result sets, summarise counts and show a representative sample.
- Always include the `note` field when showing individual relations — it explains *why* the relation holds.
- When the user asks about a concept, show its description, module, and a count of its relations by type as a quick orientation before listing the edges.
