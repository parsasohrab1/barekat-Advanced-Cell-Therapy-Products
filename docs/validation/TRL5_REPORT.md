# TRL-5 Validation Evidence - v0.3.0

Generated: 2026-10-07T21:04:44+00:00  
**Verdict: ALL CRITERIA MET**

> Scope: in-silico validation of an integrated decision-support system in a simulated operational environment, on *synthetic* cohorts. It is evidence for TRL 5 of the software system; it is NOT clinical validation. See docs/TRL.md for the limits.

| Scope | ID | Criterion | Rule | Measured | Result |
|---|---|---|---|---|---|
| same_distribution | M1 | ROC-AUC on independent cohort (absolute floor) | >= 0.6 | 0.6792 | PASS |
| same_distribution | M2 | AUC / oracle AUC (ceiling set by outcome noise) | >= 0.9 | 0.9671 | PASS |
| same_distribution | M3 | Expected calibration error | <= 0.1 | 0.0486 | PASS |
| same_distribution | M4 | Brier score minus prevalence baseline | <= 0.0 | -0.0217 | PASS |
| same_distribution | M5 | Balanced accuracy at 0.5 cut-off | >= 0.55 | 0.6273 | PASS |
| same_distribution | M6 | Worst CAR-type subgroup AUC | >= 0.58 | 0.6669 | PASS |
| shifted_site | M1 | ROC-AUC on independent cohort (absolute floor) | >= 0.6 | 0.6183 | PASS |
| shifted_site | M2 | AUC / oracle AUC (ceiling set by outcome noise) | >= 0.9 | 0.943 | PASS |
| shifted_site | M3 | Expected calibration error | <= 0.1 | 0.0394 | PASS |
| shifted_site | M4 | Brier score minus prevalence baseline | <= 0.0 | -0.0115 | PASS |
| shifted_site | M5 | Balanced accuracy at 0.5 cut-off | >= 0.55 | 0.5809 | PASS |
| shifted_site | M6 | Worst CAR-type subgroup AUC | >= 0.58 | 0.5802 | PASS |
| robustness | R1 | AUC drop under 10% multiplicative input noise | <= 0.05 | -0.0044 | PASS |
| robustness | R2 | AUC drop with 20% antigen values missing | <= 0.08 | 0.0057 | PASS |
| robustness | R3 | Invalid (non-finite / out-of-range) predictions | <= 0.0 | 0.0 | PASS |
| robustness | R4 | Prediction mismatches between two seeded trainings | <= 0.0 | 0.0 | PASS |
| system | S1 | End-to-end plan success rate | >= 1.0 | 1.0 | PASS |
| system | S2 | p95 latency of /therapy/plan (seconds) | <= 2.0 | 0.4735 | PASS |
| system | S3 | Audit events per plan (design+simulation+protocol) | >= 3.0 | 3.0 | PASS |
| system | S4 | RBAC matrix checks passed (fraction) | >= 1.0 | 1.0 | PASS |
| system | S5 | Plans served by trained model (fraction) | >= 1.0 | 1.0 | PASS |
| system | S6 | Concurrent-request success rate | >= 1.0 | 1.0 | PASS |

## Raw measurements

```json
{
  "model": {
    "development_cohort": {
      "n_patients": 1000,
      "seed": 42
    },
    "internal_holdout": {
      "accuracy": 0.64,
      "f1_score": 0.6591,
      "roc_auc": 0.6836
    },
    "cohorts": {
      "same_distribution": {
        "n": 1000,
        "prevalence": 0.54,
        "auc": 0.6792,
        "oracle_auc": 0.7023,
        "auc_over_oracle": 0.9671,
        "ece": 0.0486,
        "brier": 0.2267,
        "brier_minus_baseline": -0.0217,
        "sensitivity": {
          "value": 0.5741,
          "ci": [
            0.532,
            0.6151
          ]
        },
        "specificity": {
          "value": 0.6804,
          "ci": [
            0.6365,
            0.7214
          ]
        },
        "balanced_accuracy": 0.6273,
        "subgroup_auc": {
          "CARv1": 0.6803,
          "CARv2": 0.6789,
          "CARv3": 0.6669
        },
        "worst_subgroup_auc": 0.6669
      },
      "shifted_site": {
        "n": 1000,
        "prevalence": 0.423,
        "auc": 0.6183,
        "oracle_auc": 0.6557,
        "auc_over_oracle": 0.943,
        "ece": 0.0394,
        "brier": 0.2325,
        "brier_minus_baseline": -0.0115,
        "sensitivity": {
          "value": 0.2813,
          "ci": [
            0.2406,
            0.326
          ]
        },
        "specificity": {
          "value": 0.8804,
          "ci": [
            0.8514,
            0.9044
          ]
        },
        "balanced_accuracy": 0.5809,
        "subgroup_auc": {
          "CARv1": 0.6139,
          "CARv2": 0.5802,
          "CARv3": 0.6534
        },
        "worst_subgroup_auc": 0.5802
      }
    },
    "robustness": {
      "baseline_auc": 0.6183,
      "noise_auc_drop": -0.0044,
      "missing_auc_drop": 0.0057,
      "invalid_predictions": 0,
      "prediction_mismatches": 0
    }
  },
  "system": {
    "rbac_checks": {
      "anonymous_blocked": true,
      "self_register_downgraded": true,
      "viewer_cannot_write": true,
      "clinician_can_write": true,
      "viewer_can_read": true,
      "clinician_blocked_from_audit": true,
      "scientist_reads_audit": true,
      "bad_token_rejected": true,
      "duplicate_patient_409": true,
      "unknown_patient_404": true,
      "invalid_payload_422": true
    },
    "rbac_pass_fraction": 1.0,
    "n_plans": 30,
    "success_rate": 1.0,
    "ml_model_fraction": 1.0,
    "latency_p50_s": 0.3089,
    "latency_p95_s": 0.4735,
    "concurrent_success_rate": 1.0,
    "audit_actions": {
      "design.create": 54,
      "patient.create": 31,
      "patient.read": 1,
      "protocol.create": 54,
      "simulation.run": 54,
      "user.login": 4,
      "user.register": 4
    },
    "audit_events_per_plan": 3.0
  }
}
```
