---
name: learner-model
description: >
  Use this subskill whenever the user asks the course assistant to remember the
  student, update learning goals, inspect struggles or mastery, explain study
  recommendations, record learner observations, or reason about student memory.
  It manages the FAB learner dependency network in learner-model/.
---

# Subskill: Learner Model

Use the learner dependency network as a JTMS-lite memory for the student.
The durable facts are append-only events, profile preferences, and explicit
justification rules. The generated belief cache is never the authority.

---

## Course Framing

Use course language when explaining the model:

- A dependency network supplements the ontology/constraint network with local
  memory of tentative assumptions, justifications, provenance, contradictions,
  and current `in` / `out` labels.
- Truth maintenance means making, modifying, or retracting assumptions during
  debugging.
- Dependency-directed reasoning traces a bug or confusion back to supporting
  assumptions, prerequisites, and justifications, then propagates the fix.

---

## Files

| File | Purpose |
|---|---|
| `learner-model/profile.yaml` | Student goals and preferences: `student_name`, `exam_date`, `target_outcome`, `available_days`, `session_preferences`, `active_goal_ids` |
| `learner-model/events.jsonl` | Append-only learner observations |
| `learner-model/beliefs.yaml` | Generated cache of `in` / `out` learner beliefs |
| `learner-model/justifications.yaml` | Rule definitions and active derivations |
| `ontology_core/learner_model.py` | Loader, evaluator, explainer, recommender |

Do not edit `beliefs.yaml` directly. Recompute it with the learner model module
after appending events or changing profile preferences.

---

## Core Rules

- Treat learner facts as tentative unless the event is an explicit
  `user_assertion`.
- Append events rather than rewriting history.
- Recompute beliefs after new events.
- Ground explanations in `support` and `opposition` IDs from the belief.
- Prefer SQLite for exact ontology graph lookups in app code.
- Never silently overwrite profile goals. If a goal changes, confirm with the
  user or add a superseding `goal_set` event.

---

## Event Examples

```json
{"type":"flashcard_rating","concept_id":"credit_assignment","rating":0,"source":"flashcards"}
{"type":"self_report","concept_id":"truth_maintenance","polarity":"struggle","text":"I don't get in/out labels"}
{"type":"goal_set","goal_id":"exam_pass","exam_date":"2026-06-01","target_outcome":"pass the exam"}
{"type":"mastery_mark","concept_id":"constraint_network","mastered":true}
```

The learner model fills in `id`, `ts`, and default `source` when missing.

---

## Python API

Use these functions from `ontology_core.learner_model`:

```python
load_profile()
save_profile(profile)
append_event(event)
load_events(limit=None, concept_id=None)
evaluate_beliefs()
explain_belief(belief_id)
recommend_next(limit=8)
```

For command-line checks, use short `uv run python -c` snippets that call these
functions. Do not write custom SQLite inspection scripts for manual querying.

---

## Typical Workflows

### Record an observation

1. Append an event with `append_event(...)`.
2. Run `evaluate_beliefs()`.
3. Tell the user which beliefs moved `in` or `out`.

### Explain a recommendation or struggle

1. Locate the belief ID, such as `struggling_with:credit_assignment`.
2. Run `explain_belief(belief_id)`.
3. Summarize the `support`, `opposition`, and provenance. Avoid implying the
   belief is permanent; it is the current truth-maintained label.

### Update goals

1. If changing durable preferences, use `save_profile`.
2. If changing an active exam goal, prefer appending a `goal_set` event after
   confirming with the user.
3. Recompute beliefs so schedule overload and recommendations update.

---

## HTTP API

The local study hub exposes:

```text
GET /api/learner/profile
PUT /api/learner/profile
GET /api/learner/events?limit=50&concept_id=x
POST /api/learner/events
GET /api/learner/beliefs
GET /api/learner/explain/<urlencoded belief_id>
GET /api/learner/recommendations?limit=8
```

Use the UI Learner tab for quick inspection, event capture, and explanation
drawers.
