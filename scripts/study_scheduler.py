#!/usr/bin/env python3
"""
CSP-based study scheduler for FAB 2026.

Models the scheduling problem as a Constraint Satisfaction Problem:

  Variables : one per concept — the calendar date it is first studied
  Domains   : dates from tomorrow to (exam_date - 1)
  Constraints:
    (1) Module ordering  — concepts from module M must appear before module M+1
                           Enforced via AC-3-style domain propagation: each
                           module's date-domain is pruned to a contiguous
                           sub-range, and ranges are made non-overlapping.
    (2) Daily capacity   — at most (sessions_per_day × concepts_per_session)
                           concepts per calendar day
    (3) Feasibility      — if any module's domain becomes empty the planner
                           detects infeasibility and reports it

After AC-3 propagation, a greedy left-to-right assignment fills each day
to capacity in module order.

Commands
--------
  plan          Generate a study schedule and save it
  show          Display the saved schedule
  mark          Mark a concept as mastered
  init-mastery  Initialise knowledge-base/mastery.yaml from all DB concepts
"""

from __future__ import annotations

import argparse
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import _bootstrap  # noqa: F401
from ontology_core.paths import ARTIFACTS_DIR, DB_PATH, MASTERY_YAML, SCHEDULE_YAML
from ontology_core.yaml_io import load_yaml, save_yaml


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_concepts_with_modules() -> list[dict]:
    """Return all concepts with their earliest source-document course_order."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("""
        SELECT n.id, n.label,
               COALESCE(MIN(d.course_order), 999) AS module_order
        FROM nodes n
        LEFT JOIN source_documents sd ON sd.node_id = n.id
        LEFT JOIN documents d         ON d.doc_id   = sd.doc_id
        WHERE n.node_type = 'concept'
        GROUP BY n.id
        ORDER BY module_order, n.label
    """)
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "label": r[1], "module_order": r[2]} for r in rows]


def load_mastery() -> dict[str, dict]:
    """Return {concept_id: entry_dict} from mastery.yaml, or {} if file absent."""
    if not MASTERY_YAML.exists():
        return {}
    data = load_yaml(MASTERY_YAML)
    return {
        e["id"]: e
        for e in data.get("mastery", {}).get("concepts", [])
    }


def save_mastery(mastery: dict[str, dict]) -> None:
    """Write mastery dict back to mastery.yaml."""
    concepts_list = sorted(mastery.values(), key=lambda e: e["id"])
    output = {
        "mastery": {
            "updated_at": str(date.today()),
            "concepts": concepts_list,
        }
    }
    save_yaml(MASTERY_YAML, output)


# ---------------------------------------------------------------------------
# AC-3 domain propagation
# ---------------------------------------------------------------------------

def _build_date_range(start: date, end_exclusive: date) -> list[date]:
    """Return list of dates [start, end_exclusive)."""
    days = []
    d = start
    while d < end_exclusive:
        days.append(d)
        d += timedelta(days=1)
    return days


def ac3_propagate(
    concepts_by_module: dict[int, list[dict]],
    available_days: list[date],
    capacity: int,
) -> dict[int, list[date]] | None:
    """Narrow each module's domain via AC-3-style forward-arc consistency.

    Ordering arcs: (module M) → (module M+1).
    For arc (M, M+1):
      - Remove any day d from domain(M) if there is no day d' > d in domain(M+1).
      - Remove any day d from domain(M+1) if there is no day d' < d in domain(M).

    We also enforce capacity: a module's domain must contain enough distinct days
    to hold all its concepts at the given capacity.

    Returns pruned domain dict {module_order: [dates]}, or None if infeasible.
    """
    modules = sorted(concepts_by_module.keys())
    n_modules = len(modules)
    total_days = len(available_days)
    total_concepts = sum(len(v) for v in concepts_by_module.values())

    # --- Initial domain assignment ---
    # Partition available_days into n_modules contiguous segments proportional
    # to concept count. This is the "initial constraint propagation" step —
    # it narrows domains from [all days] to a per-module sub-range.
    domains: dict[int, list[date]] = {}
    day_cursor = 0
    for i, m in enumerate(modules):
        n = len(concepts_by_module[m])
        if total_concepts == 0:
            break
        # Proportional allocation, at least ceil(n / capacity) days
        raw_share = max(1, round(n / total_concepts * total_days))
        min_days_needed = -(-n // capacity)  # ceiling division
        days_for_module = max(raw_share, min_days_needed)

        # Last module gets remaining days to avoid rounding gaps
        if i == n_modules - 1:
            end = total_days
        else:
            end = min(day_cursor + days_for_module, total_days)

        domains[m] = available_days[day_cursor:end]
        day_cursor = end
        if day_cursor >= total_days:
            # Fill remaining modules with empty domains (infeasible)
            for remaining_m in modules[i + 1:]:
                domains[remaining_m] = []
            break

    # --- AC-3 queue: arcs between adjacent modules ---
    # Each arc is (M_earlier, M_later) meaning max(domain(M_earlier)) < min(domain(M_later))
    queue: list[tuple[int, int]] = []
    for i in range(len(modules) - 1):
        queue.append((modules[i], modules[i + 1]))
        queue.append((modules[i + 1], modules[i]))  # reverse arc

    while queue:
        m_from, m_to = queue.pop(0)
        d_from = domains.get(m_from, [])
        d_to = domains.get(m_to, [])
        if not d_from or not d_to:
            continue

        changed = False

        if m_from < m_to:
            # Forward arc: d_from must have at least one value < max(d_to)
            max_to = max(d_to)
            pruned = [d for d in d_from if d < max_to]
            if len(pruned) < len(d_from):
                domains[m_from] = pruned
                changed = True
        else:
            # Reverse arc: d_from must have at least one value > min(d_to)
            min_to = min(d_to)
            pruned = [d for d in d_from if d > min_to]
            if len(pruned) < len(d_from):
                domains[m_from] = pruned
                changed = True

        if not domains[m_from]:
            return None  # Domain wipe-out: infeasible

        if changed:
            # Re-enqueue all arcs involving m_from
            for m in modules:
                if m != m_from:
                    queue.append((m, m_from))

    # --- Capacity feasibility check ---
    for m in modules:
        n_concepts = len(concepts_by_module[m])
        n_days = len(domains.get(m, []))
        if n_days * capacity < n_concepts:
            return None  # Not enough day-slots to fit all concepts

    return domains


# ---------------------------------------------------------------------------
# Greedy assignment
# ---------------------------------------------------------------------------

def greedy_assign(
    concepts_sorted: list[dict],
    module_domains: dict[int, list[date]],
    capacity: int,
    overflow_days: list[date],
) -> dict[date, list[dict]]:
    """Assign each concept to the earliest available day within its module domain.

    Falls back to overflow_days (days after all modules' allocated range) if needed.
    """
    day_load: dict[date, list[dict]] = defaultdict(list)

    for concept in concepts_sorted:
        m = concept["module_order"]
        domain = module_domains.get(m, [])
        assigned = False

        for day in domain:
            if len(day_load[day]) < capacity:
                day_load[day].append(concept)
                assigned = True
                break

        if not assigned:
            for day in overflow_days:
                if len(day_load[day]) < capacity:
                    day_load[day].append(concept)
                    assigned = True
                    break

        if not assigned:
            # Schedule on exam-1 as a last resort (shouldn't happen after feasibility check)
            fallback = overflow_days[-1] if overflow_days else domain[-1] if domain else None
            if fallback:
                day_load[fallback].append(concept)

    return dict(day_load)


# ---------------------------------------------------------------------------
# Schedule generation
# ---------------------------------------------------------------------------

def generate_schedule(
    exam_date: date,
    sessions_per_day: int,
    concepts_per_session: int,
    mastered_ids: set[str],
) -> dict | None:
    """Run the full CSP pipeline and return a schedule dict, or None if infeasible."""
    today = date.today()
    if exam_date <= today:
        raise ValueError(f"Exam date {exam_date} must be in the future")

    available_days = _build_date_range(today + timedelta(days=1), exam_date)
    if not available_days:
        raise ValueError("No days between today and exam date")

    capacity = sessions_per_day * concepts_per_session
    all_concepts = load_concepts_with_modules()
    to_study = [c for c in all_concepts if c["id"] not in mastered_ids]

    if not to_study:
        return {"days": [], "note": "All concepts already mastered."}

    # Group by module for AC-3
    by_module: dict[int, list[dict]] = defaultdict(list)
    for c in to_study:
        by_module[c["module_order"]].append(c)

    # AC-3 domain propagation
    pruned_domains = ac3_propagate(dict(by_module), available_days, capacity)

    if pruned_domains is None:
        # Infeasible: not enough time. Return partial schedule with warning.
        total_capacity = len(available_days) * capacity
        partial = to_study[:total_capacity]
        partial_by_module: dict[int, list[dict]] = defaultdict(list)
        for c in partial:
            partial_by_module[c["module_order"]].append(c)
        pruned_domains = ac3_propagate(dict(partial_by_module), available_days, capacity)
        if pruned_domains is None:
            # Degenerate case: just fill days greedily without module ordering
            pruned_domains = {m: available_days for m in partial_by_module}
        to_study = partial
        infeasible_warning = (
            f"Warning: not enough time to study all {len(all_concepts) - len(mastered_ids)} concepts. "
            f"Schedule limited to top {len(to_study)} by module order. "
            f"Consider reducing scope or extending your timeline."
        )
    else:
        infeasible_warning = None

    # Greedy assignment
    last_domain_day = max(
        (max(d) for d in pruned_domains.values() if d),
        default=available_days[-1],
    )
    last_idx = available_days.index(last_domain_day) if last_domain_day in available_days else len(available_days) - 1
    overflow_days = available_days[last_idx + 1:]

    day_schedule = greedy_assign(to_study, pruned_domains, capacity, overflow_days)

    # Format output
    days_output = []
    for day in sorted(day_schedule.keys()):
        concepts_today = day_schedule[day]
        days_output.append({
            "date": str(day),
            "concepts": [
                {"id": c["id"], "label": c["label"], "module": c["module_order"]}
                for c in concepts_today
            ],
        })

    return {
        "exam_date": str(exam_date),
        "sessions_per_day": sessions_per_day,
        "concepts_per_session": concepts_per_session,
        "capacity_per_day": capacity,
        "total_days_available": len(available_days),
        "total_concepts_scheduled": len(to_study),
        "mastered_excluded": len(mastered_ids),
        "generated_at": str(date.today()),
        "algorithm": "AC-3 domain propagation + greedy assignment",
        "warning": infeasible_warning,
        "days": days_output,
    }


def save_schedule_yaml(schedule: dict) -> None:
    save_yaml(SCHEDULE_YAML, {"study_schedule": schedule})


def write_schedule_md(schedule: dict) -> Path:
    """Write a human-readable markdown schedule to artifacts/."""
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    today = schedule.get("generated_at", str(date.today()))
    exam = schedule.get("exam_date", "unknown")
    slug = f"study_schedule_{today}"
    out_path = ARTIFACTS_DIR / f"{slug}.md"

    lines = [
        f"# Study Schedule — generated {today}",
        "",
        f"**Exam date:** {exam}",
        f"**Sessions per day:** {schedule.get('sessions_per_day', '?')}",
        f"**Concepts per session:** {schedule.get('concepts_per_session', '?')}",
        f"**Total concepts scheduled:** {schedule.get('total_concepts_scheduled', '?')}",
        f"**Mastered (excluded):** {schedule.get('mastered_excluded', 0)}",
        f"**Algorithm:** {schedule.get('algorithm', 'CSP')}",
        "",
    ]

    if schedule.get("warning"):
        lines += [f"> **{schedule['warning']}**", ""]

    days = schedule.get("days", [])
    if not days:
        lines.append("*No concepts to schedule.*")
    else:
        for day_entry in days:
            d = day_entry["date"]
            concepts = day_entry["concepts"]
            # Group into session blocks
            cps = schedule.get("concepts_per_session", 4)
            lines.append(f"## {d}")
            lines.append("")
            for s_idx, session_start in enumerate(range(0, len(concepts), cps), 1):
                session_concepts = concepts[session_start: session_start + cps]
                lines.append(f"**Session {s_idx}**")
                for c in session_concepts:
                    lines.append(f"- [ ] {c['label']} (`{c['id']}`, module {c['module']})")
                lines.append("")

    lines += [
        "---",
        "",
        "## Usage",
        "",
        "- Check off concepts as you study them.",
        "- After mastering a concept: `uv run python scripts/study_scheduler.py mark --concept <id>`",
        "- Regenerate with: `uv run python scripts/study_scheduler.py plan --exam <YYYY-MM-DD>`",
        "",
        f"*Generated by `study_scheduler.py plan` on {today}*",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_plan(args: argparse.Namespace) -> None:
    try:
        exam_date = date.fromisoformat(args.exam)
    except ValueError:
        print(f"Error: invalid date '{args.exam}'. Use YYYY-MM-DD format.")
        return

    mastery = load_mastery()
    mastered_ids = {cid for cid, e in mastery.items() if e.get("mastered")}

    print(f"Exam date        : {exam_date}")
    print(f"Sessions/day     : {args.sessions_per_day}")
    print(f"Concepts/session : {args.concepts_per_session}")
    print(f"Mastered         : {len(mastered_ids)}")
    print(f"Running AC-3 constraint propagation...")

    try:
        schedule = generate_schedule(
            exam_date=exam_date,
            sessions_per_day=args.sessions_per_day,
            concepts_per_session=args.concepts_per_session,
            mastered_ids=mastered_ids,
        )
    except ValueError as e:
        print(f"Error: {e}")
        return

    if schedule is None:
        print("Error: schedule generation failed unexpectedly.")
        return

    if schedule.get("warning"):
        print(f"\n{schedule['warning']}\n")

    # Print summary
    days = schedule.get("days", [])
    print(f"\nSchedule: {len(days)} study days, {schedule.get('total_concepts_scheduled', 0)} concepts\n")

    for day_entry in days[:7]:  # preview first week
        d = day_entry["date"]
        concepts = day_entry["concepts"]
        labels = ", ".join(c["label"] for c in concepts[:3])
        more = f" … +{len(concepts)-3}" if len(concepts) > 3 else ""
        print(f"  {d}: {labels}{more}")
    if len(days) > 7:
        print(f"  ... ({len(days) - 7} more days)")

    # Save YAML
    save_schedule_yaml(schedule)
    print(f"\nSchedule YAML → {SCHEDULE_YAML}")

    # Write artifact MD
    md_path = write_schedule_md(schedule)
    print(f"Schedule MD   → {md_path}")
    print(f"\nOpen {md_path.name} in any Markdown viewer.")


def cmd_show(args: argparse.Namespace) -> None:
    if not SCHEDULE_YAML.exists():
        print(f"No schedule found at {SCHEDULE_YAML}. Run 'plan' first.")
        return

    data = load_yaml(SCHEDULE_YAML)

    schedule = data.get("study_schedule", {})
    days = schedule.get("days", [])

    print(f"\nSchedule for exam: {schedule.get('exam_date', 'unknown')}")
    print(f"Generated: {schedule.get('generated_at', 'unknown')}")
    print(f"Total concepts: {schedule.get('total_concepts_scheduled', '?')}")
    print(f"Mastered excluded: {schedule.get('mastered_excluded', 0)}\n")

    today = str(date.today())
    found_today = False

    for day_entry in days:
        d = day_entry["date"]
        concepts = day_entry["concepts"]
        marker = " ← TODAY" if d == today else ""
        if d == today:
            found_today = True

        if args.full or d >= today:
            print(f"{d}{marker}")
            cps = schedule.get("concepts_per_session", 4)
            for s_idx, start in enumerate(range(0, len(concepts), cps), 1):
                session = concepts[start: start + cps]
                print(f"  Session {s_idx}:")
                for c in session:
                    print(f"    · {c['label']} ({c['id']})")

    if not found_today:
        print(f"(Today {today} has no scheduled study session.)")


def cmd_mark(args: argparse.Namespace) -> None:
    mastery = load_mastery()

    if not mastery:
        # Bootstrap from DB if mastery file doesn't exist yet
        concepts = load_concepts_with_modules()
        mastery = {
            c["id"]: {"id": c["id"], "label": c["label"], "mastered": False, "mastered_at": None}
            for c in concepts
        }

    concept_id = args.concept
    if concept_id not in mastery:
        # Try to find it in DB
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute("SELECT id, label FROM nodes WHERE id = ?", (concept_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            print(f"Error: concept '{concept_id}' not found in ontology.db")
            return
        mastery[concept_id] = {"id": row[0], "label": row[1], "mastered": False, "mastered_at": None}

    mastery[concept_id]["mastered"] = not args.unmark
    mastery[concept_id]["mastered_at"] = str(date.today()) if not args.unmark else None
    save_mastery(mastery)

    action = "Unmarked" if args.unmark else "Marked"
    label = mastery[concept_id].get("label", concept_id)
    print(f"{action}: {label} ({concept_id})")
    print(f"Saved → {MASTERY_YAML}")

    mastered_count = sum(1 for e in mastery.values() if e.get("mastered"))
    print(f"Total mastered: {mastered_count} / {len(mastery)}")


def cmd_init_mastery(args: argparse.Namespace) -> None:
    if MASTERY_YAML.exists() and not args.force:
        print(f"{MASTERY_YAML} already exists. Use --force to overwrite.")
        return

    concepts = load_concepts_with_modules()
    mastery = {
        c["id"]: {
            "id": c["id"],
            "label": c["label"],
            "mastered": False,
            "mastered_at": None,
        }
        for c in concepts
    }
    save_mastery(mastery)
    print(f"Initialised mastery YAML with {len(mastery)} concepts → {MASTERY_YAML}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="study_scheduler",
        description="CSP-based study scheduler for FAB 2026",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- plan ---
    p = sub.add_parser("plan", help="Generate a study schedule")
    p.add_argument("--exam", required=True, metavar="YYYY-MM-DD", help="Exam date")
    p.add_argument("--sessions-per-day", type=int, default=2, dest="sessions_per_day",
                   help="Study sessions per day (default 2)")
    p.add_argument("--concepts-per-session", type=int, default=4, dest="concepts_per_session",
                   help="Concepts per session (default 4)")
    p.set_defaults(func=cmd_plan)

    # --- show ---
    p = sub.add_parser("show", help="Display the saved schedule")
    p.add_argument("--full", action="store_true", help="Show all days including past ones")
    p.set_defaults(func=cmd_show)

    # --- mark ---
    p = sub.add_parser("mark", help="Mark a concept as mastered (or unmark with --unmark)")
    p.add_argument("--concept", required=True, metavar="CONCEPT_ID", help="Concept ID to mark")
    p.add_argument("--unmark", action="store_true", help="Unmark as mastered")
    p.set_defaults(func=cmd_mark)

    # --- init-mastery ---
    p = sub.add_parser("init-mastery", help="Initialise knowledge-base/mastery.yaml")
    p.add_argument("--force", action="store_true", help="Overwrite existing file")
    p.set_defaults(func=cmd_init_mastery)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
