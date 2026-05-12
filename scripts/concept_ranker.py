#!/usr/bin/env python3
"""
Information-theoretic concept prioritization for FAB 2026.

Scores every node in the ontology using three graph-theoretic measures:

  PageRank (40%)        — global prestige; concepts many others "point toward"
  Betweenness (35%)     — concepts that bridge disparate sub-topics
  In-degree (25%)       — foundational concepts; many things depend on these

Composite score = 0.40 * norm(PageRank) + 0.35 * norm(Betweenness) + 0.25 * norm(InDegree)

Commands
--------
  rank    Print the ranked concept table (default top 30)
  budget  Select highest-value concepts within a time budget
  save    Write ranking to knowledge-base/study_priority.yaml
  report  Write a markdown artifact to artifacts/
"""

from __future__ import annotations

import argparse
import sqlite3
from collections import defaultdict
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401
from ontology_core.paths import ARTIFACTS_DIR, DB_PATH, MASTERY_YAML, PRIORITY_YAML
from ontology_core.yaml_io import load_yaml, save_yaml

MINUTES_PER_CONCEPT = 15  # default study-time estimate per concept


# ---------------------------------------------------------------------------
# Graph loading
# ---------------------------------------------------------------------------

def load_graph(node_type: str | None = None) -> tuple[dict, list[tuple]]:
    """Return (nodes_dict, edges_list) from ontology.db.

    nodes_dict: {id: {"id", "label", "type"}}
    edges_list: [(source_id, target_id), ...]
    """
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    if node_type and node_type != "all":
        cur.execute("SELECT id, label, node_type FROM nodes WHERE node_type = ?", (node_type,))
    else:
        cur.execute("SELECT id, label, node_type FROM nodes")

    nodes = {row[0]: {"id": row[0], "label": row[1], "type": row[2]} for row in cur.fetchall()}

    # Load all edges (even between different node types — they all matter for centrality)
    cur.execute("SELECT source_id, target_id FROM relations")
    edges = [(r[0], r[1]) for r in cur.fetchall() if r[0] in nodes and r[1] in nodes]

    conn.close()
    return nodes, edges


# ---------------------------------------------------------------------------
# Graph algorithms (no networkx — stdlib only)
# ---------------------------------------------------------------------------

def compute_pagerank(
    node_ids: list[str],
    edges: list[tuple],
    damping: float = 0.85,
    iterations: int = 60,
) -> dict[str, float]:
    """Iterative PageRank. Converges in ~50 iterations for graphs of this size."""
    out_neighbors: dict[str, list] = defaultdict(list)
    in_neighbors: dict[str, list] = defaultdict(list)
    node_set = set(node_ids)

    for src, tgt in edges:
        if src in node_set and tgt in node_set:
            out_neighbors[src].append(tgt)
            in_neighbors[tgt].append(src)

    n = len(node_ids)
    pr = {nid: 1.0 / n for nid in node_ids}

    for _ in range(iterations):
        new_pr: dict[str, float] = {}
        for nid in node_ids:
            rank_sum = sum(
                pr[src] / max(len(out_neighbors[src]), 1)
                for src in in_neighbors[nid]
            )
            new_pr[nid] = (1.0 - damping) / n + damping * rank_sum
        pr = new_pr

    return pr


