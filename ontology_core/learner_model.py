"""JTMS-lite learner model backed by append-only observations.

Beliefs in this module are generated cache entries. The durable memory is the
event log plus explicit justification rules; evaluation recomputes which
tentative learner assumptions are currently in or out.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any

from .paths import (
    DB_PATH,
    LEARNER_BELIEFS_YAML,
    LEARNER_EVENTS_JSONL,
    LEARNER_JUSTIFICATIONS_YAML,
    LEARNER_MODEL_DIR,
    LEARNER_PROFILE_YAML,
    PRIORITY_YAML,
    SCHEDULE_YAML,
)
from .yaml_io import load_yaml, save_yaml

RATING_SCALE = {0: 0.0, 1: 0.33, 2: 0.66, 3: 1.0}
STRUGGLE_THRESHOLD = 0.45
MASTERY_THRESHOLD = 0.80
RECENT_RECALL_DAYS = 7
SELF_REPORT_DAYS = 14

PREREQUISITE_WEIGHTS = {
    "REQUIRES": 0.88,
    "ENABLES": 0.70,
    "PART-OF": 0.50,
    "COMPLICATES": 0.30,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_ts(value: Any) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    raw = str(value)
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _days_old(event: dict, now: datetime) -> float:
    return (now - _parse_ts(event.get("ts"))).total_seconds() / 86400


def _unique(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _default_profile() -> dict:
    return {
        "student_name": None,
        "exam_date": None,
        "target_outcome": None,
        "available_days": [],
        "session_preferences": {
            "sessions_per_day": 2,
            "concepts_per_session": 4,
        },
        "active_goal_ids": [],
    }


def _default_justifications() -> dict:
    return {
        "rules": [
            {
                "id": "low_recent_recall",
                "consequent_kind": "struggling_with",
                "event_types": ["flashcard_rating", "quiz_answer"],
                "window_days": RECENT_RECALL_DAYS,
                "threshold": STRUGGLE_THRESHOLD,
            },
            {
                "id": "recent_struggle_report",
                "consequent_kind": "struggling_with",
                "event_types": ["self_report"],
                "window_days": SELF_REPORT_DAYS,
                "polarity": "struggle",
            },
            {
                "id": "high_recent_recall",
                "consequent_kind": "mastered",
                "event_types": ["flashcard_rating", "quiz_answer"],
                "window_days": RECENT_RECALL_DAYS,
                "threshold": MASTERY_THRESHOLD,
                "min_attempts": 3,
            },
            {
                "id": "explicit_mastery",
                "consequent_kind": "mastered",
                "event_types": ["mastery_mark", "user_assertion"],
            },
            {
                "id": "one_hop_prerequisite_gap",
                "consequent_kind": "likely_prerequisite_gap",
                "relation_types": list(PREREQUISITE_WEIGHTS),
            },
            {"id": "schedule_capacity_check", "consequent_kind": "overloaded_schedule"},
            {"id": "recommend_next", "consequent_kind": "recommended_next"},
        ],
        "active_derivations": [],
    }


def _ensure_files() -> None:
    LEARNER_MODEL_DIR.mkdir(exist_ok=True)
    if not LEARNER_PROFILE_YAML.exists():
        save_yaml(LEARNER_PROFILE_YAML, {"profile": _default_profile()})
    if not LEARNER_EVENTS_JSONL.exists():
        LEARNER_EVENTS_JSONL.touch()
    if not LEARNER_BELIEFS_YAML.exists():
        save_yaml(LEARNER_BELIEFS_YAML, {"beliefs": []})
    if not LEARNER_JUSTIFICATIONS_YAML.exists():
        save_yaml(LEARNER_JUSTIFICATIONS_YAML, _default_justifications())


def _normalise_profile(profile: dict | None) -> dict:
    clean = _default_profile()
    for key, value in (profile or {}).items():
        if key == "session_preferences":
            clean[key].update(value or {})
        elif key in clean:
            clean[key] = value
        else:
            clean[key] = value
    clean["available_days"] = list(clean.get("available_days") or [])
    clean["active_goal_ids"] = list(clean.get("active_goal_ids") or [])
    clean["session_preferences"] = clean.get("session_preferences") or {}
    return clean


def load_profile() -> dict:
    _ensure_files()
    raw = load_yaml(LEARNER_PROFILE_YAML)
    return _normalise_profile(raw.get("profile", raw))


def save_profile(profile: dict) -> dict:
    _ensure_files()
    clean = _normalise_profile(profile)
    save_yaml(LEARNER_PROFILE_YAML, {"profile": clean})
    return clean


def append_event(event: dict) -> dict:
    _ensure_files()
    clean = {key: value for key, value in dict(event or {}).items() if value not in ("", None)}
    clean.setdefault("id", f"evt_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:6]}")
    clean.setdefault("ts", _now_iso())
    clean.setdefault("source", "learner")
    with LEARNER_EVENTS_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(clean, ensure_ascii=False, sort_keys=True) + "\n")
    return clean


def load_events(limit: int | None = None, concept_id: str | None = None) -> list[dict]:
    _ensure_files()
    events = []
    with LEARNER_EVENTS_JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if concept_id and event.get("concept_id") != concept_id:
                continue
            events.append(event)
    if limit is not None and limit >= 0:
        return events[-limit:]
    return events


def _load_justifications() -> dict:
    _ensure_files()
    raw = load_yaml(LEARNER_JUSTIFICATIONS_YAML)
    if not raw.get("rules"):
        raw = _default_justifications()
    raw.setdefault("active_derivations", [])
    return raw


def _save_active_derivations(active_derivations: list[dict]) -> None:
    raw = _load_justifications()
    raw["active_derivations"] = active_derivations
    save_yaml(LEARNER_JUSTIFICATIONS_YAML, raw)


def _event_score(event: dict) -> float | None:
    if event.get("type") == "flashcard_rating":
        try:
            rating = int(event.get("rating"))
        except (TypeError, ValueError):
            return None
        return RATING_SCALE.get(rating)

    if event.get("type") == "quiz_answer":
        if "score" in event:
            try:
                score = float(event["score"])
            except (TypeError, ValueError):
                return None
            return max(0.0, min(score / 100 if score > 1 else score, 1.0))
        if "correct" in event:
            return 1.0 if bool(event["correct"]) else 0.0

    return None


def _concept_id(event: dict) -> str | None:
    return event.get("concept_id") or event.get("subject")


def _recent(events: list[dict], now: datetime, days: int) -> list[dict]:
    return [event for event in events if _days_old(event, now) <= days]


def _node_labels() -> dict[str, str]:
    if not DB_PATH.exists():
        return {}
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, label FROM nodes")
        return {row[0]: row[1] for row in cur.fetchall()}
    finally:
        conn.close()


def _relation_ref(row: dict) -> str:
    return f"rel:{row['source_id']}:{row['rel_type']}:{row['target_id']}"


def _prerequisite_candidates(concept_id: str) -> list[dict]:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, rel_type, source_id, target_id, note
            FROM relations
            WHERE rel_type IN ('REQUIRES', 'ENABLES', 'PART-OF', 'COMPLICATES')
              AND (source_id = ? OR target_id = ?)
            """,
            (concept_id, concept_id),
        )
        rows = [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

    candidates = []
    for row in rows:
        rel_type = row["rel_type"]
        if rel_type == "REQUIRES" and row["source_id"] == concept_id:
            candidate = row["target_id"]
        elif rel_type == "ENABLES" and row["target_id"] == concept_id:
            candidate = row["source_id"]
        elif rel_type == "PART-OF" and row["target_id"] == concept_id:
            candidate = row["source_id"]
        elif rel_type == "COMPLICATES" and row["target_id"] == concept_id:
            candidate = row["source_id"]
        else:
            continue
        if candidate != concept_id:
            candidates.append({"concept_id": candidate, "relation": row, "weight": PREREQUISITE_WEIGHTS[rel_type]})
    return candidates


def _belief(
    kind: str,
    subject: str,
    status: str,
    confidence: float,
    support: list[str],
    opposition: list[str],
    updated_at: str,
    labels: dict[str, str],
    reason: str = "",
) -> dict:
    item = {
        "id": f"{kind}:{subject}",
        "kind": kind,
        "subject": subject,
        "status": status,
        "confidence": round(max(0.0, min(confidence, 1.0)), 3),
        "support": _unique(support),
        "opposition": _unique(opposition),
        "updated_at": updated_at,
    }
    if subject in labels:
        item["subject_label"] = labels[subject]
    if reason:
        item["reason"] = reason
    return item


def _effective_profile(profile: dict, events: list[dict]) -> dict:
    effective = _normalise_profile(profile)
    active_goal_ids = list(effective.get("active_goal_ids") or [])
    for event in events:
        if event.get("type") != "goal_set":
            continue
        goal_id = event.get("goal_id")
        if goal_id and goal_id not in active_goal_ids:
            active_goal_ids.append(goal_id)
        for key in ("exam_date", "target_outcome"):
            if event.get(key):
                effective[key] = event[key]
    effective["active_goal_ids"] = active_goal_ids
    return effective


def _study_schedule() -> dict:
    if not SCHEDULE_YAML.exists():
        return {}
    return load_yaml(SCHEDULE_YAML).get("study_schedule", {})


def _daily_preference(profile: dict) -> int:
    prefs = profile.get("session_preferences") or {}
    if prefs.get("max_daily_concepts"):
        try:
            return max(1, int(prefs["max_daily_concepts"]))
        except (TypeError, ValueError):
            pass
    try:
        sessions = int(prefs.get("sessions_per_day") or 1)
        per_session = int(prefs.get("concepts_per_session") or 4)
    except (TypeError, ValueError):
        return 4
    return max(1, sessions * per_session)


def _priority_scores() -> dict[str, dict]:
    if not PRIORITY_YAML.exists():
        return {}
    raw = load_yaml(PRIORITY_YAML).get("study_priority", {})
    entries = raw.get("concepts", [])
    if not entries:
        return {}
    total = max(len(entries), 1)
    scores = {}
    for entry in entries:
        rank = int(entry.get("rank") or total)
        centrality = entry.get("composite_score", 0)
        scores[entry["id"]] = {
            "rank": rank,
            "centrality": float(centrality or 0),
            "rank_score": max(0.0, (total - rank + 1) / total),
        }
    return scores


def _upcoming_schedule_refs(schedule: dict, limit_days: int = 10) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = defaultdict(list)
    today = date.today()
    seen_days = 0
    for day_entry in schedule.get("days", []):
        try:
            day = date.fromisoformat(day_entry.get("date", ""))
        except ValueError:
            continue
        if day < today:
            continue
        seen_days += 1
        if seen_days > limit_days:
            break
        for concept in day_entry.get("concepts", []):
            cid = concept.get("id")
            if cid:
                refs[cid].append(f"schedule:{day}:{cid}")
    return refs


def _evaluate_scored_events(events: list[dict], now: datetime) -> dict[str, list[tuple[dict, float]]]:
    grouped: dict[str, list[tuple[dict, float]]] = defaultdict(list)
    for event in _recent(events, now, RECENT_RECALL_DAYS):
        cid = _concept_id(event)
        score = _event_score(event)
        if cid and score is not None:
            grouped[cid].append((event, score))
    return grouped


def evaluate_beliefs() -> list[dict]:
    _ensure_files()
    now = datetime.now(timezone.utc)
    updated_at = _now_iso()
    events = load_events()
    profile = _effective_profile(load_profile(), events)
    labels = _node_labels()
    scored = _evaluate_scored_events(events, now)
    by_concept: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        cid = _concept_id(event)
        if cid:
            by_concept[cid].append(event)

    beliefs: dict[str, dict] = {}
    active_derivations: list[dict] = []
    concept_ids = set(by_concept) | set(scored)

    for cid in sorted(concept_ids):
        recent_scores = scored.get(cid, [])
        recent_score_events = [event for event, _ in recent_scores]
        scores = [score for _, score in recent_scores]
        avg = sum(scores) / len(scores) if scores else None

        struggle_reports = [
            event
            for event in _recent(by_concept.get(cid, []), now, SELF_REPORT_DAYS)
            if event.get("type") == "self_report" and event.get("polarity") == "struggle"
        ]
        positive_reports = [
            event
            for event in _recent(by_concept.get(cid, []), now, SELF_REPORT_DAYS)
            if event.get("type") == "self_report" and event.get("polarity") in {"mastered", "confident", "understood"}
        ]
        low_recent = bool(scores) and avg is not None and avg < STRUGGLE_THRESHOLD
        positive_recent = [event for event, score in recent_scores if score >= 0.66]

        if low_recent or struggle_reports:
            support = []
            confidence_parts = []
            if low_recent:
                derivation_id = f"just_low_recent_recall:{cid}"
                support += [event["id"] for event in recent_score_events] + [derivation_id]
                confidence_parts.append(
                    0.55
                    + (STRUGGLE_THRESHOLD - float(avg)) / STRUGGLE_THRESHOLD * 0.30
                    + min(len(scores), 3) / 3 * 0.10
                )
                active_derivations.append(
                    {
                        "id": derivation_id,
                        "rule_id": "low_recent_recall",
                        "consequent": f"struggling_with:{cid}",
                        "status": "in",
                        "support": [event["id"] for event in recent_score_events],
                        "measure": {
                            "average": round(float(avg), 3),
                            "attempts": len(scores),
                            "threshold": STRUGGLE_THRESHOLD,
                            "window_days": RECENT_RECALL_DAYS,
                        },
                    }
                )
            if struggle_reports:
                derivation_id = f"just_recent_struggle_report:{cid}"
                support += [event["id"] for event in struggle_reports] + [derivation_id]
                confidence_parts.append(0.82)
                active_derivations.append(
                    {
                        "id": derivation_id,
                        "rule_id": "recent_struggle_report",
                        "consequent": f"struggling_with:{cid}",
                        "status": "in",
                        "support": [event["id"] for event in struggle_reports],
                    }
                )
            opposition = [event["id"] for event in positive_recent + positive_reports]
            beliefs[f"struggling_with:{cid}"] = _belief(
                "struggling_with",
                cid,
                "in",
                max(confidence_parts),
                support,
                opposition,
                updated_at,
                labels,
                "Recent evidence suggests this concept is causing trouble.",
            )
        elif recent_scores or positive_reports:
            opposition = [event["id"] for event in positive_recent + positive_reports]
            confidence = float(avg) if avg is not None else 0.55
            beliefs[f"struggling_with:{cid}"] = _belief(
                "struggling_with",
                cid,
                "out",
                confidence,
                [],
                opposition,
                updated_at,
                labels,
                "Recent evidence does not currently support a struggle assumption.",
            )

    for cid in sorted(concept_ids):
        recent_scores = scored.get(cid, [])
        scores = [score for _, score in recent_scores]
        avg = sum(scores) / len(scores) if scores else None
        explicit_mastery = [
            event
            for event in by_concept.get(cid, [])
            if event.get("type") == "mastery_mark" and event.get("mastered", True) is not False
        ]
        mastery_reports = [
            event
            for event in _recent(by_concept.get(cid, []), now, SELF_REPORT_DAYS)
            if event.get("type") == "self_report" and event.get("polarity") in {"mastered", "confident", "understood"}
        ]
        high_recent = avg is not None and avg >= MASTERY_THRESHOLD and len(scores) >= 3
        support = []
        confidence_parts = []
        if high_recent:
            derivation_id = f"just_high_recent_recall:{cid}"
            support += [event["id"] for event, _ in recent_scores] + [derivation_id]
            confidence_parts.append(min(0.95, float(avg) + min(len(scores) - 3, 3) * 0.02))
            active_derivations.append(
                {
                    "id": derivation_id,
                    "rule_id": "high_recent_recall",
                    "consequent": f"mastered:{cid}",
                    "status": "in",
                    "support": [event["id"] for event, _ in recent_scores],
                    "measure": {
                        "average": round(float(avg), 3),
                        "attempts": len(scores),
                        "threshold": MASTERY_THRESHOLD,
                        "window_days": RECENT_RECALL_DAYS,
                    },
                }
            )
        if explicit_mastery:
            derivation_id = f"just_explicit_mastery:{cid}"
            support += [event["id"] for event in explicit_mastery] + [derivation_id]
            confidence_parts.append(0.95)
            active_derivations.append(
                {
                    "id": derivation_id,
                    "rule_id": "explicit_mastery",
                    "consequent": f"mastered:{cid}",
                    "status": "in",
                    "support": [event["id"] for event in explicit_mastery],
                }
            )
        if mastery_reports:
            support += [event["id"] for event in mastery_reports]
            confidence_parts.append(0.72)

        struggle = beliefs.get(f"struggling_with:{cid}")
        opposition = []
        if struggle and struggle["status"] == "in" and struggle["confidence"] > 0.7:
            opposition.append(f"belief:{struggle['id']}")

        if support or opposition:
            status = "out" if opposition and max(confidence_parts or [0]) < 0.95 else "in"
            confidence = max(confidence_parts or [0.55])
            if status == "out":
                confidence = max(confidence, struggle["confidence"] if struggle else 0.7)
            beliefs[f"mastered:{cid}"] = _belief(
                "mastered",
                cid,
                status,
                confidence,
                support,
                opposition,
                updated_at,
                labels,
                "Mastery is tentative and can be retracted by stronger struggle evidence.",
            )

    for struggle in [item for item in beliefs.values() if item["kind"] == "struggling_with" and item["status"] == "in"]:
        dependent = struggle["subject"]
        for candidate in _prerequisite_candidates(dependent):
            cid = candidate["concept_id"]
            relation = candidate["relation"]
            derivation_id = f"just_one_hop_prerequisite_gap:{dependent}:{cid}"
            support = [f"belief:{struggle['id']}", _relation_ref(relation), derivation_id]
            mastered = beliefs.get(f"mastered:{cid}")
            opposition = [f"belief:{mastered['id']}"] if mastered and mastered["status"] == "in" else []
            confidence = struggle["confidence"] * candidate["weight"]
            if confidence < 0.45:
                continue
            status = "out" if opposition and confidence < 0.75 else "in"
            belief_id = f"likely_prerequisite_gap:{cid}"
            existing = beliefs.get(belief_id)
            if existing and existing["confidence"] >= confidence:
                existing["support"] = _unique(existing["support"] + support)
                existing["opposition"] = _unique(existing["opposition"] + opposition)
                continue
            beliefs[belief_id] = _belief(
                "likely_prerequisite_gap",
                cid,
                status,
                confidence,
                support,
                opposition,
                updated_at,
                labels,
                f"One-hop ontology relation links this concept to struggle with {labels.get(dependent, dependent)}.",
            )
            active_derivations.append(
                {
                    "id": derivation_id,
                    "rule_id": "one_hop_prerequisite_gap",
                    "consequent": belief_id,
                    "status": status,
                    "support": [f"belief:{struggle['id']}", _relation_ref(relation)],
                    "relation_type": relation["rel_type"],
                    "dependent_concept": dependent,
                }
            )

    schedule = _study_schedule()
    if schedule:
        allowed = _daily_preference(profile)
        days = max(int(schedule.get("total_days_available") or len(schedule.get("days", [])) or 1), 1)
        scheduled = int(schedule.get("total_concepts_scheduled") or 0)
        required = scheduled / days
        capacity = int(schedule.get("capacity_per_day") or 0)
        overloaded = bool(schedule.get("warning")) or required > allowed or (capacity and capacity > allowed)
        confidence = min(0.95, 0.55 + max(required - allowed, 0) / max(allowed, 1) * 0.35)
        if schedule.get("warning"):
            confidence = max(confidence, 0.82)
        support = ["profile:session_preferences", "study_schedule.yaml", "just_schedule_capacity_check"]
        opposition = [] if overloaded else ["study_schedule.yaml"]
        beliefs["overloaded_schedule:true"] = _belief(
            "overloaded_schedule",
            "true",
            "in" if overloaded else "out",
            confidence if overloaded else 0.6,
            support if overloaded else [],
            opposition,
            updated_at,
            labels,
            f"Schedule asks for about {required:.1f} concepts/day; preference allows {allowed}.",
        )
        active_derivations.append(
            {
                "id": "just_schedule_capacity_check",
                "rule_id": "schedule_capacity_check",
                "consequent": "overloaded_schedule:true",
                "status": "in" if overloaded else "out",
                "support": ["profile:session_preferences", "study_schedule.yaml"],
                "measure": {"required_daily_concepts": round(required, 2), "preferred_daily_concepts": allowed},
            }
        )

    for event in events:
        if event.get("type") != "user_assertion":
            continue
        kind = event.get("kind")
        subject = event.get("subject") or event.get("concept_id")
        belief_id = event.get("belief_id") or (f"{kind}:{subject}" if kind and subject else None)
        if not belief_id:
            continue
        if not kind or not subject:
            kind, subject = belief_id.split(":", 1)
        status = event.get("status", "in")
        existing = beliefs.get(belief_id)
        opposition = []
        support = [event["id"]]
        if existing and existing.get("status") != status:
            opposition = existing.get("support", [])
        beliefs[belief_id] = _belief(
            kind,
            subject,
            status,
            float(event.get("confidence", 0.95)),
            support,
            opposition,
            updated_at,
            labels,
            "Explicit user assertion.",
        )

    _add_recommendation_beliefs(beliefs, active_derivations, schedule, labels, updated_at)

    output = sorted(beliefs.values(), key=lambda item: (item["kind"], item["subject"], item["id"]))
    save_yaml(LEARNER_BELIEFS_YAML, {"beliefs": output})
    _save_active_derivations(active_derivations)
    return output


def _add_recommendation_beliefs(
    beliefs: dict[str, dict],
    active_derivations: list[dict],
    schedule: dict,
    labels: dict[str, str],
    updated_at: str,
) -> None:
    priority = _priority_scores()
    upcoming = _upcoming_schedule_refs(schedule)
    scores: dict[str, float] = defaultdict(float)
    support: dict[str, list[str]] = defaultdict(list)

    for belief in beliefs.values():
        if belief["status"] != "in":
            continue
        if belief["kind"] == "struggling_with":
            scores[belief["subject"]] += 0.55 * belief["confidence"]
            support[belief["subject"]].append(f"belief:{belief['id']}")
        elif belief["kind"] == "likely_prerequisite_gap":
            scores[belief["subject"]] += 0.45 * belief["confidence"]
            support[belief["subject"]].append(f"belief:{belief['id']}")

    for cid, refs in upcoming.items():
        scores[cid] += 0.28
        support[cid] += refs[:2]

    if not scores:
        for cid, data in sorted(priority.items(), key=lambda item: item[1]["rank"])[:12]:
            scores[cid] += 0.20 * data["rank_score"]
            support[cid].append(f"priority:{data['rank']}:{cid}")

    for cid in list(scores):
        if cid in priority:
            data = priority[cid]
            scores[cid] += 0.20 * data["centrality"]
            support[cid].append(f"priority:{data['rank']}:{cid}")

    mastered_in = {belief["subject"] for belief in beliefs.values() if belief["kind"] == "mastered" and belief["status"] == "in"}
    ranked = [
        (cid, score)
        for cid, score in scores.items()
        if cid not in mastered_in and labels.get(cid)
    ]
    ranked.sort(key=lambda item: item[1], reverse=True)

    for cid, score in ranked[:12]:
        derivation_id = f"just_recommend_next:{cid}"
        refs = _unique(support[cid] + [derivation_id])
        confidence = min(0.95, max(0.35, score))
        beliefs[f"recommended_next:{cid}"] = _belief(
            "recommended_next",
            cid,
            "in",
            confidence,
            refs,
            [],
            updated_at,
            labels,
            "Recommended by current struggle, prerequisite, schedule, and centrality signals.",
        )
        active_derivations.append(
            {
                "id": derivation_id,
                "rule_id": "recommend_next",
                "consequent": f"recommended_next:{cid}",
                "status": "in",
                "support": refs[:-1],
                "measure": {"score": round(score, 3)},
            }
        )


def load_beliefs(recompute: bool = True) -> list[dict]:
    if recompute:
        return evaluate_beliefs()
    _ensure_files()
    return list(load_yaml(LEARNER_BELIEFS_YAML).get("beliefs", []) or [])


def recommend_next(limit: int = 8) -> list[dict]:
    beliefs = evaluate_beliefs()
    recs = [belief for belief in beliefs if belief["kind"] == "recommended_next" and belief["status"] == "in"]
    recs.sort(key=lambda item: item["confidence"], reverse=True)
    return recs[:limit]


def _resolve_relation_ref(ref: str) -> dict | None:
    _, source, rel_type, target = ref.split(":", 3)
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT r.id, r.rel_type, r.source_id, r.target_id, r.note, r.quote,
                   s.label AS source_label, t.label AS target_label
            FROM relations r
            LEFT JOIN nodes s ON s.id = r.source_id
            LEFT JOIN nodes t ON t.id = r.target_id
            WHERE r.source_id = ? AND r.rel_type = ? AND r.target_id = ?
            LIMIT 1
            """,
            (source, rel_type, target),
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _resolve_schedule_ref(ref: str) -> dict:
    parts = ref.split(":", 2)
    if len(parts) < 3:
        return {"ref": ref}
    _, day, concept_id = parts
    schedule = _study_schedule()
    for day_entry in schedule.get("days", []):
        if day_entry.get("date") != day:
            continue
        for concept in day_entry.get("concepts", []):
            if concept.get("id") == concept_id:
                return {"date": day, "concept": concept}
    return {"date": day, "concept_id": concept_id}


def _resolve_priority_ref(ref: str) -> dict:
    _, rank, concept_id = ref.split(":", 2)
    priority = _priority_scores().get(concept_id, {})
    return {"rank": int(rank), "concept_id": concept_id, **priority}


def _resolve_ref(ref: str, events: dict[str, dict], derivations: dict[str, dict], beliefs: dict[str, dict]) -> dict:
    if ref.startswith("evt_"):
        return {"kind": "event", "ref": ref, "data": events.get(ref)}
    if ref.startswith("just_"):
        return {"kind": "justification", "ref": ref, "data": derivations.get(ref)}
    if ref.startswith("belief:"):
        belief_id = ref.removeprefix("belief:")
        return {"kind": "belief", "ref": ref, "data": beliefs.get(belief_id)}
    if ref.startswith("rel:"):
        return {"kind": "relation", "ref": ref, "data": _resolve_relation_ref(ref)}
    if ref.startswith("schedule:"):
        return {"kind": "schedule", "ref": ref, "data": _resolve_schedule_ref(ref)}
    if ref.startswith("priority:"):
        return {"kind": "priority", "ref": ref, "data": _resolve_priority_ref(ref)}
    if ref.startswith("profile:"):
        return {"kind": "profile", "ref": ref, "data": load_profile().get(ref.split(":", 1)[1])}
    return {"kind": "reference", "ref": ref, "data": None}


def explain_belief(belief_id: str) -> dict:
    beliefs_list = evaluate_beliefs()
    beliefs = {belief["id"]: belief for belief in beliefs_list}
    belief = beliefs.get(belief_id)
    if not belief:
        return {"error": "not found", "belief_id": belief_id}

    event_map = {event["id"]: event for event in load_events()}
    justifications = _load_justifications()
    derivations = {item["id"]: item for item in justifications.get("active_derivations", [])}
    return {
        "belief": belief,
        "support": [_resolve_ref(ref, event_map, derivations, beliefs) for ref in belief.get("support", [])],
        "opposition": [_resolve_ref(ref, event_map, derivations, beliefs) for ref in belief.get("opposition", [])],
        "provenance": {
            "events": str(LEARNER_EVENTS_JSONL),
            "belief_cache": str(LEARNER_BELIEFS_YAML),
            "justifications": str(LEARNER_JUSTIFICATIONS_YAML),
            "ontology": str(DB_PATH),
        },
    }
