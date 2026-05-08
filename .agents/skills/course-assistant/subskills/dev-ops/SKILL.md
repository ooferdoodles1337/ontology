# Subskill: Dev Ops

**Purpose:** Modify the system itself — skills, instructions, and settings.

---

## Mode Gate

**This subskill requires dev mode.** Before doing anything:

1. Check whether the user has explicitly said "switch to dev mode", "we're in dev mode", or
   equivalent in the current conversation.
2. If yes: proceed.
3. If no: stop and say: *"Dev mode is required to edit system files. Say 'switch to dev mode'
   to unlock this."* Do not make any edits.

---

## Editing AGENTS.md

`AGENTS.md` is the primary instruction file. `CLAUDE.md` is a symlink to it — edit only `AGENTS.md`.

```bash
# Confirm symlink target before editing
ls -la CLAUDE.md
```

Use the Edit tool to make targeted changes. Do not rewrite the whole file unless the user
explicitly asks for a full rewrite. After editing, confirm the symlink still works:

```bash
diff AGENTS.md CLAUDE.md && echo "in sync"
```

---

## Editing or Creating Skills

For simple edits to an existing skill (e.g. fixing a query pattern, adding a step):
- Use the Edit tool on the relevant `SKILL.md` or subskill file directly.

For creating a new skill from scratch, or for evals and benchmarking:
- Delegate to the `skill-creator` skill, which has tooling for scaffolding, evals, and
  description optimization.

Skill files live at:
```
.agents/skills/<skill-name>/SKILL.md
.agents/skills/<skill-name>/subskills/<subskill>.md
```

After editing a skill, check whether its trigger description in the frontmatter still
accurately describes when it should fire. An inaccurate description causes mis-routing.

---

## Editing Settings

Project settings are at `.agents/settings.local.json` (not committed) and `.agents/settings.json`.
The `update-config` skill has detailed guidance for hooks, permissions, and environment variables.
For complex settings changes, delegate to it.

For simple edits (add a single permission, update an env var), use the Edit tool directly.

---

## What NOT to Do in Dev Mode

- Do not delete skill directories without checking that nothing references them.
- Do not rename a skill without updating its `name` frontmatter field and any callers.
- Do not edit `skills-lock.json` manually — it tracks remotely installed skills and is
  managed by the harness.
