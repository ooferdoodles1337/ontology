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


def compute_degrees(relations: list[dict]) -> dict[str, int]:
    """Count total connections (in + out) for each node."""
    degrees: dict[str, int] = {}
    for rel in relations:
        degrees[rel["source"]] = degrees.get(rel["source"], 0) + 1
        degrees[rel["target"]] = degrees.get(rel["target"], 0) + 1
    return degrees


def scale_size(degree: int, min_deg: int, max_deg: int, min_size: float = 12, max_size: float = 40) -> float:
    """Map a degree value linearly onto [min_size, max_size]."""
    if max_deg == min_deg:
        return (min_size + max_size) / 2
    return min_size + (degree - min_deg) / (max_deg - min_deg) * (max_size - min_size)


def get_edge_color(relation_type: str) -> str:
    """Return hex color for a relation type, falling back to grey."""
    return EDGE_COLORS.get(relation_type, "#999999")


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
        font_size = 10 + int((size - 12) / 4)
        net.add_node(
            node_id,
            label=node_id.replace("_", " "),
            title=f"{node_id} (connections: {deg})",
            color="#4a4a8a",
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
