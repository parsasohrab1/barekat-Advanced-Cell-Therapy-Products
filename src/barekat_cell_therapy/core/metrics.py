"""متریک‌های Prometheus."""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

SIMULATION_COUNTER = Counter(
    "barekat_cell_therapy_simulations_total",
    "Total therapy simulations",
    ["outcome"],
)
PATIENT_COUNTER = Counter(
    "barekat_cell_therapy_patients_total",
    "Total registered patients",
)


def metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
