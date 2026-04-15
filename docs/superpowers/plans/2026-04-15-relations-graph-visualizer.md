# Relations Graph Visualizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single `visualize.py` script that reads `relations.yaml` and writes a self-contained, interactive `graph.html` viewable in any browser.

**Architecture:** Parse YAML → extract unique nodes from all source/target IDs → build directed pyvis network with color-coded edges by relation type → write HTML. No server needed; the output file is fully self-contained.

**Tech Stack:** Python 3, `pyyaml`, `pyvis`

---

## File Structure

- Create: `visualize.py` — entry point; parsing, graph construction, HTML output
- Create: `tests/test_visualize.py` — unit tests for parsing and graph-building logic

---

### Task 1: Install dependencies and scaffold test file

**Files:**
- Create: `tests/test_visualize.py`

- [ ] **Step 1: Install dependencies**

```bash
pip install pyyaml pyvis
```

Expected: Both packages install without error.

- [ ] **Step 2: Create the test file**

Create `tests/test_visualize.py` with this content:

```python
import pytest
import yaml
from pathlib import Path

RELATIONS_YAML = Path(__file__).parent.parent / "relations.yaml"


def load_relations():
    with open(RELATIONS_YAML) as f:
        data = yaml.safe_load(f)
    return data["relations"]
```

- [ ] **Step 3: Verify the test file imports cleanly**

```bash
cd /home/ooferdoodles/projects/ontology
python -m pytest tests/test_visualize.py --collect-only
```

Expected: `no tests ran` (no test functions yet, but no import errors).

---

### Task 2: Implement and test node extraction

**Files:**
- Create: `visualize.py` (initial scaffold with `extract_nodes`)
- Modify: `tests/test_visualize.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_visualize.py`:

```python
def test_extract_nodes_returns_all_unique_ids():
    from visualize import extract_nodes
    relations = [
        {"type": "IS-A", "source": "reinforcement_learning", "target": "learning"},
        {"type": "IS-A", "source": "delayed_feedback", "target": "feedback"},
        {"type": "PART-OF", "source": "feedback", "target": "credit_assignment"},
    ]
    nodes = extract_nodes(relations)
    assert nodes == {
        "reinforcement_learning",
        "learning",
        "delayed_feedback",
        "feedback",
        "credit_assignment",
    }


def test_extract_nodes_deduplicates():
    from visualize import extract_nodes
    relations = [
        {"type": "IS-A", "source": "a", "target": "b"},
        {"type": "CAUSES", "source": "a", "target": "c"},
    ]
    nodes = extract_nodes(relations)
    assert nodes == {"a", "b", "c"}
```

- [ ] **Step 2: Run to verify it fails**

```bash
python -m pytest tests/test_visualize.py -v
```

Expected: `ImportError: cannot import name 'extract_nodes'`

- [ ] **Step 3: Create `visualize.py` with `extract_nodes`**

Create `visualize.py`:

```python
import yaml
from pathlib import Path
from pyvis.network import Network


EDGE_COLORS = {
    "IS-A":           "#4a90d9",  # blue
    "PART-OF":        "#27ae60",  # green
    "CAUSES":         "#e74c3c",  # red
    "CONTRASTS-WITH": "#e67e22",  # orange
    "EXAMPLE-OF":     "#8e44ad",  # purple
    "REQUIRES":       "#16a085",  # teal
}


def extract_nodes(relations: list[dict]) -> set[str]:
    """Return all unique node IDs referenced in relations."""
    nodes = set()
    for rel in relations:
        nodes.add(rel["source"])
        nodes.add(rel["target"])
    return nodes
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_visualize.py -v
```

Expected: Both `test_extract_nodes_*` tests PASS.

- [ ] **Step 5: Commit**

```bash
git add visualize.py tests/test_visualize.py
git commit -m "feat: scaffold visualize.py with extract_nodes and tests"
```

---

### Task 3: Implement and test edge color lookup

**Files:**
- Modify: `tests/test_visualize.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_visualize.py`:

```python
def test_edge_color_known_types():
    from visualize import EDGE_COLORS
    for t in ["IS-A", "PART-OF", "CAUSES", "CONTRASTS-WITH", "EXAMPLE-OF", "REQUIRES"]:
        assert t in EDGE_COLORS, f"Missing color for relation type: {t}"
        assert EDGE_COLORS[t].startswith("#"), f"Color should be a hex code, got: {EDGE_COLORS[t]}"


def test_edge_color_unknown_type_falls_back():
    from visualize import get_edge_color
    assert get_edge_color("UNKNOWN") == "#999999"


def test_edge_color_known_type_returns_correct_color():
    from visualize import get_edge_color
    assert get_edge_color("IS-A") == "#4a90d9"
    assert get_edge_color("CAUSES") == "#e74c3c"
```

