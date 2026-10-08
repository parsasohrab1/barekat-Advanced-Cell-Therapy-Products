"""Model validation on independent cohorts in a simulated operational environment."""

from __future__ import annotations

import tempfile

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

from barekat_cell_therapy.data.synthetic import generate_cell_therapy_data
from barekat_cell_therapy.ml.evaluation import _wilson_ci
from barekat_cell_therapy.ml.trainer import (
    add_derived_features,
    prepare_features,
    train_response_model,
)

DEV = {"n_patients": 1000, "seed": 42}
# Independent "relevant environment" cohorts: new seeds; second one has covariate shift
# (lower antigen density, different CAR mix) to mimic a different treatment centre.
COHORTS = {
    "same_distribution": {"n_patients": 1000, "seed": 2024},
    "shifted_site": {
        "n_patients": 1000,
        "seed": 7,
        "antigen_scale": 1.2,
        "car_probs": (0.4, 0.4, 0.2),
    },
}


def _ece(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    ece = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            ece += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(ece)


def _predict(model, X: pd.DataFrame) -> np.ndarray:
    return model.predict_proba(X)[:, 1]


def _metrics(model, df: pd.DataFrame) -> dict:
    X, y = prepare_features(df)
    yv = y.to_numpy()
    p = _predict(model, X)
    pred = (p >= 0.5).astype(int)
    tp = int(((pred == 1) & (yv == 1)).sum())
    tn = int(((pred == 0) & (yv == 0)).sum())
    pos, neg = int((yv == 1).sum()), int((yv == 0).sum())
    sens, spec = tp / pos, tn / neg
    auc = float(roc_auc_score(yv, p))
    oracle = float(roc_auc_score(yv, df["Response_Probability"]))
    prev = float(yv.mean())
    sub = {}
    for car, g in df.groupby("CAR_Type"):
        gy = g["Treatment_Response"].to_numpy()
        if len(set(gy)) == 2:
            sub[car] = round(float(roc_auc_score(gy, _predict(model, prepare_features(g)[0]))), 4)
    return {
        "n": int(len(yv)),
        "prevalence": round(prev, 4),
        "auc": round(auc, 4),
        "oracle_auc": round(oracle, 4),
        "auc_over_oracle": round(auc / oracle, 4),
        "ece": round(_ece(yv, p), 4),
        "brier": round(float(brier_score_loss(yv, p)), 4),
        "brier_minus_baseline": round(float(brier_score_loss(yv, p)) - prev * (1 - prev), 4),
        "sensitivity": {"value": round(sens, 4), "ci": _wilson_ci(tp, pos)},
        "specificity": {"value": round(spec, 4), "ci": _wilson_ci(tn, neg)},
        "balanced_accuracy": round((sens + spec) / 2, 4),
        "subgroup_auc": sub,
        "worst_subgroup_auc": min(sub.values()) if sub else 0.0,
    }


def _robustness(model, df: pd.DataFrame) -> dict:
    X, y = prepare_features(df)
    base = roc_auc_score(y, _predict(model, X))
    rng = np.random.default_rng(0)
    ag = [c for c in X.columns if c.endswith("_Expression")]

    Xn = X.copy()
    Xn[ag] = np.clip(Xn[ag] * rng.normal(1.0, 0.10, Xn[ag].shape), 0, 100)
    Xn = add_derived_features(Xn)
    noise_auc = roc_auc_score(y, _predict(model, Xn))

    Xm = X.copy()
    mask = rng.random(Xm[ag].shape) < 0.20
    Xm[ag] = Xm[ag].mask(mask, 0.0)
    Xm = add_derived_features(Xm)
    miss_auc = roc_auc_score(y, _predict(model, Xm))

    allp = np.concatenate([_predict(model, X), _predict(model, Xn), _predict(model, Xm)])
    invalid = int((~np.isfinite(allp) | (allp < 0) | (allp > 1)).sum())
    return {
        "baseline_auc": round(float(base), 4),
        "noise_auc_drop": round(float(base - noise_auc), 4),
        "missing_auc_drop": round(float(base - miss_auc), 4),
        "invalid_predictions": invalid,
    }


def _reproducibility(dev: pd.DataFrame, probe: pd.DataFrame) -> dict:
    preds = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as d:
            train_response_model(dev, output_dir=d)
            bundle = joblib.load(f"{d}/response_predictor_v1.pkl")
            preds.append(_predict(bundle["model"], prepare_features(probe)[0]))
    return {"prediction_mismatches": int((~np.isclose(preds[0], preds[1])).sum())}


def run_model_validation(model_dir: str) -> dict:
    dev = generate_cell_therapy_data(**DEV)
    train_metrics = train_response_model(dev, output_dir=model_dir)
    model = joblib.load(f"{model_dir}/response_predictor_v1.pkl")["model"]
    cohorts = {}
    frames = {}
    for name, kw in COHORTS.items():
        frames[name] = generate_cell_therapy_data(**kw)
        cohorts[name] = _metrics(model, frames[name])
    rob = _robustness(model, frames["shifted_site"])
    rob.update(_reproducibility(dev, frames["same_distribution"].head(200)))
    return {
        "development_cohort": DEV,
        "internal_holdout": {k: train_metrics[k] for k in ("accuracy", "f1_score", "roc_auc")},
        "cohorts": cohorts,
        "robustness": rob,
    }
