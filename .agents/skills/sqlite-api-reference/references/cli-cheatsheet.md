# sqlite-utils CLI Cheatsheet

Official docs: https://sqlite-utils.datasette.io/en/stable/cli.html

Prefer `uv run sqlite-utils ...` in this repository.

## Inspect A Database

```bash
uv run sqlite-utils tables ontology.db --counts
uv run sqlite-utils schema ontology.db
uv run sqlite-utils schema ontology.db nodes
uv run sqlite-utils indexes ontology.db
uv run sqlite-utils triggers ontology.db
```

## Run SQL

```bash
uv run sqlite-utils query ontology.db "select * from nodes limit 10" --table
uv run sqlite-utils ontology.db "select count(*) as count from relations" --table
```

Common output flags:

```bash
--table
--csv
--tsv
--nl
--arrays
```

## Browse Rows

```bash
uv run sqlite-utils rows ontology.db nodes --limit 20 --table
uv run sqlite-utils rows ontology.db nodes --where "id like '%search%'" --table
uv run sqlite-utils rows ontology.db relations --order rel_type --table
```

## Insert Or Import Data

Check local syntax first:

```bash
uv run sqlite-utils insert --help
uv run sqlite-utils upsert --help
```

Typical shapes:

```bash
uv run sqlite-utils insert my.db table rows.json --pk id
uv run sqlite-utils insert my.db table rows.csv --csv
uv run sqlite-utils upsert my.db table rows.json --pk id
```

## Full-Text Search

Check exact installed flags first:

```bash
uv run sqlite-utils enable-fts --help
uv run sqlite-utils search --help
```

Typical shapes:

```bash
uv run sqlite-utils enable-fts my.db documents title body
uv run sqlite-utils search my.db documents "search terms" --table
uv run sqlite-utils populate-fts my.db documents title body
uv run sqlite-utils rebuild-fts my.db documents
uv run sqlite-utils disable-fts my.db documents
```

## Schema Changes

```bash
uv run sqlite-utils create-table --help
uv run sqlite-utils add-column --help
uv run sqlite-utils transform --help
uv run sqlite-utils add-foreign-key --help
uv run sqlite-utils create-index --help
```

Run `--help` before using schema-changing commands because flags vary by command and should match the installed package.

## Maintenance

```bash
uv run sqlite-utils vacuum ontology.db
uv run sqlite-utils analyze ontology.db
uv run sqlite-utils optimize ontology.db
uv run sqlite-utils dump ontology.db
```

## Project Convention

For ontology database inspection, prefer:

```bash
uv run sqlite-utils query ontology.db "..." --table
```

Do not write one-off Python scripts just to inspect SQLite data when `sqlite-utils query` can answer the question.
