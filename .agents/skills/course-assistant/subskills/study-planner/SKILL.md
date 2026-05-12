# Subskill: Study Planner

Generates a day-by-day study schedule from the ontology using a
Constraint Satisfaction Problem (CSP) solver:

- **Variables**: one per concept — the calendar date on which to study it
- **Domains**: dates from tomorrow to exam day − 1
- **Constraints**:
  1. *Module ordering* — concepts from module M appear before module M+1
     (enforced via AC-3 domain propagation)
  2. *Daily capacity* — at most `sessions_per_day × concepts_per_session` concepts per day
  3. *Feasibility* — detected and reported if there is not enough time

After propagation, a greedy left-to-right assignment fills sessions in module order.

---

## When to Load This Subskill

User says things like:

- "make me a study plan"
- "build a schedule for the exam"
- "I have until June 1st — plan my study"
- "schedule the concepts for the next two weeks"
- "show my study schedule"
- "I've mastered credit assignment, mark it done"
- "initialise my mastery tracker"

---

## Commands

All commands run from the project root via `uv run python scripts/study_scheduler.py`.

### Generate a schedule

```bash
uv run python scripts/study_scheduler.py plan --exam YYYY-MM-DD
uv run python scripts/study_scheduler.py plan --exam 2026-06-01 --sessions-per-day 2 --concepts-per-session 4
```

Options:
- `--exam YYYY-MM-DD` — exam date (required)
- `--sessions-per-day N` — study sessions per day (default 2)
- `--concepts-per-session N` — concepts per session (default 4)

**What this produces:**
- Prints a one-week preview to the console
- Saves `knowledge-base/study_schedule.yaml` (machine-readable; user can edit)
- Writes `artifacts/study_schedule_<date>.md` (checklist format, open in any Markdown viewer)

If there are not enough days to cover all concepts, the planner reports the
shortfall, limits the schedule to what fits, and suggests extending the timeline
or reducing scope with `concept_ranker.py`.

### Display the current schedule

```bash
uv run python scripts/study_scheduler.py show
uv run python scripts/study_scheduler.py show --full   # include past days
```

Shows today's sessions prominently. Use `--full` to display the entire schedule
from the beginning.

### Mark a concept as mastered

```bash
uv run python scripts/study_scheduler.py mark --concept credit_assignment
uv run python scripts/study_scheduler.py mark --concept credit_assignment --unmark
```

Updates `knowledge-base/mastery.yaml`. After marking several concepts, regenerate
the schedule with `plan` to get an updated plan that excludes mastered concepts.

### Initialise the mastery tracker

```bash
uv run python scripts/study_scheduler.py init-mastery
uv run python scripts/study_scheduler.py init-mastery --force   # overwrite existing
```

Creates `knowledge-base/mastery.yaml` with all 315 concepts set to `mastered: false`.
Run this once before using `mark`. If the file already exists, `--force` is required.

---

## Typical Session Flow

1. **First time:** initialise mastery tracker:
   ```bash
   uv run python scripts/study_scheduler.py init-mastery
   ```

2. **Generate schedule:**
   ```bash
   uv run python scripts/study_scheduler.py plan --exam <date>
   ```
   Tell the user the output paths and offer to open the markdown file.

3. **Check today's sessions:**
   ```bash
   uv run python scripts/study_scheduler.py show
   ```

4. **After studying:** mark concepts mastered:
   ```bash
   uv run python scripts/study_scheduler.py mark --concept <id>
   ```

5. **Regenerate** with updated mastery:
   ```bash
   uv run python scripts/study_scheduler.py plan --exam <date>
   ```

---

## How to Find Concept IDs

When the user says "mark X as mastered" and you need the concept ID:

```bash
sqlite-utils query ontology.db "SELECT id, label FROM nodes WHERE label LIKE '%keyword%'" --table
```

Or search the current schedule:
```bash
uv run python scripts/study_scheduler.py show
```

---

## Output Files

| File | Purpose |
|------|---------|
| `knowledge-base/mastery.yaml` | Per-concept mastery flags; user-editable |
| `knowledge-base/study_schedule.yaml` | Full schedule in YAML; user-editable |
| `artifacts/study_schedule_<date>.md` | Printable checklist in Markdown |

---

## Interpreting Warnings

**"Not enough time to study all N concepts"** — the AC-3 feasibility check detected
that the available days × daily capacity < total unmastered concepts.

Suggested responses to the user:
- Extend the timeline (move up the study start date or push back the exam)
- Reduce scope: first run `concept_ranker.py rank` and focus on the top-scored concepts
- Increase sessions per day or concepts per session
- Mark concepts already familiar as mastered before generating the schedule
