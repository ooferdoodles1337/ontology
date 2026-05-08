# Ontology Maintenance Instructions

> **`.agents/` is the primary source of truth** — all settings, skills, and configuration live here.
> **`.claude/` is a symlink to `.agents/`** for tool compatibility. Do not edit `.claude/` directly; make all changes in `.agents/`.

This project builds a concept graph for a course (FAB 2026). The graph is stored in YAML files and a SQLite database (`ontology.db`).

---

## Operating Modes

There are two operating modes. **User mode is the default.**

### User mode (default)

In user mode you may:
- Query the ontology and RAG index to answer course questions.
- Ingest new course-note documents (add nodes, relations, rebuild the DB).
- Write or update entries in `knowledge-base/*.yaml`.
- Run validation and DB-rebuild scripts.

In user mode you may **not**:
- Edit skills (`.agents/skills/`).
- Edit system instructions (`AGENTS.md`, `CLAUDE.md`).
- Edit agent settings (`settings.json`, `settings.local.json`).
- Create, rename, or delete skill files or configuration files.

### Dev mode

Dev mode is for actively developing or changing the system itself. In dev mode all of the above restrictions are lifted and you may edit skills, instructions, and configuration freely.

**To enter dev mode**, the user must explicitly say so — e.g. *"switch to dev mode"* or *"we're in dev mode now"*. Until that signal is given, stay in user mode and decline requests that would modify system files.

---

## File Roles

| File | Purpose |
|------|---------|
| `knowledge-base/documents.yaml` | Source-document registry: canonical `doc_id`, title, path, aliases, and course order for course notes. |
| `knowledge-base/nodes.yaml` | All nodes (concepts, people, examples) with their metadata. Single source of truth for vocabulary and node descriptions. |
| `knowledge-base/relations.yaml` | Relation instances — every edge in the graph with source, target, type, and note. |
| `knowledge-base/relation-schema.yaml` | The evolving vocabulary of relation types. Read before extracting relations; update after coining new types. |
| `docs/course-notes/` | Source documents to extract from. |
| `.rag/manifests/*.sections.json` | Durable RAG section-boundary manifests. Draft mechanically, then review before indexing. |
| `.rag/reviews/*.section-review.md` | LLM-facing packets for checking and repairing section boundaries. |

---

## Question Routing: RAG vs SQLite vs Source Documents

Before answering a course or ontology question, decide which evidence source fits the question.
Use the smallest source that can answer accurately, and combine sources when useful.

### Use RAG for semantic course understanding

Use the local RAG index (`query-course-rag` skill or `uv run python scripts/rag.py query ...`) when the user asks:

- what the course "means by" a concept, theory, example, or phrase;
- for a fuzzy comparison or explanation across notes;
- for semantically relevant passages, examples, or source-backed interpretation;
- questions where the wording may not exactly match node IDs or relation types.

RAG results are retrieval context, not the final answer. Ground the response in retrieved chunks
and graph expansion, and say when retrieval looks weak or incomplete.

### Use SQLite for exact ontology lookups

Use the ontology database when the question is exact, structural, or countable:

- list nodes, relations, people, examples, or documents;
- find all edges for a node, relation type, or document;
- count entries, detect duplicates, validate IDs, or check schema coverage;
- answer "what is connected to X?" or "does relation Y exist?"

Use `sqlite-utils query ontology.db "..." --table` for DB inspection. Do not write inline Python
scripts to query SQLite.

### Read source documents or YAML directly for precision

Read the source PDF/text/YAML directly when:

- the user asks for exact wording, quotes, page-level evidence, or section boundaries;
- RAG returns weak, contradictory, stale, or overly truncated context;
- the document is new or likely not indexed yet;
- extracting vocabulary or relations for ingestion;
- the question is about repository configuration, scripts, or YAML contents rather than course meaning.

When extracting ontology updates from course notes, follow the one-document-at-a-time rule:
read one source document, update the relevant YAML, rebuild/validate, then move on.

### Default sequence for ambiguous questions

1. If it is a natural-language course question, start with RAG.
2. If the answer depends on exact graph facts, verify with SQLite.
3. If exact quotes, full context, or ingestion-quality evidence are needed, read the source document.
4. If the question is about code or file structure, read the relevant files directly.

---

## RAG Chunking Workflow

PDF section extraction is heuristic and can be fragile when formatting changes. Treat generated
section boundaries as drafts, not unquestioned truth.

When adding or changing course-note PDFs:

1. Draft or refresh section manifests:
   ```bash
   uv run python scripts/rag.py sections --write
   ```
2. Generate LLM review packets:
   ```bash
   uv run python scripts/rag.py review-sections --write
   ```
3. Read the relevant `.rag/reviews/*.section-review.md` packet and check whether chunks are
   semantically coherent. If needed, edit the matching `.rag/manifests/*.sections.json` file.
4. Rebuild the index only after the manifest review pass:
   ```bash
   uv run python scripts/rag.py index
   ```

Use `--doc-id notes_krr` with `review-sections` to review a single document. Use `--redraft`
only when you specifically want to compare against fresh heuristic boundaries.

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

Before Step 1, add or update the document's canonical `doc_id`, title, path, aliases, and course order
in `knowledge-base/documents.yaml`.

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
  uv run python -c "import yaml; yaml.safe_load(open('knowledge-base/documents.yaml'))"
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
