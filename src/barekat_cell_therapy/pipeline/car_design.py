"""طراحی ساختار CAR برای بیمار."""

from __future__ import annotations

import uuid

from barekat_cell_therapy.core.config import get_settings
from barekat_cell_therapy.data.synthetic import CAR_EFFICIENCY

DOMAIN_AFFINITY = {
    "CARv1": 0.65,
    "CARv2": 0.78,
    "CARv3": 0.90,
}


def design_car(
    patient_id: str,
    target_antigen: str,
    car_version: str | None = None,
    costimulatory_domains: list[str] | None = None,
) -> dict:
    """ساخت طرح پیشنهادی CAR."""
    settings = get_settings()
    version = car_version or settings.default_car_version
    domains = costimulatory_domains or ["CD28", "4-1BB"]
    design_id = f"CAR_{uuid.uuid4().hex[:12].upper()}"

    return {
        "design_id": design_id,
        "patient_id": patient_id,
        "target_antigen": target_antigen,
        "car_version": version,
        "scfv_affinity": DOMAIN_AFFINITY.get(version, 0.75),
        "costimulatory_domains": domains,
        "hinge": "CD8α",
        "transmembrane": "CD8α",
        "signaling_domain": "CD3ζ",
        "expected_efficacy": CAR_EFFICIENCY.get(version, 0.7),
        "structure": {
            "extracellular": f"anti-{target_antigen} scFv",
            "hinge": "CD8α",
            "transmembrane": "CD8α",
            "costimulatory": "+".join(domains),
            "signaling": "CD3ζ",
        },
    }
