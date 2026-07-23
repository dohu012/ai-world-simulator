"""Deterministically export public domain models as JSON Schema."""

import json
from pathlib import Path

from app.domain.schemas import DOMAIN_MODELS


def schema_output_dir() -> Path:
    """Return the repository-level schema output directory."""
    return Path(__file__).resolve().parents[3] / "schemas" / "domain"


def export_schemas(output_dir: Path | None = None) -> dict[str, str]:
    """Export every public model and return filename-to-content mappings."""
    destination = output_dir or schema_output_dir()
    destination.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, str] = {}
    for slug, model in DOMAIN_MODELS.items():
        content = json.dumps(
            model.model_json_schema(mode="serialization"),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        content += "\n"
        filename = f"{slug}.schema.json"
        (destination / filename).write_text(content, encoding="utf-8", newline="\n")
        rendered[filename] = content
    return rendered


if __name__ == "__main__":
    export_schemas()
