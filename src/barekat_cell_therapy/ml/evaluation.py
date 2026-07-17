"""ارزیابی مدل پیش‌بینی پاسخ CAR-T."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from barekat_cell_therapy.ml.trainer import FEATURE_COLUMNS, prepare_features


def _wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return round(float(max(0, center - margin)), 4), round(float(min(1, center + margin)), 4)


def evaluate_response_model(df: pd.DataFrame, model=None, n_splits: int = 5) -> dict[str, Any]:
    """ارزیابی با CV و فاصله اطمینان Wilson برای حساسیت/اختصاصیت."""
    X, y = prepare_features(df)
    if model is None:
        model = RandomForestClassifier(
            n_estimators=100, max_depth=8, random_state=42, class_weight="balanced"
        )

    min_class = int(y.value_counts().min())
    splits = min(n_splits, max(2, min_class))
    skf = StratifiedKFold(n_splits=splits, shuffle=True, random_state=42)
    proba = cross_val_predict(model, X, y, cv=skf, method="predict_proba")[:, 1]
    preds = (proba >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(y, preds, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    sens_ci = _wilson_ci(int(tp), int(tp + fn))
    spec_ci = _wilson_ci(int(tn), int(tn + fp))

    folds = []
    for i, (train_idx, test_idx) in enumerate(skf.split(X, y), start=1):
        fold_model = RandomForestClassifier(
            n_estimators=100, max_depth=8, random_state=42, class_weight="balanced"
        )
        fold_model.fit(X.iloc[train_idx], y.iloc[train_idx])
        fold_pred = fold_model.predict(X.iloc[test_idx])
        fold_proba = fold_model.predict_proba(X.iloc[test_idx])[:, 1]
        folds.append(
            {
                "fold": i,
                "accuracy": round(float(accuracy_score(y.iloc[test_idx], fold_pred)), 4),
                "f1_score": round(float(f1_score(y.iloc[test_idx], fold_pred)), 4),
                "roc_auc": round(float(roc_auc_score(y.iloc[test_idx], fold_proba)), 4),
            }
        )

    return {
        "accuracy": round(float(accuracy_score(y, preds)), 4),
        "sensitivity": {
            "value": round(float(sensitivity), 4),
            "ci_lower": sens_ci[0],
            "ci_upper": sens_ci[1],
        },
        "specificity": {
            "value": round(float(specificity), 4),
            "ci_lower": spec_ci[0],
            "ci_upper": spec_ci[1],
        },
        "precision": round(float(precision_score(y, preds, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y, preds, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y, proba)), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "cross_validation": folds,
        "n_samples": int(len(y)),
        "feature_columns": FEATURE_COLUMNS,
    }
