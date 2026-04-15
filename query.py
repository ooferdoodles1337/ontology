#!/usr/bin/env python3
"""
Declarative triple-pattern queries over the FAB 2026 ontology.

PATTERN QUERY  (any token can be '?' for wildcard)
    python query.py "? IS-A learning"
    python query.py "? ATTRIBUTED-TO herbert_simon"
    python query.py "reinforcement_learning ? ?"
    python query.py "? ? credit_assignment"

GRAPH TRAVERSAL
    python query.py --ancestors reinforcement_learning [TYPE]
    python query.py --descendants learning [TYPE]
    python query.py --neighborhood credit_assignment

NODE INFO
    python query.py --info reinforcement_learning
    python query.py --info herbert_simon

OPTIONS
    --full      Show full notes (default behavior now)
    --compact   Truncate notes to 90 chars

TYPE defaults to IS-A for traversal commands.
"""
import sys
import yaml
from pathlib import Path


BASE = Path(__file__).parent
KB = BASE / "knowledge-base"


def load():
    with open(KB / "relations.yaml") as f:
        return yaml.safe_load(f)["relations"]


def load_metadata() -> dict[str, dict]:
    """Return {node_id: metadata_entry} from knowledge-base/metadata.yaml."""
    path = KB / "metadata.yaml"
    if not path.exists():
        return {}
    with open(path) as f:
        data = yaml.safe_load(f)
    mapping: dict[str, dict] = {}
    for section in ("concepts", "people_and_institutions", "examples_and_metaphors"):
        for entry in (data or {}).get(section, []):
            mapping[entry["id"]] = {"_section": section, **entry}
    return mapping


def _match(pattern: str, value: str) -> bool:
    return pattern == "?" or pattern == value


def query_triples(relations, source_pat, type_pat, target_pat):
    return [
        r for r in relations
        if _match(source_pat, r["source"])
        and _match(type_pat, r["type"])
        and _match(target_pat, r["target"])
    ]


def ancestors(relations, node, rel_type="IS-A"):
    visited, frontier, chain = set(), [node], []
    while frontier:
        current = frontier.pop()
        if current in visited:
            continue
        visited.add(current)
        for r in relations:
            if r["source"] == current and r["type"] == rel_type:
                chain.append((current, r["target"]))
                frontier.append(r["target"])
    return chain


def descendants(relations, node, rel_type="IS-A"):
    visited, frontier, chain = set(), [node], []
    while frontier:
        current = frontier.pop()
        if current in visited:
            continue
        visited.add(current)
        for r in relations:
            if r["target"] == current and r["type"] == rel_type:
                chain.append((r["source"], current))
                frontier.append(r["source"])
    return chain


def neighborhood(relations, node):
    return [r for r in relations if r["source"] == node or r["target"] == node]


def _fmt(r, compact=False):
    note = (r.get("note") or "").strip().replace("\n", " ")

    if compact and len(note) > 90:
        note = note[:90] + "…"

    line = f"  [{r['type']}]  {r['source']}  →  {r['target']}"
    if note:
        line += f"\n         {note}"
    return line


def _fmt_info(node_id: str, meta: dict | None, relations: list[dict]) -> str:
    """Pretty-print node metadata and its edge count."""
    if not meta:
        return f"No metadata found for '{node_id}'."
    lines = []
    section = meta.get("_section", "")
    lines.append(f"{'─' * 60}")
    lines.append(f"  {meta.get('label', node_id)}  [{section}]")
    lines.append(f"{'─' * 60}")

    desc = (meta.get("description") or "").strip().replace("\n", " ")
    if desc:
        lines.append(f"  {desc}")
        lines.append("")

    if section == "concepts":
        module = meta.get("module")
        tags = meta.get("tags") or []
        if module:
            lines.append(f"  Module : {module}")
        if tags:
            lines.append(f"  Tags   : {', '.join(str(t) for t in tags)}")

    if section == "people_and_institutions":
        for key, label in (("type", "Type"), ("era", "Era"), ("affiliation", "Affiliation")):
            val = meta.get(key, "")
            if val:
                lines.append(f"  {label:<12}: {val}")

    if section == "examples_and_metaphors":
        source = meta.get("source", "")
        illustrates = meta.get("illustrates") or []
        if source:
            lines.append(f"  Source     : {source}")
        if illustrates:
            lines.append(f"  Illustrates: {', '.join(illustrates)}")

    edges = [r for r in relations if r["source"] == node_id or r["target"] == node_id]
    lines.append(f"\n  Edges: {len(edges)}")
    for r in edges:
        arrow = "→" if r["source"] == node_id else "←"
        other = r["target"] if r["source"] == node_id else r["source"]
        lines.append(f"    [{r['type']}] {arrow} {other}")

    return "\n".join(lines)


def main():
    relations = load()
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    # --- flags ---
    compact = "--compact" in args
    args = [a for a in args if a not in ("--compact", "--full")]

    # --- node info mode ---
    if args[0] == "--info":
        if len(args) < 2:
            print("Error: --info requires a node ID")
            sys.exit(1)
        node_id = args[1]
        metadata = load_metadata()
        print(_fmt_info(node_id, metadata.get(node_id), relations))
        return

    # --- graph traversal modes ---
    if args[0] == "--ancestors":
        node = args[1]
        rel_type = args[2] if len(args) > 2 else "IS-A"
        chain = ancestors(relations, node, rel_type)
        print(f"Ancestors of '{node}' via {rel_type} ({len(chain)}):")
        for src, tgt in chain:
            print(f"  {src}  →  {tgt}")
        return

    if args[0] == "--descendants":
        node = args[1]
        rel_type = args[2] if len(args) > 2 else "IS-A"
        chain = descendants(relations, node, rel_type)
        print(f"Descendants of '{node}' via {rel_type} ({len(chain)}):")
        for src, tgt in chain:
            print(f"  {src}  →  {tgt}")
        return

    if args[0] == "--neighborhood":
        node = args[1]
        results = neighborhood(relations, node)
        print(f"All edges touching '{node}' ({len(results)}):")
        for r in results:
            print(_fmt(r, compact))
        return

    # --- triple pattern query ---
    pattern = " ".join(args)
    parts = pattern.split()
    if len(parts) != 3:
        print(f"Error: expected 3-token pattern like '? IS-A learning', got: {pattern!r}")
        sys.exit(1)

    source_pat, type_pat, target_pat = parts
    results = query_triples(relations, source_pat, type_pat, target_pat)

    print(f"[{source_pat}]  --{type_pat}-->  [{target_pat}]  ({len(results)} results)\n")
    for r in results:
        print(_fmt(r, compact))


if __name__ == "__main__":
    main()