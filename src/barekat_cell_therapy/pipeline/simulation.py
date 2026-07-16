"""شبیه‌سازی پاسخ درمانی و عوارض جانبی."""

from __future__ import annotations

import uuid

import numpy as np

from barekat_cell_therapy.core.config import get_settings
from barekat_cell_therapy.data.synthetic import CAR_EFFICIENCY, TIME_POINTS


def _hla_boost(hla_profile: dict[str, int]) -> float:
    boost = 0.0
    if hla_profile.get("HLA-A*02:01", 0) > 0:
        boost += 0.05 * hla_profile["HLA-A*02:01"]
    if hla_profile.get("HLA-DRB1*01:01", 0) > 0:
        boost += 0.03 * hla_profile["HLA-DRB1*01:01"]
    return boost


def simulate_therapy(
    patient_id: str,
    design_id: str,
    target_antigen: str,
    car_version: str,
    antigen_expression: dict[str, float],
    hla_profile: dict[str, int],
    dose_cells: float = 1e8,
    horizon_days: int | None = None,
    seed: int | None = None,
) -> dict:
    """پیش‌بینی پاسخ، CRS و داده‌های طولی."""
    settings = get_settings()
    rng = np.random.default_rng(seed)
    horizon = horizon_days or settings.simulation_horizon_days

    expr = antigen_expression.get(target_antigen, 0.0)
    base = CAR_EFFICIENCY.get(car_version, 0.7) * (expr / 100.0)
    dose_factor = float(np.clip(np.log10(dose_cells) / 8.0, 0.7, 1.2))
    response_prob = float(np.clip(base * dose_factor + _hla_boost(hla_profile), 0.05, 0.98))

    predicted_response = bool(rng.random() < response_prob)

    if predicted_response and response_prob > settings.crs_risk_threshold:
        crs_grade = int(rng.choice([0, 1, 2, 3, 4], p=[0.3, 0.3, 0.2, 0.15, 0.05]))
    else:
        crs_grade = int(rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1]))

    neuro_risk = 0.3 if crs_grade >= 3 else 0.05
    neurotoxicity_risk = float(neuro_risk)

    days = [d for d in TIME_POINTS if d <= horizon]
    longitudinal = []
    still_responding = predicted_response
    for day in days:
        if still_responding:
            relapse_prob = 0.02 * (day / 30) * (1 - response_prob)
            if rng.random() < relapse_prob:
                still_responding = False
        tumor = 100.0 * (1 - response_prob) if not still_responding else max(5.0, 100 * (1 - response_prob * day / horizon))
        longitudinal.append(
            {
                "day": day,
                "response": still_responding,
                "tumor_burden_pct": round(float(tumor), 2),
            }
        )

    efficacy = response_prob * (1 - crs_grade / 10)
    safety = 1.0 - (crs_grade / 4.0) * 0.5 - neurotoxicity_risk * 0.3

    contributions = [
        {
            "feature": f"{target_antigen}_expression",
            "value": expr,
            "contribution": round(expr / 100 * 0.4, 3),
            "direction": "positive" if expr > 30 else "negative",
        },
        {
            "feature": "car_version_efficacy",
            "value": CAR_EFFICIENCY.get(car_version, 0.7),
            "contribution": round(CAR_EFFICIENCY.get(car_version, 0.7) * 0.35, 3),
            "direction": "positive",
        },
        {
            "feature": "hla_boost",
            "value": _hla_boost(hla_profile),
            "contribution": round(_hla_boost(hla_profile), 3),
            "direction": "positive" if _hla_boost(hla_profile) > 0 else "negative",
        },
        {
            "feature": "dose_factor",
            "value": dose_factor,
            "contribution": round((dose_factor - 1) * 0.2, 3),
            "direction": "positive" if dose_factor >= 1 else "negative",
        },
    ]

    return {
        "simulation_id": f"SIM_{uuid.uuid4().hex[:12].upper()}",
        "patient_id": patient_id,
        "design_id": design_id,
        "status": "completed",
        "response_probability": round(response_prob, 3),
        "predicted_response": predicted_response,
        "crs_grade": crs_grade,
        "neurotoxicity_risk": round(neurotoxicity_risk, 3),
        "efficacy_score": round(float(efficacy), 3),
        "safety_score": round(float(np.clip(safety, 0, 1)), 3),
        "longitudinal": longitudinal,
        "explanation": {
            "model_version": "v1",
            "predicted_outcome": "responder" if predicted_response else "non_responder",
            "confidence": round(response_prob if predicted_response else 1 - response_prob, 3),
            "top_features": contributions,
            "method": "feature_importance",
        },
    }
