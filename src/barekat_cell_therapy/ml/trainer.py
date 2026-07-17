"""آموزش مدل پیش‌بینی پاسخ درمان."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from barekat_cell_therapy.core.config import get_settings
from barekat_cell_therapy.data.synthetic import CAR_EFFICIENCY, TUMOR_ANTIGENS


FEATURE_COLUMNS = [
    *[f"{ag}_Expression" for ag in TUMOR_ANTIGENS],
    "car_efficacy",
    "HLA_A0201",
    "HLA_DRB10101",
]


def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    X = pd.DataFrame()
    for ag in TUMOR_ANTIGENS:
        col = f"{ag}_Expression"
        X[col] = df[col] if col in df.columns else 0.0

    X["car_efficacy"] = df["CAR_Type"].map(CAR_EFFICIENCY).fillna(0.7)
    X["HLA_A0201"] = df["HLA_A_0201"] if "HLA_A_0201" in df.columns else 0
    X["HLA_DRB10101"] = df["HLA_DRB1_0101"] if "HLA_DRB1_0101" in df.columns else 0
    y = df["Treatment_Response"]
    return X, y


def train_response_model(df: pd.DataFrame, output_dir: str | None = None) -> dict:
    settings = get_settings()
    out = Path(output_dir or settings.model_path)
    out.mkdir(parents=True, exist_ok=True)

    X, y = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, preds)), 4),
        "f1_score": round(float(f1_score(y_test, preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "feature_columns": FEATURE_COLUMNS,
    }

    metrics["model_version"] = "v1"
    model_path = out / settings.response_model
    joblib.dump({"model": model, "features": FEATURE_COLUMNS, "metrics": metrics}, model_path)
    metrics["model_path"] = str(model_path)

    from barekat_cell_therapy.ml.registry import register_model

    register_model(
        version="v1",
        file=settings.response_model,
        metrics={k: v for k, v in metrics.items() if k != "feature_columns"},
        promote=True,
    )
    # Invalidate cached predictor after retrain
    from barekat_cell_therapy.ml.predictor import load_response_model

    load_response_model.cache_clear()
    return metrics
