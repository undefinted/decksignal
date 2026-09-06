from pathlib import Path

from openpptbench.validate import validate_path


def test_published_tasks_validate():
    root = Path(__file__).parents[1]
    errors = validate_path(
        root / "benchmark" / "tasks", root / "benchmark" / "schema" / "task.schema.json"
    )
    assert errors == []

