"""Model explainability for physicians."""

from __future__ import annotations

import numpy as np

from barekat_cell_therapy.schemas import FeatureContribution, ModelExplanation


def explain_prediction(
    model,
    feature_columns: list[str],
    features: dict[str, float],
    model_version: str = "v1",
    top_k: int = 5,
) -> ModelExplanation:
    """Extract feature contributions for a single prediction."""
    import pandas as pd

    X = pd.DataFrame([[features.get(c, 0.0) for c in feature_columns]], columns=feature_columns)
    pred_proba = model.predict_proba(X)[0]
    pred_class = int(model.predict(X)[0])

    contributions = _occlusion_contributions(model, feature_columns, features)
    contributions.sort(key=lambda c: abs(c.contribution), reverse=True)

    return ModelExplanation(
        model_version=model_version,
        predicted_outcome="responder" if pred_class == 1 else "non_responder",
        confidence=float(pred_proba[pred_class]),
        top_features=contributions[:top_k],
        method="occlusion",
    )


def _get_feature_importances(model, feature_columns: list[str]) -> dict[str, float]:
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
        total = float(values.sum()) or 1.0
        return {col: float(val / total) for col, val in zip(feature_columns, values)}
    if hasattr(model, "coef_"):
        coef = np.abs(model.coef_).flatten()
        total = float(coef.sum()) or 1.0
        return {col: float(val / total) for col, val in zip(feature_columns, coef)}
    return {}


def _compute_contributions(
    features: dict[str, float],
    importances: dict[str, float],
    feature_columns: list[str],
    pred_class: int,
) -> list[FeatureContribution]:
    contributions: list[FeatureContribution] = []
    if not importances:
        for col in feature_columns:
            val = features.get(col, 0.0)
            contributions.append(
                FeatureContribution(
                    feature=col,
                    value=val,
                    contribution=round(val * 0.01, 4),
                    direction="positive" if val > 0.5 else "negative",
                )
            )
        return contributions

    median_val = float(np.median([features.get(c, 0.0) for c in feature_columns]))
    for col in feature_columns:
        val = features.get(col, 0.0)
        imp = importances.get(col, 0.0)
        signed = imp * (1 if val >= median_val else -1)
        if pred_class == 0:
            signed = -signed
        contributions.append(
            FeatureContribution(
                feature=col,
                value=round(val, 4),
                contribution=round(signed, 4),
                direction="positive" if signed > 0 else "negative",
            )
        )
    return contributions


def _occlusion_contributions(
    model, feature_columns: list[str], features: dict[str, float]
) -> list[FeatureContribution]:
    """Local attribution: change in P(responder) when a feature is set to its neutral value (0).

    Positive contribution = the feature's actual value raises the response probability.
    """
    import pandas as pd

    base = {c: float(features.get(c, 0.0)) for c in feature_columns}
    rows = [base]
    for col in feature_columns:
        occluded = dict(base)
        occluded[col] = 0.0
        rows.append(occluded)
    X = pd.DataFrame([[r[c] for c in feature_columns] for r in rows], columns=feature_columns)
    proba = model.predict_proba(X)[:, 1]
    out: list[FeatureContribution] = []
    for col, p_occ in zip(feature_columns, proba[1:]):
        delta = float(proba[0] - p_occ)
        out.append(
            FeatureContribution(
                feature=col,
                value=round(base[col], 4),
                contribution=round(delta, 4),
                direction="positive" if delta >= 0 else "negative",
            )
        )
    return out
