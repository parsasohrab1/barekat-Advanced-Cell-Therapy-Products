"""ML evaluation and registry endpoints."""

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from barekat_cell_therapy.core.rbac import require_role
from barekat_cell_therapy.ml.evaluation import evaluate_response_model
from barekat_cell_therapy.ml.registry import load_registry
from barekat_cell_therapy.models.user import User
from barekat_cell_therapy.schemas import EvaluationResponse, ModelRegistryResponse

router = APIRouter()


@router.get("/ml/registry", response_model=ModelRegistryResponse)
def get_registry(_: User | None = Depends(require_role("viewer"))) -> ModelRegistryResponse:
    reg = load_registry()
    return ModelRegistryResponse(
        production_version=reg.get("production_version", "v1"),
        versions=reg.get("versions", []),
    )


@router.post("/ml/evaluate", response_model=EvaluationResponse)
def evaluate(
    csv_path: str | None = None,
    _: User | None = Depends(require_role("scientist")),
) -> EvaluationResponse:
    path = Path(csv_path or "data/raw/synthetic_patients.csv")
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found: {path}")
    df = pd.read_csv(path)
    result = evaluate_response_model(df)
    return EvaluationResponse(**result)
