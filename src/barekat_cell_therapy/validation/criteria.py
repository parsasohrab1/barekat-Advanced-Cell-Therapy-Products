"""Pre-specified TRL-5 acceptance criteria (revision 2, see docs/TRL.md section 4).

Thresholds are fixed here, in version control, BEFORE results are produced; the runner only
compares measured values against them. Changing a threshold is a reviewable code change.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Criterion:
    id: str
    description: str
    op: str  # ">=" or "<="
    threshold: float

    def check(self, value: float) -> bool:
        return value >= self.threshold if self.op == ">=" else value <= self.threshold


MODEL_CRITERIA = [
    Criterion("M1", "ROC-AUC on independent cohort (absolute floor)", ">=", 0.60),
    Criterion("M2", "AUC / oracle AUC (ceiling set by outcome noise)", ">=", 0.90),
    Criterion("M3", "Expected calibration error", "<=", 0.10),
    Criterion("M4", "Brier score minus prevalence baseline", "<=", 0.0),
    Criterion("M5", "Balanced accuracy at 0.5 cut-off", ">=", 0.55),
    Criterion("M6", "Worst CAR-type subgroup AUC", ">=", 0.58),
]
ROBUSTNESS_CRITERIA = [
    Criterion("R1", "AUC drop under 10% multiplicative input noise", "<=", 0.05),
    Criterion("R2", "AUC drop with 20% antigen values missing", "<=", 0.08),
    Criterion("R3", "Invalid (non-finite / out-of-range) predictions", "<=", 0.0),
    Criterion("R4", "Prediction mismatches between two seeded trainings", "<=", 0.0),
]
SYSTEM_CRITERIA = [
    Criterion("S1", "End-to-end plan success rate", ">=", 1.0),
    Criterion("S2", "p95 latency of /therapy/plan (seconds)", "<=", 2.0),
    Criterion("S3", "Audit events per plan (design+simulation+protocol)", ">=", 3.0),
    Criterion("S4", "RBAC matrix checks passed (fraction)", ">=", 1.0),
    Criterion("S5", "Plans served by trained model (fraction)", ">=", 1.0),
    Criterion("S6", "Concurrent-request success rate", ">=", 1.0),
]
