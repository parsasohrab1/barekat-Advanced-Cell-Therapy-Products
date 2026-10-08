"""Tests for the TRL-5 validation harness itself."""

import numpy as np

from barekat_cell_therapy.validation.criteria import MODEL_CRITERIA, SYSTEM_CRITERIA
from barekat_cell_therapy.validation.model_validation import _ece
from barekat_cell_therapy.validation.runner import evaluate


def test_ece_perfect_and_worst():
    y = np.array([0, 1] * 50)
    assert _ece(y, y.astype(float)) == 0.0
    assert _ece(y, 1.0 - y) > 0.9


def test_criteria_ids_unique_and_directional():
    ids = [c.id for c in MODEL_CRITERIA + SYSTEM_CRITERIA]
    assert len(ids) == len(set(ids))
    assert MODEL_CRITERIA[0].check(0.7) and not MODEL_CRITERIA[0].check(0.5)


def test_evaluate_flags_a_failing_system():
    cohort = {
        "auc": 0.7, "auc_over_oracle": 0.95, "ece": 0.05, "brier_minus_baseline": -0.01,
        "balanced_accuracy": 0.65, "worst_subgroup_auc": 0.65,
    }
    model = {
        "cohorts": {"c": cohort},
        "robustness": {"noise_auc_drop": 0.0, "missing_auc_drop": 0.0,
                       "invalid_predictions": 0, "prediction_mismatches": 0},
    }
    system = {
        "success_rate": 1.0, "latency_p95_s": 0.2, "audit_events_per_plan": 3.0,
        "rbac_pass_fraction": 1.0, "ml_model_fraction": 1.0, "concurrent_success_rate": 1.0,
    }
    assert evaluate(model, system)["all_passed"]
    system["rbac_pass_fraction"] = 0.9
    assert not evaluate(model, system)["all_passed"]
