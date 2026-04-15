import yaml
from pathlib import Path

RELATIONS_YAML = Path(__file__).parent.parent / "relations.yaml"


def load_relations():
    with open(RELATIONS_YAML) as f:
        data = yaml.safe_load(f)
    return data["relations"]


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