def compute_betweenness(
    node_ids: list[str],
    edges: list[tuple],
) -> dict[str, float]:
    """Unweighted betweenness centrality via Brandes algorithm (undirected).

    Runtime: O(V * (V + E)) — acceptable for ~430 nodes, ~339 edges.
    """
    # Build undirected adjacency for betweenness (we want bridge concepts regardless of direction)
    adj: dict[str, list] = defaultdict(list)
    node_set = set(node_ids)
    for src, tgt in edges:
        if src in node_set and tgt in node_set:
            adj[src].append(tgt)
            adj[tgt].append(src)

    betweenness: dict[str, float] = defaultdict(float)
    n = len(node_ids)

    for s in node_ids:
        stack: list[str] = []
        predecessors: dict[str, list] = defaultdict(list)
        sigma: dict[str, int] = defaultdict(int)
        sigma[s] = 1
        dist: dict[str, int] = {s: 0}
        queue: list[str] = [s]

        while queue:
            v = queue.pop(0)
            stack.append(v)
            for w in adj[v]:
                if w not in dist:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    predecessors[w].append(v)

        delta: dict[str, float] = defaultdict(float)
        while stack:
            w = stack.pop()
            for v in predecessors[w]:
                delta[v] += (sigma[v] / max(sigma[w], 1)) * (1.0 + delta[w])
            if w != s:
                betweenness[w] += delta[w]

    # Normalise: divide by (n-1)(n-2) for undirected graph
    norm = (n - 1) * (n - 2) if n > 2 else 1
    return {nid: betweenness[nid] / norm for nid in node_ids}


def compute_degrees(
    node_ids: list[str],
    edges: list[tuple],
) -> dict[str, dict]:
    """Return in-degree and out-degree for each node."""
    in_deg: dict[str, int] = defaultdict(int)
    out_deg: dict[str, int] = defaultdict(int)
    node_set = set(node_ids)

    for src, tgt in edges:
        if src in node_set and tgt in node_set:
            out_deg[src] += 1
            in_deg[tgt] += 1

    return {
        nid: {"in": in_deg[nid], "out": out_deg[nid]}
        for nid in node_ids
    }


def composite_scores(
    node_ids: list[str],
    pagerank: dict[str, float],
    betweenness: dict[str, float],
    degrees: dict[str, dict],
) -> dict[str, float]:
    """Normalise each metric to [0,1] then compute weighted composite."""
    max_pr = max(pagerank.values(), default=1.0)
    max_bt = max(betweenness.values(), default=1.0) or 1.0
    max_in = max(d["in"] for d in degrees.values()) if degrees else 1

    scores: dict[str, float] = {}
    for nid in node_ids:
        pr_n = pagerank.get(nid, 0) / max_pr
        bt_n = betweenness.get(nid, 0) / max_bt
        in_n = degrees.get(nid, {}).get("in", 0) / max_in
        scores[nid] = round(0.40 * pr_n + 0.35 * bt_n + 0.25 * in_n, 4)

    return scores


# ---------------------------------------------------------------------------
# Mastery helpers
# ---------------------------------------------------------------------------

def load_mastered(path: Path | None = None) -> set[str]:
    """Return set of concept IDs marked mastered in the given YAML file."""
    p = path or MASTERY_YAML
    if not p.exists():
        return set()
    data = load_yaml(p)
    return {
        e["id"]
        for e in data.get("mastery", {}).get("concepts", [])
        if e.get("mastered")
    }


# ---------------------------------------------------------------------------
# Core ranking function
# ---------------------------------------------------------------------------

