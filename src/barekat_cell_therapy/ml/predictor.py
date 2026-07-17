"""بارگذاری و inference مدل پیش‌بینی پاسخ."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from barekat_cell_therapy.core.config import get_settings
from barekat_cell_therapy.data.synthetic import CAR_EFFICIENCY, TUMOR_ANTIGENS
from barekat_cell_therapy.ml.trainer import FEATURE_COLUMNS


def features_from_patient(
    antigen_expression: dict[str, float],
    hla_profile: dict[str, int],
    car_version: str,
) -> dict[str, float]:
    """ساخت دیکشنری ویژگی هم‌تراز با آموزش مدل."""
    features: dict[str, float] = {}
    for ag in TUMOR_ANTIGENS:
        features[f"{ag}_Expression"] = float(antigen_expression.get(ag, 0.0))
    features["car_efficacy"] = float(CAR_EFFICIENCY.get(car_version, 0.7))
    features["HLA_A0201"] = float(hla_profile.get("HLA-A*02:01", 0))
    features["HLA_DRB10101"] = float(hla_profile.get("HLA-DRB1*01:01", 0))
    return features


@lru_cache
def load_response_model(model_file: str | None = None) -> dict | None:
    settings = get_settings()
    path = Path(settings.model_path) / (model_file or settings.response_model)
    if not path.exists():
        return None
    return joblib.load(path)


def predict_response(
    antigen_expression: dict[str, float],
    hla_profile: dict[str, int],
    car_version: str,
) -> dict | None:
    """پیش‌بینی پاسخ؛ None اگر مدل موجود نباشد (fallback به heuristic)."""
    bundle = load_response_model()
    if bundle is None:
        return None

    model = bundle["model"]
    feature_columns: list[str] = bundle.get("features", FEATURE_COLUMNS)
    features = features_from_patient(antigen_expression, hla_profile, car_version)
    X = pd.DataFrame([[features.get(c, 0.0) for c in feature_columns]], columns=feature_columns)
    proba = float(model.predict_proba(X)[0][1])
    pred = int(model.predict(X)[0])
    return {
        "response_probability": proba,
        "predicted_response": bool(pred == 1),
        "features": features,
        "feature_columns": feature_columns,
        "model": model,
        "model_version": bundle.get("metrics", {}).get("model_version", "v1"),
        "metrics": bundle.get("metrics", {}),
    }
