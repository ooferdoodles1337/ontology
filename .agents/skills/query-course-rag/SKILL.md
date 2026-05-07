---
name: query-course-rag
description: >
  Use the local LlamaIndex/Chroma RAG index to answer natural-language questions
  about the FAB 2026 course notes and ontology. Use this skill whenever the user
  asks what the course says about a concept, wants semantically relevant source
  passages, asks fuzzy questions across PDFs and ontology relations, mentions
  RAG/vector search/semantic search, or asks for evidence from course notes. For
  exact graph/table lookups, the ontology DB is useful; for natural-language
  course understanding, this RAG skill should be used.
---

# Querying Course RAG

This project has a local RAG CLI at `scripts/rag.py`. It indexes:

- PDF course-note chunks, where one chunk is one logical numbered section.
- Ontology node chunks from `knowledge-base/nodes.yaml`.
- Ontology relation chunks from `knowledge-base/relations.yaml`.

The vector store is local Chroma under `.rag/chroma`, using
`jinaai/jina-embeddings-v5-text-nano` through LlamaIndex's HuggingFace embedding
adapter. Query results also include SQLite graph expansion around retrieved node
and relation IDs.

## Before Querying

The default query output is compact LLM-facing context. It preserves the useful
metadata, excerpts, and graph facts without JSON scaffolding:

```bash
uv run python scripts/rag.py query "How does search relate to credit assignment?"
```

Use JSON only when you need complete raw metadata or programmatic post-processing:

```bash
uv run python scripts/rag.py query "How does search relate to credit assignment?" --format json
```

If the command reports that the collection is empty, build the index:

```bash
uv run python scripts/rag.py index
```

If the user is asking about chunk quality, section boundaries, or newly added
PDFs, draft section manifests first:

```bash
uv run python scripts/rag.py sections --write
```

Then generate LLM review packets. Read the relevant packet in `.rag/reviews/`,
check whether section starts/ends are semantically coherent, and edit the
target `.rag/manifests/*.sections.json` if the packet reveals bad boundaries:

```bash
uv run python scripts/rag.py review-sections --write
```

For a single document:

```bash
uv run python scripts/rag.py review-sections --doc-id notes_krr --write
```

After the checking pass and any manifest edits, rebuild:

```bash
uv run python scripts/rag.py index
```

## How To Use Results

Read the returned RAG output as retrieval context, not as a final answer. The important
fields or lines are:

- `Retrieved context`: semantically relevant chunks with `kind`, score, IDs, citations, and excerpts.
- `Graph facts`: exact SQLite relations adjacent to retrieved or query-matched nodes.
- `metadata.source_path`, `doc_id`, `section_title`, and page fields for citations.

When answering the user:

- Ground claims in retrieved chunks and graph expansion.
- Mention section titles, page ranges, node IDs, or relation triples when useful.
- Do not invent ontology relations that are absent from `graph_expansion` or retrieved relation chunks.
- If retrieval looks weak or off-topic, say so and run a narrower query.

## Useful Commands

Retrieve more context:

```bash
uv run python scripts/rag.py query "interactionist critique of symbolic AI" --top-k 12
```

Limit very long chunks in terminal output:

```bash
uv run python scripts/rag.py query "frame problem" --excerpt-chars 500
```

Retrieve only vector context, without graph expansion:

```bash
uv run python scripts/rag.py query "Moravec paradox" --no-graph
```

Inspect section boundaries:

```bash
uv run python scripts/rag.py sections
```

Generate an LLM-facing section-boundary review packet:

```bash
uv run python scripts/rag.py review-sections --doc-id notes_krr
```
