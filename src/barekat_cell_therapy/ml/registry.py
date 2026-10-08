"""Registry of therapeutic response model versions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from barekat_cell_therapy.core.config import get_settings


def _registry_path(model_dir: str | Path | None = None) -> Path:
    base = Path(model_dir) if model_dir is not None else Path(get_settings().model_path)
    return base / "registry.json"


def load_registry(model_dir: str | Path | None = None) -> dict:
    path = _registry_path(model_dir)
    if not path.exists():
        return {"production_version": "v1", "versions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(registry: dict, model_dir: str | Path | None = None) -> None:
    path = _registry_path(model_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")


def register_model(
    version: str,
    file: str,
    metrics: dict,
    algorithm: str = "random_forest",
    promote: bool = True,
    model_dir: str | Path | None = None,
) -> dict:
    """Register a model version in the registry that lives next to the model file."""
    registry = load_registry(model_dir)
    entry = {
        "version": version,
        "file": file,
        "algorithm": algorithm,
        "status": "production" if promote else "candidate",
        "metrics": metrics,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    registry["versions"] = [v for v in registry.get("versions", []) if v["version"] != version]
    registry["versions"].append(entry)
    if promote:
        registry["production_version"] = version
        for v in registry["versions"]:
            if v["version"] != version and v.get("status") == "production":
                v["status"] = "archived"
    save_registry(registry, model_dir)
    return registry
