"""تولید داده‌های سنتتیک برای درمان‌های سلولی (CAR-T)."""

from __future__ import annotations

import numpy as np
import pandas as pd

HLA_ALLELES = [
    "HLA-A*01:01",
    "HLA-A*02:01",
    "HLA-B*07:02",
    "HLA-B*08:01",
    "HLA-C*03:03",
    "HLA-C*04:01",
    "HLA-DRB1*01:01",
    "HLA-DRB1*03:01",
    "HLA-DQB1*02:01",
    "HLA-DQB1*03:02",
]

TUMOR_ANTIGENS = ["HER2", "EGFR", "PD-L1", "CD19", "CD20", "BCMA", "MUC1", "CEA"]
CAR_EFFICIENCY = {"CARv1": 0.6, "CARv2": 0.75, "CARv3": 0.85}
TIME_POINTS = [7, 14, 30, 60, 90]


def generate_cell_therapy_data(
    n_patients: int = 200,
    seed: int = 42,
) -> pd.DataFrame:
    """تولید پروفایل بیماران سنتتیک با HLA، آنتی‌ژن، پاسخ و عوارض."""
    rng = np.random.default_rng(seed)

    hla_data: dict[str, np.ndarray] = {}
    for allele in HLA_ALLELES:
        hla_data[allele] = rng.choice([0, 1, 2], n_patients, p=[0.4, 0.4, 0.2])

    antigen_expression: dict[str, np.ndarray] = {}
    for antigen in TUMOR_ANTIGENS:
        expression = rng.gamma(2, 1.5, n_patients) * 10
        antigen_expression[f"{antigen}_Expression"] = np.round(np.clip(expression, 0, 100), 2)

    best_antigens: list[str] = []
    for i in range(n_patients):
        expr_values = {ag: antigen_expression[f"{ag}_Expression"][i] for ag in TUMOR_ANTIGENS}
        best_antigens.append(max(expr_values, key=expr_values.get))

    car_type = rng.choice(["CARv1", "CARv2", "CARv3"], n_patients, p=[0.2, 0.3, 0.5])
    car_efficacy = np.array([CAR_EFFICIENCY[c] for c in car_type])

    response_prob = np.zeros(n_patients)
    for i in range(n_patients):
        base_prob = car_efficacy[i] * (
            antigen_expression[f"{best_antigens[i]}_Expression"][i] / 100
        )
        base_prob = float(np.clip(base_prob, 0.1, 0.95))
        hla_boost = 0.0
        if hla_data["HLA-A*02:01"][i] > 0:
            hla_boost += 0.05 * hla_data["HLA-A*02:01"][i]
        if hla_data["HLA-DRB1*01:01"][i] > 0:
            hla_boost += 0.03 * hla_data["HLA-DRB1*01:01"][i]
        response_prob[i] = float(np.clip(base_prob + hla_boost, 0.05, 0.98))

    treatment_response = rng.binomial(1, response_prob)

    crs_grade = np.zeros(n_patients, dtype=int)
    neuro_toxicity = np.zeros(n_patients, dtype=int)
    for i in range(n_patients):
        if treatment_response[i] == 1 and response_prob[i] > 0.7:
            crs_grade[i] = int(rng.choice([0, 1, 2, 3, 4], p=[0.3, 0.3, 0.2, 0.15, 0.05]))
        else:
            crs_grade[i] = int(rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1]))
        if crs_grade[i] >= 3:
            neuro_toxicity[i] = int(rng.binomial(1, 0.3))
        else:
            neuro_toxicity[i] = int(rng.binomial(1, 0.05))

    longitudinal: dict[str, np.ndarray] = {}
    for day in TIME_POINTS:
        response_over_time = treatment_response.copy()
        for j in range(n_patients):
            if treatment_response[j] == 1:
                relapse_prob = 0.02 * (day / 30) * (1 - response_prob[j])
                if rng.random() < relapse_prob:
                    response_over_time[j] = 0
        longitudinal[f"Response_Day_{day}"] = response_over_time

    df = pd.DataFrame(
        {
            "Patient_ID": [f"CT_{str(i).zfill(4)}" for i in range(n_patients)],
            "CAR_Type": car_type,
            "Best_Target_Antigen": best_antigens,
            "Treatment_Response": treatment_response,
            "Response_Probability": np.round(response_prob, 3),
            "CRS_Grade": crs_grade,
            "Neurological_Toxicity": neuro_toxicity,
        }
    )

    for allele, values in hla_data.items():
        # HLA-A*02:01 -> HLA_A_0201
        short = allele.replace("HLA-", "").replace("*", "_").replace(":", "")
        df[f"HLA_{short}"] = values

    for antigen, values in antigen_expression.items():
        df[antigen] = values

    for day, responses in longitudinal.items():
        df[day] = responses

    return df
