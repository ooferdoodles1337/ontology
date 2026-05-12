"""YAML loading and saving helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class FoldedString(str):
    """String marker used to emit readable folded YAML scalars."""


def _represent_folded_string(dumper: yaml.Dumper, value: FoldedString) -> yaml.ScalarNode:
    style = ">" if ("\n" in value or len(value) > 80) else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


yaml.add_representer(FoldedString, _represent_folded_string, Dumper=yaml.Dumper)


def _wrap_long_strings(value: Any) -> Any:
    if isinstance(value, str) and ("\n" in value or len(value) > 80):
        return FoldedString(value)
    if isinstance(value, list):
        return [_wrap_long_strings(item) for item in value]
    if isinstance(value, dict):
        return {key: _wrap_long_strings(item) for key, item in value.items()}
    return value


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def save_yaml(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(
            _wrap_long_strings(data),
            handle,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=120,
        )

