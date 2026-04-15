# Relations Graph Visualizer — Design Spec
_2026-04-15_

## Summary

A single Python script (`visualize.py`) that reads `relations.yaml` and produces a self-contained `graph.html` file viewable in any browser with full interactivity.

## Architecture

One script, one output file. No server required.

- **Input:** `relations.yaml` (same directory)
- **Output:** `graph.html` (same directory)
- **Dependencies:** `pyyaml`, `pyvis`

## Components

**Node construction** — All unique `source` and `target` IDs across all relations become nodes. Labels are IDs with underscores replaced by spaces. No separate read of `ontology.yaml` needed.

**Edge construction** — One directed edge per relation entry (`source → target`). Each edge is colored by relation type and carries the `note` text as a tooltip.

**Color scheme:**

| Type | Color |
|---|---|
| IS-A | `#4a90d9` (blue) |
| PART-OF | `#27ae60` (green) |
| CAUSES | `#e74c3c` (red) |
| CONTRASTS-WITH | `#e67e22` (orange) |
| EXAMPLE-OF | `#8e44ad` (purple) |
| REQUIRES | `#16a085` (teal) |

**Interactivity** — Provided by pyvis/vis.js out of the box: drag nodes, zoom, pan, hover tooltips on edges (shows note), physics simulation with toggle-able control panel.

## Usage

```bash
pip install pyvis pyyaml
python visualize.py
# opens graph.html in browser automatically (or open manually)
```

## Out of Scope

- Filtering by relation type or module (can be added later)
- Reading node metadata from `ontology.yaml`
- A web server or Streamlit UI
