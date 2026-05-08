# Subskill: Extract Vocabulary

**Purpose:** Parse the course note PDF with liteparse, then identify every new node that
does not yet exist in `knowledge-base/nodes.yaml` and write it into that file.

---

## Step 1 — Parse the PDF

Use the `liteparse` skill to extract the full text of the target PDF. You need the *complete*
text, not a summary — every sentence may contain terminology worth capturing.

After parsing, hold the full text in context. Do not read a second document before finishing
this extraction pass.

---

## Step 2 — Load the existing vocabulary

Read `knowledge-base/nodes.yaml` and collect every existing `id` into a set. This is your
deduplication guard: if a term already has an id in this set, do not add it again (even if
the spelling differs slightly — check for near-duplicates by label as well).

```bash
sqlite-utils query ontology.db "SELECT id, label FROM nodes ORDER BY id" --table
```

---

## Step 3 — Extract new terms

Read through the full parsed text carefully. Produce a rationale table before writing anything
to disk — it forces explicit justification and makes it easy to catch duplicates:

| Candidate ID | Type | Why extracted |
|---|---|---|
| `intermediate_feedback` | concept | Named explicitly with a definition |
| `arthur_samuel` | person | Named as the originator of the idea |
| `ex_checkers_game` | example | Concrete case illustrating intermediate feedback |

**What to extract:**
- **Explicitly defined** terms ("credit assignment refers to…")
- **Core building blocks** the text lists as structural components of an argument
- **Named challenges or mechanisms** the text singles out by name
- **Named people or institutions** credited with a core idea
- **Concrete examples or metaphors** used to illustrate an abstract concept

**What to skip:**
- Passing mentions with no definition or explanatory role
- General-purpose words used in their everyday sense ("process", "effect", "problem")
- Specific details *inside* a larger example that don't stand alone as concepts

**ID conventions:**
- All IDs: `snake_case`, lowercase only
- Concepts: plain noun phrase — `credit_assignment`, `constraint_propagation`
- People / institutions: `firstname_lastname` or institution name — `herbert_simon`, `carnegie_mellon`
- Examples / metaphors: always prefixed `ex_` — `ex_checkers_game`, `ex_watchmaker_parable`

---

## Step 4 — Write new entries to `knowledge-base/nodes.yaml`

Append new entries under the correct top-level section. Group them with a comment naming
the source document. Do not add relation instances here.

**IMPORTANT — uniform schema rule:** Every node — concept, person, institution, or example —
uses exactly these four fields and no others:

```
id              snake_case identifier
label           Human-readable name
description     One or two sentences (block scalar style >)
source_documents  list of doc_id strings
```

Do not add `type`, `era`, `affiliation`, `source`, `illustrates`, `module`, or any other field.
Put information about affiliation, era, or what an example illustrates in the `description` text.

**Concept:**
```yaml
- id: concept_name
  label: Human Readable Name
  description: >
    One or two sentences defining this concept in the context of the course.
  source_documents:
  - <doc_id>
```

**Person or Institution:**
```yaml
- id: firstname_lastname
  label: Full Name
  description: >
    Brief bio or description including era, affiliation, and contribution to the course topics.
  source_documents:
  - <doc_id>
```

**Example / metaphor:**
```yaml
- id: ex_short_name
  label: Descriptive Example Name
  description: >
    What this example illustrates, how it is used in the text, and source/author if relevant.
  source_documents:
  - <doc_id>
```

**If a node was introduced in an earlier document** and appears again in this one, do not
create a duplicate — add the new `doc_id` to its existing `source_documents` list instead.

---

## Step 5 — Verify YAML validity

```bash
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/nodes.yaml'))" && echo "OK"
```

Fix any parse errors before returning control to the parent subskill.
