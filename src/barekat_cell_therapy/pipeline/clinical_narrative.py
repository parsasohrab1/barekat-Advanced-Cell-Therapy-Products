"""Clinical narrative understandable to physicians."""

from __future__ import annotations


def build_clinical_narrative(
    target_antigen: str,
    car_version: str,
    response_probability: float,
    predicted_response: bool,
    crs_grade: int,
    neurotoxicity_risk: float,
    explanation: dict,
) -> str:
    outcome = "likely responder" if predicted_response else "unlikely responder"
    top = explanation.get("top_features") or []
    drivers = ", ".join(
        f"{f.get('feature')} ({f.get('direction')})" for f in top[:3]
    ) or "insufficient data"

    crs_note = {
        0: "negligible CRS risk",
        1: "Mild CRS likely; outpatient monitoring is sufficient",
        2: "Moderate CRS; Tocilizumab readiness is recommended",
        3: "Severe CRS likely; consider ICU admission",
        4: "Life-threatening CRS; activate the emergency protocol",
    }.get(crs_grade, "CRS grade unknown")

    neuro = (
        "Neurotoxicity risk is high; daily neurological assessment is required."
        if neurotoxicity_risk >= 0.25
        else "Neurotoxicity risk is within the acceptable range."
    )

    return (
        f"For target {target_antigen} with {car_version}, "
        f"the patient is predicted as a \"{outcome}\" "
        f"with a response probability of {response_probability:.0%}. "
        f"Main model drivers: {drivers}. "
        f"{crs_note}. {neuro}"
    )
