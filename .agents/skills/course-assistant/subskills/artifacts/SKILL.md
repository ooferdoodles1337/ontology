# Subskill: Artifacts

Generates study artifacts from the FAB 2026 ontology and course notes.
Each artifact is a self-contained file the student can open directly in a browser.

---

## Available Artifact Types

| Type | Subskill | Trigger phrases |
|---|---|---|
| Multiple-choice quiz | `subskills/multiple-choice-quiz/SKILL.md` | "make a quiz", "quiz me on X", "practice questions", "test on module N" |
| Flashcards (spaced repetition + TD credit) | `subskills/flashcards/SKILL.md` | "make flashcards", "generate a flashcard deck", "spaced repetition", "study with flashcards", "flashcards for module N" |

Read the user's request, pick one artifact type, load its subskill, and follow its instructions.

---

## Shared Conventions

- **Output directory:** `artifacts/`
- **File naming:** `<type>_<topic_slug>.<ext>` — e.g. `quiz_search.html`, `flashcards_module3.html`
- **Always write using the Write tool** — never shell redirection or heredocs
- **After writing**, report the output path relative to project root and one-line open instruction
- **Self-contained:** every artifact must work by opening the file directly — no local server, no external data files

---

## Adding a New Artifact Type

When a new artifact type is built, add a directory under `subskills/` with its own `SKILL.md`
and register it in the table above.
