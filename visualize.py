import math
import yaml
from pathlib import Path
from pyvis.network import Network


NODE_COLORS = {
    "concepts":               "#4a7fc1",  # steel blue
    "people_and_institutions": "#c0392b",  # crimson
    "examples_and_metaphors":  "#2ecc71",  # emerald
    "unknown":                 "#7f8c8d",  # grey fallback
}

EDGE_COLORS = {
    "IS-A":           "#4a90d9",  # blue
    "PART-OF":        "#27ae60",  # green
    "CAUSES":         "#e74c3c",  # red
    "CONTRASTS-WITH": "#e67e22",  # orange
    "EXAMPLE-OF":     "#8e44ad",  # purple
    "REQUIRES":       "#16a085",  # teal
    "ATTRIBUTED-TO":  "#f39c12",  # amber
}


def extract_nodes(relations: list[dict]) -> set[str]:
    """Return all unique node IDs referenced in relations."""
    nodes = set()
    for rel in relations:
        nodes.add(rel["source"])
        nodes.add(rel["target"])
    return nodes


def compute_degrees(relations: list[dict]) -> dict[str, int]:
    """Count total connections (in + out) for each node."""
    degrees: dict[str, int] = {}
    for rel in relations:
        degrees[rel["source"]] = degrees.get(rel["source"], 0) + 1
        degrees[rel["target"]] = degrees.get(rel["target"], 0) + 1
    return degrees


def scale_size(degree: int, min_deg: int, max_deg: int, min_size: float = 10, max_size: float = 70) -> float:
    """Map a degree value onto [min_size, max_size] using a square-root curve
    so highly-connected nodes stand out dramatically."""
    if max_deg == min_deg:
        return (min_size + max_size) / 2
    t = (degree - min_deg) / (max_deg - min_deg)
    return min_size + math.sqrt(t) * (max_size - min_size)


def get_edge_color(relation_type: str) -> str:
    """Return hex color for a relation type, falling back to grey."""
    return EDGE_COLORS.get(relation_type, "#999999")


def build_node_type_map(ontology: dict) -> dict[str, str]:
    """Return {node_id: section_key} for every node in the ontology."""
    mapping: dict[str, str] = {}
    for section in ("concepts", "people_and_institutions", "examples_and_metaphors"):
        for entry in ontology.get(section, []):
            mapping[entry["id"]] = section
    return mapping


def build_metadata_map(metadata: dict) -> dict[str, dict]:
    """Return {node_id: metadata_entry} for every node in metadata.yaml."""
    mapping: dict[str, dict] = {}
    for section in ("concepts", "people_and_institutions", "examples_and_metaphors"):
        for entry in metadata.get(section, []):
            mapping[entry["id"]] = entry
    return mapping


def _node_tooltip(node_id: str, section: str, deg: int, meta: dict | None) -> str:
    """Build an HTML tooltip string for a node."""
    lines = []
    label = meta.get("label", node_id) if meta else node_id
    lines.append(f"<b>{label}</b>")

    if meta:
        desc = (meta.get("description") or "").strip().replace("\n", " ")
        if desc:
            lines.append(f"<i>{desc}</i>")

        if section == "people_and_institutions":
            era = meta.get("era", "")
            affil = meta.get("affiliation", "")
            kind = meta.get("type", "")
            parts = [p for p in (kind, era, affil) if p]
            if parts:
                lines.append(" · ".join(parts))

        module = meta.get("module")
        if module:
            lines.append(f"Module {module}")

        src_docs = meta.get("source_documents") or []
        if src_docs:
            lines.append(f"Sources: {', '.join(src_docs)}")

    lines.append(f"[{section}] · {deg} connection(s)")
    return "<br>".join(lines)


def build_graph(
    relations: list[dict],
    node_types: dict[str, str],
    metadata_map: dict[str, dict],
) -> Network:
    """Build a pyvis Network from a list of relation dicts."""
    net = Network(
        height="100vh",
        width="100%",
        directed=True,
        bgcolor="#1a1a2e",
        font_color="#e0e0e0",
        notebook=False,
    )
    net.barnes_hut(
        gravity=-6000,
        central_gravity=0.4,
        spring_length=120,
        spring_strength=0.05,
        damping=0.18,
    )
    net.options.physics.maxVelocity = 30
    net.options.physics.minVelocity = 0.5
    net.options.physics.stabilization.iterations = 300
    net.options.physics.stabilization.updateInterval = 25

    degrees = compute_degrees(relations)
    min_deg = min(degrees.values())
    max_deg = max(degrees.values())

    for node_id in extract_nodes(relations):
        deg = degrees.get(node_id, 1)
        size = scale_size(deg, min_deg, max_deg)
        font_size = 9 + int(size / 6)
        section = node_types.get(node_id, "unknown")
        color = NODE_COLORS[section]
        meta = metadata_map.get(node_id)
        display_label = meta.get("label", node_id) if meta else node_id.replace("_", " ")
        tooltip = _node_tooltip(node_id, section, deg, meta)
        net.add_node(
            node_id,
            label=display_label,
            title=tooltip,
            color=color,
            size=size,
            font={"size": font_size},
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
            arrows="to, from" if rel["type"] == "CONTRASTS-WITH" else "to",
        )

    return net


def main():
    base = Path(__file__).parent
    kb = base / "knowledge-base"
    relations_path = kb / "relations.yaml"
    metadata_path = kb / "metadata.yaml"
    ontology_path = base / "ontology.yaml"
    output_path = base / "graph.html"

    with open(relations_path) as f:
        data = yaml.safe_load(f)
    with open(ontology_path) as f:
        ontology = yaml.safe_load(f)
    with open(metadata_path) as f:
        metadata = yaml.safe_load(f)

    relations = data.get("relations") or []
    node_types = build_node_type_map(ontology)
    metadata_map = build_metadata_map(metadata)
    net = build_graph(relations, node_types, metadata_map)
    net.show_buttons(filter_=["physics"])
    net.write_html(str(output_path))
    print(f"Graph written to {output_path}")


if __name__ == "__main__":
    main()
