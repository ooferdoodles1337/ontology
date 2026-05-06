# Subskill: Build Connections

**Purpose:** Using the full parsed text already in context (from the extract-vocabulary phase),
identify every relationship between nodes and append them to `knowledge-base/relations.yaml`.
This subskill also includes all query patterns needed to interrogate the existing graph before
writing — so you can avoid duplicates and anchor new edges to real node IDs.

---

## Step 1 — Orient yourself in the existing graph

Before writing a single relation, query the database to understand what already exists for
the nodes you are about to connect. The database was rebuilt after vocabulary extraction, so
it reflects the current full node set.

Run queries using:
```bash
uv run python -c "
import sqlite3
conn = sqlite3.connect('ontology.db')
cur = conn.cursor()
cur.execute(\"\"\"YOUR SQL HERE\"\"\")
for row in cur.fetchall(): print(row)
conn.close()
"
```

**Useful pre-flight queries:**

Get all nodes introduced by this document (to know your working set):
```sql
SELECT n.id, n.label, n.node_type
FROM nodes n
JOIN source_documents sd ON sd.node_id = n.id
WHERE sd.doc_id = '<doc_id>'
ORDER BY n.node_type, n.label
```

Check whether a relation already exists before adding it:
```sql
SELECT rel_type, note FROM relations
WHERE (source_id = 'a' AND target_id = 'b')
   OR (source_id = 'b' AND target_id = 'a')
```

Get all existing relations for a node (so you don't duplicate):
```sql
SELECT rel_type, source_id, target_id
FROM relations
WHERE source_id = 'node_id' OR target_id = 'node_id'
```

Get all node IDs (to validate that source/target exist before writing):
```sql
SELECT id FROM nodes ORDER BY id
```

---

## Step 2 — Identify relationships from the text

Re-read the document text. For each pair of nodes where the text:
- **explicitly states** that one is a type of another → `IS-A`
- **explicitly states** that one is a component of another → `PART-OF`
- **explicitly states** that one produces or leads to another → `CAUSES`
- **explicitly contrasts** two concepts along a shared dimension → `CONTRASTS-WITH`
- **uses a concrete case to illustrate** an abstract concept → `EXAMPLE-OF`
- **states that understanding one requires** prior understanding of another → `REQUIRES`
- **attributes a concept to** a researcher or institution → `ATTRIBUTED-TO`

…create a candidate relation. Do not invent relations that go beyond what the text supports.

**Relation type quick reference:**

| Type | Direction | Key test |
|------|-----------|----------|
| `IS-A` | specific → general | "A is a kind/type/form of B" |
| `PART-OF` | component → whole | "A is a component/element of B" |
| `CAUSES` | cause → effect | "A leads to / produces / results in B" |
| `CONTRASTS-WITH` | write once, most prominent direction | "A vs B", "unlike A, B…" |
| `EXAMPLE-OF` | instance → abstraction | "A is an example/case/illustration of B" |
| `REQUIRES` | dependent → prerequisite | "to understand A you need B", "A assumes B" |
| `ATTRIBUTED-TO` | concept → person/institution | "A was developed/proposed by B" |

---

## Step 3 — Verify node IDs

Before writing any relation, confirm both `source` and `target` are real node IDs in the
database. A quick check:

```bash
uv run python -c "
import sqlite3
conn = sqlite3.connect('ontology.db')
cur = conn.cursor()
cur.execute('SELECT id FROM nodes')
ids = {r[0] for r in cur.fetchall()}
candidates = [
    ('source_id_1', 'target_id_1'),
    # … your candidates …
]
for s, t in candidates:
    if s not in ids: print(f'MISSING source: {s}')
    if t not in ids: print(f'MISSING target: {t}')
conn.close()
"
```

If either ID is missing, either fix the ID spelling or add the node in the vocabulary files
first (then rebuild the DB) before writing the relation.

---

## Step 4 — Append relations to `relations.yaml`

Add a clearly labelled block at the end of `knowledge-base/relations.yaml`:

```yaml
  # =========================================================
  # <MODULE N>: <Document Title>
  # =========================================================

  # --- IS-A ---
  - type: IS-A
    source: child_concept
    target: parent_concept
    note: >
      One or two sentences explaining why this relation holds,
      citing the text where possible.

  # --- PART-OF ---
  - type: PART-OF
    source: component
    target: whole
    note: >
      Explanation.

  # --- (continue for each type used) ---
```

Group relations by type within the block. Every relation must have a non-empty `note`.

---

## Step 5 — Validate YAML and referential integrity

```bash
# YAML parse check
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/relations.yaml'))" && echo "YAML OK"

# Referential integrity
uv run python -c "
import yaml, sys
ont = yaml.safe_load(open('ontology.yaml'))
ids = {e['id'] for section in ['concepts','people_and_institutions','examples_and_metaphors']
       for e in ont.get(section, [])}
rels = yaml.safe_load(open('knowledge-base/relations.yaml'))
bad = [(r['source'], r['target'], r['type']) for r in rels.get('relations', [])
       if r.get('source') not in ids or r.get('target') not in ids]
if bad:
    for b in bad: print('BROKEN:', b)
    sys.exit(1)
else:
    print(f'All {len(rels[\"relations\"])} relations valid')
"
```

Fix any errors before returning control to the parent skill.
