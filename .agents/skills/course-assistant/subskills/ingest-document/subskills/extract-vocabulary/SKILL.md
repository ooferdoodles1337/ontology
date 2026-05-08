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
to disk — it forces explicit justification and makes it easy to catch duplicates.

**Worked example** — given this passage:

> "Founders of AI referred to this general problem of intelligence as that of learning to assign credit (Samuel 1959; Minsky 1961). **Credit assignment** refers to any process for evaluating effects of individual actions on solving a problem. […] all three examples involved (1) **goal-directed agents** who (2) generated **actions** (3) tested effects on **goals** using (4) **trial-and-error feedback**, and used this to (5) **modify** actions. […] Samuel called the evaluation of such proxies the use of **'intermediate feedback'** to assign credit."

The extraction table would be:

| Candidate ID | Type | Why extracted |
|---|---|---|
| `credit_assignment` | concept | Central term, explicitly defined |
| `goal_directed_agents` | concept | Explicitly listed as a structural building block |
| `actions` | concept | Explicitly listed — the things agents generate and test |
| `goals` | concept | Explicitly listed — criteria against which actions are evaluated |
| `trial_and_error_feedback` | concept | Explicitly listed — the feedback mechanism |
| `interdependence_of_actions` | concept | Named as the fundamental challenge |
| `delayed_feedback` | concept | Named as a key difficulty |
| `ambiguous_feedback` | concept | Named as a key difficulty |
| `intermediate_feedback` | concept | Named explicitly with a definition (Samuel's term) |
| `arthur_samuel` | person | Named as the IBM scientist who first described the solution |
| `ex_checkers_game` | example | Concrete case used to illustrate intermediate feedback |

Note what was *not* extracted: "IBM" (only Arthur Samuel's employer, not load-bearing);
"number of pieces" (a detail inside the checkers example, not a standalone concept).

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
