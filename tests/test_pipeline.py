"""Tests for pipeline modules."""

from barekat_cell_therapy.pipeline.car_design import design_car
from barekat_cell_therapy.pipeline.protocol import generate_protocol
from barekat_cell_therapy.pipeline.simulation import simulate_therapy
from barekat_cell_therapy.pipeline.target_selection import select_best_target


def test_select_best_target():
    antigens = {"CD19": 80.0, "HER2": 20.0, "BCMA": 45.0}
    assert select_best_target(antigens) == "CD19"


def test_design_car():
    design = design_car("CT_0001", "CD19", car_version="CARv3")
    assert design["target_antigen"] == "CD19"
    assert design["car_version"] == "CARv3"
    assert "design_id" in design
    assert "structure" in design


def test_simulate_therapy():
    result = simulate_therapy(
        patient_id="CT_0001",
        design_id="CAR_TEST",
        target_antigen="CD19",
        car_version="CARv3",
        antigen_expression={"CD19": 75.0, "HER2": 10.0},
        hla_profile={"HLA-A*02:01": 1},
        seed=42,
    )
    assert result["status"] == "completed"
    assert 0 <= result["response_probability"] <= 1
    assert "explanation" in result
    assert len(result["longitudinal"]) > 0


def test_generate_protocol():
    protocol = generate_protocol("CT_0001", "CAR_TEST", "CD19", "CARv3")
    assert protocol["vector_type"] == "lentiviral"
    assert len(protocol["steps"]) >= 5
