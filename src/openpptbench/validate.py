from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


def load_data(path: str | Path) -> Any:
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        if source.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(handle)
        return json.load(handle)


def validate_path(target: str | Path, schema_path: str | Path) -> list[dict[str, str]]:
    target_path = Path(target)
    schema = load_data(schema_path)
    files = (
        sorted(path for path in target_path.iterdir() if path.suffix.lower() in {".yaml", ".yml", ".json"})
        if target_path.is_dir()
        else [target_path]
    )
    errors: list[dict[str, str]] = []
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for path in files:
        data = load_data(path)
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "$"
            errors.append({"file": str(path), "location": location, "message": error.message})
    return errors

