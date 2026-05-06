# Subskill: Extract Vocabulary

**Purpose:** Parse the course note PDF with liteparse, then identify every new node that
does not yet exist in `ontology.yaml` and write it into both `ontology.yaml` and
`knowledge-base/metadata.yaml`.

---

## Step 1 — Parse the PDF

Use the `liteparse` skill to extract the full text of the target PDF. You need the *complete*
text, not a summary — every sentence may contain terminology worth capturing.

After parsing, hold the full text in context. Do not read a second document before finishing
this extraction pass.

---

## Step 2 — Load the existing vocabulary

Read `ontology.yaml` and collect every existing `id` into a set. This is your deduplication
guard: if a term already has an id in this set, do not add it again (even if the spelling
differs slightly — check for near-duplicates by label as well).

```bash
uv run python -c "
import yaml
ont = yaml.safe_load(open('ontology.yaml'))
ids = {e['id'] for section in ['concepts','people_and_institutions','examples_and_metaphors']
       for e in ont.get(section, [])}
print(f'{len(ids)} existing nodes')
"
```

---

## Step 3 — Extract new terms

Read through the full parsed text carefully. For each term produce a rationale table before
writing anything to disk — it forces explicit justification for each candidate and makes it
easy to catch duplicates or near-misses against the existing vocabulary:

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
- Passing mentions with no definition or explanatory role (e.g., "IBM" named only as an employer — not central to the argument)
- General-purpose words used in their everyday sense ("process", "effect", "problem")
- Specific details *inside* a larger example that don't stand alone as concepts (e.g., "number of pieces" within a checkers example — it's a detail, not a standalone node)

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

Note what was *not* extracted: "IBM" (only Arthur Samuel's employer, not load-bearing),
"number of pieces" (a detail inside the checkers example, not a standalone concept).

**ID conventions (enforce these strictly):**
- All IDs: `snake_case`, lowercase only
- Concepts: plain noun phrase — `credit_assignment`, `constraint_propagation`
- People / institutions: `firstname_lastname` or institution name — `herbert_simon`, `carnegie_mellon`
- Examples / metaphors: always prefixed `ex_` — `ex_checkers_game`, `ex_watchmaker_parable`

---

## Step 4 — Write new entries to `ontology.yaml`

Append new entries under the correct top-level section (`concepts`, `people_and_institutions`,
or `examples_and_metaphors`). Group them under a comment that names the source document:

```yaml
  # — <Module N>: <Document Title> —
  - id: new_concept_id
  - id: another_concept_id
```

Do not add relation instances to this file.

---

## Step 5 — Write metadata entries to `metadata.yaml`

For every new node, append a metadata entry to the correct section in
`knowledge-base/metadata.yaml`. Use these templates exactly:

**Concept:**
```yaml
- id: concept_name
  label: Human Readable Name
  description: >
    One or two sentences defining this concept in the context of the course.
  module: <N>
  tags: [optional, keywords]
  source_documents:
  - <doc_id>
```

**Person:**
```yaml
- id: firstname_lastname
  label: Full Name
  type: person
  era: "1950s–1970s"
  affiliation: University or Organisation Name
  description: >
    Brief bio focused on their contribution to topics in this course.
  source_documents:
  - <doc_id>
```

**Institution:**
```yaml
- id: institution_name
  label: Full Institution Name
  type: institution
  affiliation: City, Country
  description: >
    What this institution contributed to the topics in this course.
  source_documents:
  - <doc_id>
```

**Example / metaphor:**
```yaml
- id: ex_short_name
  label: Descriptive Example Name
  description: >
    What this example illustrates and how it is used in the text.
  source: "Author / Work / Year (if known)"
  illustrates: [concept_id_1, concept_id_2]
  source_documents:
  - <doc_id>
```

**Important:** If a node was introduced in an earlier document and you are now seeing it
again in a new document, do not create a duplicate entry — instead add the new `doc_id`
to its existing `source_documents` list in `metadata.yaml`.

---

## Step 6 — Verify YAML validity

```bash
uv run python -c "import yaml; yaml.safe_load(open('ontology.yaml'))" && echo "OK"
uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/metadata.yaml'))" && echo "OK"
```

Fix any parse errors before returning control to the parent skill.
