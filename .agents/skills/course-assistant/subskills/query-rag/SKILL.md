# Subskill: Query Course RAG

Use this subskill for natural-language questions about what the course means, fuzzy
comparisons across notes, requests for source passages, and any question where exact
ID matching would miss relevant content.

The local RAG CLI at `scripts/rag.py` indexes:
- PDF course-note chunks (one chunk = one logical numbered section)
- Ontology node chunks from `knowledge-base/nodes.yaml`
- Ontology relation chunks from `knowledge-base/relations.yaml`

Vector store: local Chroma under `.rag/chroma`.

---

## Basic Query

```bash
uv run python scripts/rag.py query "How does search relate to credit assignment?"
```

Use `--format json` only when you need raw metadata for programmatic post-processing.

If the collection is empty, build the index first:
```bash
uv run python scripts/rag.py index
```

---

## Useful Options

```bash
# Retrieve more context
uv run python scripts/rag.py query "interactionist critique of symbolic AI" --top-k 12

# Limit long chunk output
uv run python scripts/rag.py query "frame problem" --excerpt-chars 500

# Vector context only, skip graph expansion
uv run python scripts/rag.py query "Moravec paradox" --no-graph
```

---

## How to Use Results

RAG output is retrieval context, not a final answer.

Key fields to read:
- **Retrieved context** — semantically relevant chunks with `kind`, score, IDs, citations, and excerpts
- **Graph facts** — exact SQLite relations adjacent to retrieved or query-matched nodes
- `metadata.source_path`, `doc_id`, `section_title`, page fields — for citations

When answering:
- Ground claims in retrieved chunks and graph expansion
- Mention section titles, page ranges, node IDs, or relation triples when useful
- Do not invent ontology relations absent from `graph_expansion` or retrieved chunks
- If retrieval looks weak or off-topic, say so and run a narrower query

---

## Index Maintenance

When a course-note PDF is new or recently changed, refresh section manifests before indexing:

```bash
# 1. Draft section boundaries
uv run python scripts/rag.py sections --write

# 2. Generate LLM review packets
uv run python scripts/rag.py review-sections --write

# 3. Read the relevant .rag/reviews/*.section-review.md packet
#    Edit the matching .rag/manifests/*.sections.json if boundaries look wrong

# 4. Rebuild the index
uv run python scripts/rag.py index
```

For a single document:
```bash
uv run python scripts/rag.py review-sections --doc-id notes_krr --write
```

Use `--redraft` only when you specifically want fresh heuristic boundaries to compare against.