- [ ] **Step 2: Run to verify it fails**

```bash
python -m pytest tests/test_visualize.py -v
```

Expected: `ImportError: cannot import name 'get_edge_color'`

- [ ] **Step 3: Add `get_edge_color` to `visualize.py`**

Add after the `EDGE_COLORS` dict in `visualize.py`:

```python
def get_edge_color(relation_type: str) -> str:
    """Return hex color for a relation type, falling back to grey."""
    return EDGE_COLORS.get(relation_type, "#999999")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_visualize.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add visualize.py tests/test_visualize.py
git commit -m "feat: add get_edge_color with fallback and tests"
```

---

### Task 4: Implement `build_graph` and wire up `main`

**Files:**
- Modify: `visualize.py`
- Modify: `tests/test_visualize.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_visualize.py`:

```python
def test_build_graph_has_correct_node_count():
    from visualize import build_graph
    relations = [
        {"type": "IS-A", "source": "a", "target": "b", "note": None},
        {"type": "CAUSES", "source": "b", "target": "c", "note": "b causes c"},
    ]
    net = build_graph(relations)
    assert len(net.nodes) == 3


def test_build_graph_has_correct_edge_count():
    from visualize import build_graph
    relations = [
        {"type": "IS-A", "source": "a", "target": "b", "note": None},
        {"type": "CAUSES", "source": "b", "target": "c", "note": "b causes c"},
    ]
    net = build_graph(relations)
    assert len(net.edges) == 2


def test_build_graph_node_label_replaces_underscores():
    from visualize import build_graph
    relations = [
        {"type": "IS-A", "source": "hill_climbing", "target": "informed_search", "note": None},
    ]
    net = build_graph(relations)
    labels = {n["label"] for n in net.nodes}
    assert "hill climbing" in labels
    assert "informed search" in labels
```

- [ ] **Step 2: Run to verify it fails**

```bash
python -m pytest tests/test_visualize.py -v
```

Expected: `ImportError: cannot import name 'build_graph'`

- [ ] **Step 3: Add `build_graph` and `main` to `visualize.py`**

Append to `visualize.py`:

```python
def build_graph(relations: list[dict]) -> Network:
    """Build a pyvis Network from a list of relation dicts."""
    net = Network(
        height="100vh",
        width="100%",
        directed=True,
        bgcolor="#1a1a2e",
        font_color="#e0e0e0",
        notebook=False,
    )
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=120)

    for node_id in extract_nodes(relations):
        net.add_node(
            node_id,
            label=node_id.replace("_", " "),
            title=node_id,
            color="#4a4a8a",
            size=16,
            font={"size": 12},
        )

    for rel in relations:
        note = rel.get("note") or ""
        color = get_edge_color(rel["type"])
        net.add_edge(
            rel["source"],
            rel["target"],
            title=f"[{rel['type']}] {note.strip()}",
            color=color,
            label=rel["type"],
            font={"size": 9, "color": color},
            arrows="to",
        )

    return net


def main():
    relations_path = Path(__file__).parent / "relations.yaml"
    output_path = Path(__file__).parent / "graph.html"

    with open(relations_path) as f:
        data = yaml.safe_load(f)

    relations = data.get("relations") or []
    net = build_graph(relations)
    net.show_buttons(filter_=["physics"])
    net.write_html(str(output_path))
    print(f"Graph written to {output_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
python -m pytest tests/test_visualize.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Run the script and open the output**

```bash
python visualize.py
```

Expected output: `Graph written to /home/ooferdoodles/projects/ontology/graph.html`

Open `graph.html` in a browser and verify:
- Graph renders with nodes and colored edges
- Dragging nodes works
- Hovering edges shows the relation type and note
- Physics control panel appears

- [ ] **Step 6: Commit**

```bash
git add visualize.py tests/test_visualize.py
git commit -m "feat: add build_graph, main; completes graph visualizer"
```

---

## Self-Review

**Spec coverage:**
- ✅ Reads `relations.yaml`
- ✅ Nodes derived from all unique source/target IDs
- ✅ Labels use spaces instead of underscores
- ✅ Edges colored by relation type with the specified hex colors
- ✅ Tooltips on hover (edge shows `[TYPE] note`)
- ✅ Interactive: drag, zoom, pan, physics panel
- ✅ Output is self-contained `graph.html`
- ✅ Usage: `pip install pyvis pyyaml && python visualize.py`

**Placeholder scan:** None found.

**Type consistency:** `extract_nodes` returns `set[str]`, used in `build_graph` with `for node_id in extract_nodes(relations)` — consistent. `get_edge_color` returns `str`, used as `color=` kwarg — consistent. `build_graph` returns `Network`, used in `main` as `net` — consistent.
