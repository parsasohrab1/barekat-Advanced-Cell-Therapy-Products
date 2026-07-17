"""رجیستری نسخه‌های مدل پاسخ درمانی."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from barekat_cell_therapy.core.config import get_settings


def _registry_path() -> Path:
    settings = get_settings()
    return Path(settings.model_path) / "registry.json"


def load_registry() -> dict:
    path = _registry_path()
    if not path.exists():
        return {"production_version": "v1", "versions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(registry: dict) -> None:
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")


def register_model(
    version: str,
    file: str,
    metrics: dict,
    algorithm: str = "random_forest",
    promote: bool = True,
) -> dict:
    registry = load_registry()
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
    save_registry(registry)
    return registry
