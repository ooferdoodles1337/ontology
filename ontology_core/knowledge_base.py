"""Knowledge-base YAML accessors used by the local browser and scripts."""

from __future__ import annotations

from .paths import DOCUMENTS_YAML, NODES_YAML, RELATION_SCHEMA_YAML, RELATIONS_YAML
from .yaml_io import load_yaml, save_yaml

NODE_SECTIONS = [
    ("concepts", "concept"),
    ("people_and_institutions", "person"),
    ("examples_and_metaphors", "example"),
]


def load_documents() -> list[dict]:
    raw = load_yaml(DOCUMENTS_YAML)
    docs = list(raw.get("documents") or [])
    return sorted(docs, key=lambda doc: doc.get("course_order", 99))


def load_nodes() -> list[dict]:
    raw = load_yaml(NODES_YAML)
    nodes = []
    for section, type_label in NODE_SECTIONS:
        for node in raw.get(section) or []:
            nodes.append({**node, "_type": type_label})
    return nodes


def _section_for(node: dict) -> str:
    node_type = node.get("_type", "")
    if node_type == "person":
        return "people_and_institutions"
    if node_type == "example" or node.get("id", "").startswith("ex_"):
        return "examples_and_metaphors"
    return "concepts"


def _clean_node(node: dict) -> dict:
    return {key: value for key, value in node.items() if not key.startswith("_")}


def update_node(node_id: str, updated: dict) -> bool:
    raw = load_yaml(NODES_YAML)
    clean = _clean_node(updated)
    for section, _ in NODE_SECTIONS:
        nodes = raw.get(section) or []
        for index, node in enumerate(nodes):
            if node["id"] == node_id:
                nodes[index] = clean
                raw[section] = nodes
                save_yaml(NODES_YAML, raw)
                return True
    return False


def insert_node(node: dict) -> str | None:
    raw = load_yaml(NODES_YAML)
    node_id = node.get("id", "")
    for section, _ in NODE_SECTIONS:
        if any(existing["id"] == node_id for existing in raw.get(section) or []):
            return "duplicate id"

    section = _section_for(node)
    raw.setdefault(section, []).append(_clean_node(node))
    save_yaml(NODES_YAML, raw)
    return None


def remove_node(node_id: str) -> bool:
    raw = load_yaml(NODES_YAML)
    for section, _ in NODE_SECTIONS:
        nodes = raw.get(section) or []
        kept = [node for node in nodes if node["id"] != node_id]
        if len(kept) < len(nodes):
            raw[section] = kept
            save_yaml(NODES_YAML, raw)
            return True
    return False


def load_relations() -> list[dict]:
    raw = load_yaml(RELATIONS_YAML)
    return list(raw.get("relations") or [])


def save_relations(relations: list[dict]) -> None:
    raw = load_yaml(RELATIONS_YAML)
    raw["relations"] = relations
    save_yaml(RELATIONS_YAML, raw)


def load_schema() -> list[dict]:
    raw = load_yaml(RELATION_SCHEMA_YAML)
    return list(raw.get("relation_types") or [])

