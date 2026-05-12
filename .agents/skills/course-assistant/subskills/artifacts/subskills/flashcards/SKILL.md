# Subskill: Generate Flashcards

Generates a self-contained HTML flashcard app implementing
**Prerequisite-Aware Spaced Repetition with TD Credit Assignment**.

The flashcard system is not a standard flashcard app. It embeds the full
ontology prerequisite graph into the HTML and runs the following algorithm
entirely in the browser (no server, no LLM, no backend):

**Algorithm (all in-browser JS):**
- Each card has a mastery estimate V ∈ [0,1] — the TD value function
- On recall, TD error δ = actual_score − V updates the card's mastery
- Credit/blame propagates through the prerequisite graph (BFS, max 3 hops):
  - Fail: backward propagation — blame ancestors by δ × 0.5^hop
  - Pass: forward propagation — boost dependents by δ × 0.3^hop
- SM-2 scheduling sets the next review interval
- Card selection targets the weakest frontier (deliberate practice)
- State persisted in localStorage — works offline, no account needed

---

## When to Load This Subskill

User says things like:

- "make me flashcards"
- "generate a flashcard deck"
- "I want to study with flashcards"
- "create flashcards for module 3"
- "make spaced repetition cards on search"
- "flashcards for credit assignment"

---

## Command

```bash
uv run python scripts/flashcard_generator.py generate [options]
```

### Scope options

| Option | Example | Effect |
|--------|---------|--------|
| *(none)* | | Full deck — all 315 concepts |
| `--module N [N...]` | `--module 1 2` | Concepts from those course modules |
| `--doc-id ID [ID...]` | `--doc-id notes_credit_assignment` | Concepts from those source documents |
| `--type TYPE` | `--type concept` | Filter by node type: `concept` (default), `person`, `example`, `all` |
| `--slug SLUG` | `--slug search_module` | Custom filename slug |

### Examples

```bash
# Full deck (all concepts)
uv run python scripts/flashcard_generator.py generate

# Module 1 only
uv run python scripts/flashcard_generator.py generate --module 1

# Modules 1–3
uv run python scripts/flashcard_generator.py generate --module 1 2 3 --slug modules_1_to_3

# From a specific document
uv run python scripts/flashcard_generator.py generate --doc-id notes_search

# Concepts + people
uv run python scripts/flashcard_generator.py generate --type all --slug full_with_people
```

---

## Output

The command writes a single HTML file to `artifacts/flashcards_<slug>.html`.

Tell the user:
1. The output path: `artifacts/flashcards_<slug>.html`
2. How many cards and prerequisite edges are in the deck
3. Open instruction: *"Open `artifacts/flashcards_<slug>.html` in any browser. No internet needed after the page loads."*

---

## How the UI Works (explain to user if asked)

**Front of card:** concept name, current mastery % bar, module badge → click "Reveal"

**Back of card:** full description + four rating buttons:
- ✗ Forgot (resets interval to 1 day)
- ≈ Hard (small interval increase, ease penalty)
- ✓ Good (normal SM-2 interval)
- ★ Easy (larger interval, ease bonus)

**Credit propagation panel** (appears after rating):
- Shows which prerequisite concepts were penalised (on fail) or boosted (on pass)
- Displays hop distance and mastery delta for each affected concept
- This is the key feature that distinguishes this from standard Anki

**Mastery overview** (top of page):
- Ring showing % mastered (≥ 70%)
- Histogram of mastery distribution across all cards

**Dashboard** (bottom):
- Weakest 8 concepts by mastery score
- Upcoming review queue with due times

**State:** persisted in localStorage — progress survives page refreshes and browser restarts.

---

## Finding doc-id Values

To list available document IDs for `--doc-id`:

```bash
sqlite-utils query ontology.db "SELECT doc_id, title, course_order FROM documents ORDER BY course_order" --table
```

## Finding module Numbers

Modules correspond to `course_order` in the documents table. Check:

```bash
sqlite-utils query ontology.db "SELECT course_order as module, title FROM documents ORDER BY course_order" --table
```
