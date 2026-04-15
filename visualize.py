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
