"""Tests for ML explainability and predictor wiring."""

from barekat_cell_therapy.data.synthetic import generate_cell_therapy_data
from barekat_cell_therapy.ml.evaluation import evaluate_response_model
from barekat_cell_therapy.ml.trainer import train_response_model
from barekat_cell_therapy.pipeline.simulation import simulate_therapy


def test_train_and_explain(tmp_path):
    df = generate_cell_therapy_data(n_patients=80, seed=7)
    metrics = train_response_model(df, output_dir=str(tmp_path))
    assert metrics["accuracy"] >= 0.0
    assert (tmp_path / "response_predictor_v1.pkl").exists()


def test_evaluate_model():
    df = generate_cell_therapy_data(n_patients=60, seed=3)
    result = evaluate_response_model(df, n_splits=3)
    assert "roc_auc" in result
    assert "sensitivity" in result
    assert result["n_samples"] == 60


def test_simulate_returns_narrative():
    result = simulate_therapy(
        patient_id="CT_X",
        design_id="CAR_X",
        target_antigen="CD19",
        car_version="CARv3",
        antigen_expression={"CD19": 80.0, "HER2": 10.0},
        hla_profile={"HLA-A*02:01": 1},
        seed=1,
    )
    assert result["clinical_narrative"]
    assert result["inference_source"] in {"ml_model", "heuristic"}
    assert "explanation" in result
