# FAB 2026 Ontology

Course ontology for FAB Spring 2026. Concepts, relations, and an interactive graph visualizer.

## Files

- `ontology.yaml` — node vocabulary (concepts, people, examples)
- `relations.yaml` — directed relations between nodes (IS-A, PART-OF, CAUSES, CONTRASTS-WITH, EXAMPLE-OF, REQUIRES)

## Graph Visualizer

Generates an interactive `graph.html` from `relations.yaml`.

```bash
uv venv .venv
uv pip install pyyaml pyvis
uv run python visualize.py
# open graph.html in your browser
```

Edges are color-coded by relation type. Hover an edge to see its note. Drag, zoom, and pan to explore.
