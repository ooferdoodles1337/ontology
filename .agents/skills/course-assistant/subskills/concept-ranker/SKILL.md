# Subskill: Concept Ranker

Ranks every concept in the ontology by its graph-theoretic importance and helps
the student decide what to study first given limited time.

**Algorithm:** composite score = PageRank (40%) + Betweenness Centrality (35%) + In-degree (25%)

- **PageRank** — prestige; concepts many others reference or depend on
- **Betweenness** — bridge concepts that connect disparate sub-topics
- **In-degree** — foundational concepts; removing them disconnects many others

---

## When to Load This Subskill

User says things like:

- "what should I study first?"
- "rank the concepts by importance"
- "I have 2 hours — what are the most important concepts?"
- "what's the most central concept in the graph?"
- "prioritise the concepts for me"
- "give me a study priority list"
- "save the concept ranking"

---

## Commands

All commands run from the project root via `uv run python scripts/concept_ranker.py`.

### Print ranked table

```bash
uv run python scripts/concept_ranker.py rank
uv run python scripts/concept_ranker.py rank --top 20
uv run python scripts/concept_ranker.py rank --type concept --top 50
uv run python scripts/concept_ranker.py rank --exclude-mastered --mastered knowledge-base/mastery.yaml
```

Options:
- `--top N` — show top N results (default 30)
- `--type concept|person|example|all` — filter by node type (default `concept`)
- `--mastered PATH` — path to mastery YAML; defaults to `knowledge-base/mastery.yaml`
- `--exclude-mastered` — hide concepts already marked mastered

### Select for a time budget

```bash
uv run python scripts/concept_ranker.py budget --hours 2
uv run python scripts/concept_ranker.py budget --hours 4 --minutes-per-concept 20
uv run python scripts/concept_ranker.py budget --hours 1.5 --mastered knowledge-base/mastery.yaml
```

Options:
- `--hours N` — study hours available (required)
- `--minutes-per-concept N` — minutes per concept (default 15)
- `--mastered PATH` — exclude mastered concepts (always excluded in budget mode)

### Save ranking to YAML

```bash
uv run python scripts/concept_ranker.py save
uv run python scripts/concept_ranker.py save --type concept
```

Writes to `knowledge-base/study_priority.yaml`. The user can inspect or edit this file.

### Write markdown artifact

```bash
uv run python scripts/concept_ranker.py report
uv run python scripts/concept_ranker.py report --top 40 --exclude-mastered
```

Writes to `artifacts/concept_priority_<date>.md`. Tell the user the path and that
they can open it in any Markdown viewer.

---

## How to Interpret Output

| Column | Meaning |
|--------|---------|
| Score | Composite 0–1. Higher = more central to the concept graph. |
| PR | PageRank. Concepts many others cite or depend on. |
| Btwn | Betweenness centrality. Concepts that bridge sub-topic clusters. |
| In | In-degree. Many relations point *to* this concept — it is foundational. |
| Out | Out-degree. This concept points *to* many others — it references widely. |

A concept with high In-degree and low Out-degree is a **leaf dependency** — many
things depend on it, but it doesn't depend on many others. Master it early.

A concept with high Betweenness is a **bridge** — understanding it unlocks
comprehension across multiple modules simultaneously.

---

## Default Flow

1. Run `rank --top 30` to show the current priority table.
2. If the user gives a time budget, run `budget --hours N`.
3. Offer to `save` the ranking to YAML and/or write a `report` to `artifacts/`.
4. If `knowledge-base/mastery.yaml` exists, offer to exclude mastered concepts
   with `--exclude-mastered`.

---

## Output Files

| File | Purpose |
|------|---------|
| `knowledge-base/study_priority.yaml` | Machine-readable ranking; edit to adjust priorities |
| `artifacts/concept_priority_<date>.md` | Human-readable markdown report |
