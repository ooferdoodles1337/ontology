#!/usr/bin/env python3
"""Rename a relation type across relations.yaml and relation-schema.yaml.

Usage: uv run python scripts/rename_relation_type.py OLD-NAME NEW-NAME
"""

import sys
import yaml

import _bootstrap  # noqa: F401
from ontology_core.paths import RELATION_SCHEMA_YAML, RELATIONS_YAML

RELATIONS = RELATIONS_YAML
SCHEMA = RELATION_SCHEMA_YAML


def main():
    if len(sys.argv) != 3:
        print("Usage: rename_relation_type.py OLD-NAME NEW-NAME")
        sys.exit(1)
    old, new = sys.argv[1], sys.argv[2]

    # --- relations.yaml ---
    rels_data = yaml.safe_load(RELATIONS.read_text())
    relations = rels_data.get("relations") or []
    renamed = 0
    for r in relations:
        if r.get("type") == old:
            r["type"] = new
            renamed += 1

    with open(RELATIONS, "w") as f:
        f.write("# ============================================================\n")
        f.write("# FAB 2026 — Course Ontology Relations\n")
        f.write("# ============================================================\n")
        f.write("# Relation types are defined in knowledge-base/relation-schema.yaml.\n")
        f.write("# Type names are free-form strings from that vocabulary.\n")
        f.write("# ============================================================\n\n")
        yaml.dump({"relations": relations}, f, default_flow_style=False,
                  allow_unicode=True, sort_keys=False, width=100)
    print(f"relations.yaml: renamed {renamed} instances of '{old}' → '{new}'")

    # --- relation-schema.yaml ---
    schema_data = yaml.safe_load(SCHEMA.read_text()) or {}
    types = schema_data.get("relation_types") or []
    for t in types:
        if t.get("name") == old:
            t["name"] = new
            aliases = t.setdefault("aliases", [])
            if old not in aliases:
                aliases.append(old)
            print(f"relation-schema.yaml: renamed type '{old}' → '{new}', added alias")
            break
    else:
        print(f"relation-schema.yaml: type '{old}' not found — no schema entry updated")

    with open(SCHEMA, "w") as f:
        f.write("# ============================================================\n")
        f.write("# FAB 2026 — Relation Type Vocabulary\n")
        f.write("# ============================================================\n\n")
        yaml.dump(schema_data, f, default_flow_style=False,
                  allow_unicode=True, sort_keys=False, width=100)


if __name__ == "__main__":
    main()