def rank(
    node_type: str | None = None,
    exclude_ids: set[str] | None = None,
) -> list[dict]:
    """Return list of node dicts sorted by composite score descending.

    Each dict has: id, label, type, composite, pagerank, betweenness, in_degree, out_degree.
    """
    nodes, edges = load_graph(node_type)
    node_ids = list(nodes.keys())

    pr = compute_pagerank(node_ids, edges)
    bt = compute_betweenness(node_ids, edges)
    deg = compute_degrees(node_ids, edges)
    comp = composite_scores(node_ids, pr, bt, deg)

    results = []
    for nid, node in nodes.items():
        if exclude_ids and nid in exclude_ids:
            continue
        results.append({
            "id": nid,
            "label": node["label"],
            "type": node["type"],
            "composite": comp.get(nid, 0),
            "pagerank": round(pr.get(nid, 0), 6),
            "betweenness": round(bt.get(nid, 0), 6),
            "in_degree": deg.get(nid, {}).get("in", 0),
            "out_degree": deg.get(nid, {}).get("out", 0),
        })

    results.sort(key=lambda x: x["composite"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_rank(args: argparse.Namespace) -> None:
    mastered = load_mastered(Path(args.mastered) if args.mastered else None)
    exclude = mastered if args.exclude_mastered else set()
    node_type = None if args.type == "all" else args.type

    results = rank(node_type=node_type, exclude_ids=exclude)
    top = results[: args.top]

    header = (
        f"\n{'Rank':<5} {'Score':>6}  {'PR':>8}  {'Btwn':>8}  {'In':>3}  {'Out':>3}  "
        f"{'Type':<8}  Label / ID"
    )
    sep = "-" * 100
    print(header)
    print(sep)
    for i, r in enumerate(top, 1):
        label = r["label"]
        nid = r["id"]
        print(
            f"{i:<5} {r['composite']:>6.4f}  {r['pagerank']:>8.5f}  "
            f"{r['betweenness']:>8.4f}  {r['in_degree']:>3}  {r['out_degree']:>3}  "
            f"{r['type']:<8}  {label} ({nid})"
        )

    total_available = len(results)
    print(f"\n{len(top)} of {total_available} nodes shown")
    if mastered:
        note = f"  ({len(mastered)} mastered excluded)" if args.exclude_mastered else f"  ({len(mastered)} mastered in DB)"
        print(f"Mastery file: {args.mastered or MASTERY_YAML}{note}")
    print("\nMetric weights: PageRank 40% · Betweenness 35% · In-degree 25%")


def cmd_budget(args: argparse.Namespace) -> None:
    mastered = load_mastered(Path(args.mastered) if args.mastered else None)
    node_type = None if args.type == "all" else args.type

    results = rank(node_type=node_type, exclude_ids=mastered)

    total_minutes = int(args.hours * 60)
    mpc = args.minutes_per_concept
    capacity = total_minutes // mpc
    selected = results[:capacity]

    print(f"\nTime budget : {args.hours}h = {total_minutes} min")
    print(f"~{mpc} min/concept → capacity: {capacity} concepts")
    print(f"Mastered (excluded): {len(mastered)}")
    print(f"Remaining unmastered: {len(results)}\n")

    header = f"{'Rank':<5} {'Score':>6}  {'In':>3}  {'Out':>3}  Label (id)"
    print(header)
    print("-" * 80)
    for i, r in enumerate(selected, 1):
        print(f"{i:<5} {r['composite']:>6.4f}  {r['in_degree']:>3}  {r['out_degree']:>3}  {r['label']} ({r['id']})")

    time_used = len(selected) * mpc
    remaining = len(results) - len(selected)
    print(f"\nSelected: {len(selected)} concepts · ~{time_used} min")
    print(f"Not covered this session: {remaining} unmastered concepts")


def cmd_save(args: argparse.Namespace) -> None:
    node_type = None if args.type == "all" else args.type
    mastered = load_mastered(Path(args.mastered) if args.mastered else None)
    results = rank(node_type=node_type)

    entries = []
    for i, r in enumerate(results, 1):
        entry = {
            "rank": i,
            "id": r["id"],
            "label": r["label"],
            "type": r["type"],
            "composite_score": r["composite"],
            "pagerank": r["pagerank"],
            "betweenness": r["betweenness"],
            "in_degree": r["in_degree"],
            "out_degree": r["out_degree"],
        }
        if r["id"] in mastered:
            entry["mastered"] = True
        entries.append(entry)

    output = {
        "study_priority": {
            "generated_at": str(date.today()),
            "method": "pagerank=0.40, betweenness=0.35, in_degree=0.25",
            "node_type_filter": args.type,
            "total_ranked": len(entries),
            "concepts": entries,
        }
    }

    save_yaml(PRIORITY_YAML, output)

    print(f"Saved → {PRIORITY_YAML}")
    print(f"{len(entries)} concepts ranked")


def cmd_report(args: argparse.Namespace) -> None:
    node_type = None if args.type == "all" else args.type
    mastered = load_mastered(Path(args.mastered) if args.mastered else None)
    exclude = mastered if args.exclude_mastered else set()
    results = rank(node_type=node_type, exclude_ids=exclude)
    top = results[: args.top]

    today = date.today()
    slug = f"concept_priority_{today}"
    out_path = ARTIFACTS_DIR / f"{slug}.md"
    ARTIFACTS_DIR.mkdir(exist_ok=True)

    lines = [
        f"# Concept Priority Report — {today}",
        "",
        f"**Method:** PageRank (40%) + Betweenness Centrality (35%) + In-degree (25%)",
        f"**Filter:** node type = `{args.type}`",
        f"**Mastered excluded:** {len(mastered)}",
        f"**Showing:** top {len(top)} of {len(results)} unmastered concepts",
        "",
        "| Rank | Score | In | Out | Label | ID |",
        "|------|------:|---:|----:|-------|-----|",
    ]

    for i, r in enumerate(top, 1):
        mastered_mark = " ✓" if r["id"] in mastered else ""
        lines.append(
            f"| {i} | {r['composite']:.4f} | {r['in_degree']} | {r['out_degree']} "
            f"| {r['label']}{mastered_mark} | `{r['id']}` |"
        )

    lines += [
        "",
        "## Score Interpretation",
        "",
        "- **Score**: composite (0–1). Higher = more central to the concept graph.",
        "- **In**: in-degree. Many concepts depend on / point to this one — it is foundational.",
        "- **Out**: out-degree. This concept points to many others — it is a hub of references.",
        "",
        "## How to Use This List",
        "",
        "1. Work top-to-bottom when time is limited — you cover the highest-leverage concepts first.",
        "2. Run `study_scheduler.py plan` to turn this priority list into a day-by-day schedule.",
        "3. After mastering a concept, run `study_scheduler.py mark --concept <id>` and regenerate.",
        "",
        f"*Generated by `concept_ranker.py report` on {today}*",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written → {out_path}")
    print(f"Open with any Markdown viewer.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="concept_ranker",
        description="Information-theoretic concept prioritization for FAB 2026",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- rank ---
    p = sub.add_parser("rank", help="Print ranked concept table")
    p.add_argument("--top", type=int, default=30, metavar="N", help="Show top N (default 30)")
    p.add_argument("--type", choices=["concept", "person", "example", "all"], default="concept")
    p.add_argument("--mastered", metavar="YAML", help="Path to mastery YAML (default: knowledge-base/mastery.yaml)")
    p.add_argument("--exclude-mastered", action="store_true", help="Hide already-mastered concepts")
    p.set_defaults(func=cmd_rank)

    # --- budget ---
    p = sub.add_parser("budget", help="Select best concepts for a study session time budget")
    p.add_argument("--hours", type=float, required=True, help="Hours available to study")
    p.add_argument("--minutes-per-concept", dest="minutes_per_concept", type=int,
                   default=MINUTES_PER_CONCEPT, help=f"Minutes per concept (default {MINUTES_PER_CONCEPT})")
    p.add_argument("--type", choices=["concept", "person", "example", "all"], default="concept")
    p.add_argument("--mastered", metavar="YAML", help="Path to mastery YAML to exclude mastered concepts")
    p.set_defaults(func=cmd_budget)

    # --- save ---
    p = sub.add_parser("save", help="Save priority ranking to knowledge-base/study_priority.yaml")
    p.add_argument("--type", choices=["concept", "person", "example", "all"], default="all")
    p.add_argument("--mastered", metavar="YAML", help="Path to mastery YAML (mastered flag added to entries)")
    p.set_defaults(func=cmd_save)

    # --- report ---
    p = sub.add_parser("report", help="Write markdown artifact to artifacts/")
    p.add_argument("--top", type=int, default=50, metavar="N", help="Include top N concepts (default 50)")
    p.add_argument("--type", choices=["concept", "person", "example", "all"], default="concept")
    p.add_argument("--mastered", metavar="YAML", help="Path to mastery YAML")
    p.add_argument("--exclude-mastered", action="store_true", help="Hide mastered concepts in the report")
    p.set_defaults(func=cmd_report)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
