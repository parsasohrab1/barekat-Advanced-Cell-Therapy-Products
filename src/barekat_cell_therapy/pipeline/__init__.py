"""Pipeline: target selection, CAR design, simulation, protocol."""

from barekat_cell_therapy.pipeline.car_design import design_car
from barekat_cell_therapy.pipeline.clinical_narrative import build_clinical_narrative
from barekat_cell_therapy.pipeline.protocol import generate_protocol
from barekat_cell_therapy.pipeline.simulation import simulate_therapy
from barekat_cell_therapy.pipeline.target_selection import select_best_target

__all__ = [
    "select_best_target",
    "design_car",
    "simulate_therapy",
    "generate_protocol",
    "build_clinical_narrative",
]
