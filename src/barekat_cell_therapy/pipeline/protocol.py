"""Generate manufacturing instructions for engineered cells."""

from __future__ import annotations

import uuid


def generate_protocol(
    patient_id: str,
    design_id: str,
    target_antigen: str,
    car_version: str,
    vector_type: str = "lentiviral",
    target_cell_dose: float = 1e8,
) -> dict:
    """Build the manufacturing protocol for CAR-T cells."""
    transduction = {"lentiviral": 0.55, "retroviral": 0.45, "transposon": 0.35}.get(
        vector_type, 0.5
    )
    protocol_id = f"PROT_{uuid.uuid4().hex[:12].upper()}"

    steps = [
        {
            "step": 1,
            "name": "Leukapheresis",
            "description": "Collect T cells from the patient",
            "duration_hours": 4,
        },
        {
            "step": 2,
            "name": "T-cell enrichment",
            "description": "CD3+/CD28+ enrichment and activation",
            "duration_hours": 24,
        },
        {
            "step": 3,
            "name": "Viral transduction",
            "description": (
                f"Transduction with {vector_type} vector "
                f"carrying anti-{target_antigen} {car_version}"
            ),
            "duration_hours": 48,
            "expected_efficiency": transduction,
        },
        {
            "step": 4,
            "name": "Expansion",
            "description": f"Expansion to target dose of {target_cell_dose:.0e} cells",
            "duration_hours": 168,
        },
        {
            "step": 5,
            "name": "QC release",
            "description": "Quality control: purity, viability, CAR expression, sterility",
            "duration_hours": 48,
        },
        {
            "step": 6,
            "name": "Formulation & cryopreservation",
            "description": "Final formulation and cryopreservation for infusion",
            "duration_hours": 6,
        },
    ]

    return {
        "protocol_id": protocol_id,
        "patient_id": patient_id,
        "design_id": design_id,
        "vector_type": vector_type,
        "transduction_efficiency": transduction,
        "target_cell_dose": target_cell_dose,
        "target_antigen": target_antigen,
        "car_version": car_version,
        "steps": steps,
        "total_duration_days": round(sum(s["duration_hours"] for s in steps) / 24, 1),
    }
