# Ontology Maintenance Instructions

This project builds a concept graph for a course (FAB 2026). The graph is stored in YAML files and rendered via `visualize.py`.

## File Roles

| File | Purpose |
|------|---------|
| `ontology.yaml` | Vocabulary — all node IDs (concepts, people, examples). No relation instances here. |
| `knowledge-base/relations.yaml` | Relation instances — every edge in the graph with source, target, type, and note. |
| `knowledge-base/metadata.yaml` | Human-readable metadata for every node: labels, descriptions, module numbers, and type-specific fields. |
| `docs/course-notes/` | Source documents to extract from. |

---

## Node ID Conventions

- Always `snake_case`, lowercase.
- Concepts: plain noun phrase — `credit_assignment`, `constraint_propagation`
- People / institutions: `firstname_lastname` or institution name — `herbert_simon`, `carnegie_mellon`
- Examples / metaphors: always prefixed with `ex_` — `ex_checkers_game`, `ex_watchmaker_parable_1000_parts`

---

## Relation Types

| Type | Meaning | Direction |
|------|---------|-----------|
| `IS-A` | A is a more specific version of B. A inherits B's properties. | A → B (specific → general) |
| `PART-OF` | A is a component that constitutes B. Removing A makes B incomplete. | A → B (part → whole) |
| `CAUSES` | A produces or gives rise to B as a consequence. | A → B (cause → effect) |
| `CONTRASTS-WITH` | A and B differ meaningfully along a shared dimension. Neither is fully defined without the other. | Bidirectional, but write once with the most prominent direction |
| `EXAMPLE-OF` | A is a concrete instantiation that illustrates abstract concept B. | A → B (instance → abstraction) |
| `REQUIRES` | A cannot be meaningfully understood without first understanding B. Epistemic dependency, not causal. | A → B (dependent → prerequisite) |

---

## Process: Adding a New Document

When one or more new documents are placed in `docs/`, follow these steps **strictly in order**.

### Step 1 — Extract new vocabulary (before touching any existing document)

Read the new document and collect every term that does not already appear as a node ID in `ontology.yaml`. Categorise each as:

- **concept** — an abstract idea, technique, mechanism, or phenomenon discussed in the course
- **person / institution** — a named researcher, organisation, or historical figure
- **example / metaphor** — a concrete case study, analogy, or illustrative scenario

Add all new entries to `ontology.yaml` under the correct section. Group them under a comment that names the module or document they came from. Do not add relation instances yet.

Format:
```yaml
# — Module N: <Title> —
- id: new_concept_id
- id: another_concept_id
```

Also add a corresponding metadata entry in `knowledge-base/metadata.yaml` for each new node (label, description, and type-specific fields). See **Entry Formats** below for templates.

Commit this vocabulary update before proceeding to Step 2.

---

### Step 2 — Extract relations, one document at a time

**CRITICAL RULE: Read exactly one source document, then immediately update `knowledge-base/relations.yaml`. Never read two or more documents before writing.**

For each document (working through them in module order):

1. Read the document in full.
2. Identify every relationship between nodes that is:
   - Explicitly stated in the text, OR
   - Strongly implied by the structure of the argument (e.g., a concept is introduced as a subtype, a prerequisite is listed, an example is walked through).
3. Append all new relations to `knowledge-base/relations.yaml` under a comment block that identifies the source document.
4. Save and verify the YAML is valid before moving to the next document.

Repeat for each remaining document.

---

## Entry Formats

### ontology.yaml — adding a concept
```yaml
- id: concept_name
```

### ontology.yaml — adding a person
```yaml
- id: firstname_lastname
```

### ontology.yaml — adding an example
```yaml
- id: ex_short_descriptive_name
```

### knowledge-base/relations.yaml — adding a relation
```yaml
- type: IS-A                      # one of the six types above
  source: child_concept
  target: parent_concept
  note: >
    One or two sentences explaining why this relation holds, citing
    the text if possible. This becomes the edge tooltip in the graph.
```

### knowledge-base/metadata.yaml — adding a concept entry
```yaml
- id: concept_name
  label: Human Readable Name
  description: >
    One or two sentences defining this concept.
  module: 3
  tags: [optional, keywords]
```

### knowledge-base/metadata.yaml — adding a person/institution entry
```yaml
- id: firstname_lastname
  label: Full Name
  type: person            # or: institution
  era: "1950s–1970s"
  affiliation: University Name
  description: >
    Brief bio or description of their contribution.
```

### knowledge-base/metadata.yaml — adding an example entry
```yaml
- id: ex_short_name
  label: Descriptive Example Name
  description: >
    What this example illustrates and how.
  source: "Author / Work / Year"
  illustrates: [concept_id_1, concept_id_2]
```

---

## Validation Checklist

Before finishing any update session, verify:

- [ ] Every `source` and `target` in `knowledge-base/relations.yaml` exists as an `id` in `ontology.yaml`.
- [ ] No duplicate relation entries (same type + source + target pair).
- [ ] All new node IDs follow `snake_case` and `ex_` prefix rules.
- [ ] Each relation has a non-empty `note`.
- [ ] New nodes added to `ontology.yaml` also have a corresponding entry in `knowledge-base/metadata.yaml`.
- [ ] YAML parses without error: `python -c "import yaml; yaml.safe_load(open('knowledge-base/relations.yaml'))"` and same for `ontology.yaml` and `knowledge-base/metadata.yaml`.
- [ ] Graph regenerates cleanly: `python visualize.py`

---

## What NOT to Do

- Do not invent relations that are not supported by the course documents.
- Do not add a node ID that is a near-duplicate of an existing one (check before adding).
- Do not read all documents first and then batch-write relations. Process one document, write, then move to the next.
- Do not modify `visualize.py` during an ontology update session.
