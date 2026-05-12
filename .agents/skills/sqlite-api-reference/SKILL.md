---
name: sqlite-api-reference
description: Use this skill whenever working with sqlite-utils CLI commands, sqlite-utils command syntax, SQLite database inspection via sqlite-utils, importing or exporting data, full-text search setup, schema/table operations, or examples from the official sqlite-utils documentation. Prefer this skill even for quick sqlite-utils questions so answers match the installed CLI and the official reference.
---

# SQLite API Reference

Use this skill to answer questions about the `sqlite-utils` command-line interface and to choose the right command for local SQLite inspection or maintenance tasks.

## Reference Order

1. Prefer installed-version help for exact syntax:
   ```bash
   uv run sqlite-utils --help
   uv run sqlite-utils <command> --help
   ```
2. Use the bundled cheatsheet for common command patterns:
   `references/cli-cheatsheet.md`
3. Use the official CLI documentation for examples and deeper behavior:
   https://sqlite-utils.datasette.io/en/stable/cli.html

If the local help and online docs disagree, trust the local help for syntax because it reflects the version installed in this project.

## Answer Style

- Give the exact command to run.
- Prefer `uv run sqlite-utils ...` in this repo.
- Include `--table` for human-readable query output when the user is inspecting results.
- Use `--help` commands as the first check when the user asks about flags or subcommands.
- Keep examples grounded in the user's database path and table names when they are known.

## Useful Starting Points

```bash
uv run sqlite-utils tables ontology.db --counts
uv run sqlite-utils schema ontology.db
uv run sqlite-utils query ontology.db "select * from nodes limit 5" --table
uv run sqlite-utils ontology.db "select * from nodes limit 5" --table
uv run sqlite-utils rows ontology.db nodes --limit 5 --table
```

The `query` subcommand is the default, so `sqlite-utils DB SQL` and `sqlite-utils query DB SQL` are equivalent. Use the explicit `query` form in instructions when clarity matters.
