"""اسکیماهای Pydantic برای API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict[str, str] = {}


class AntigenExpression(BaseModel):
    antigen: str
    expression_pct: float = Field(..., ge=0, le=100)


class HlaAllele(BaseModel):
    allele: str
    copies: int = Field(..., ge=0, le=2)


class PatientCreate(BaseModel):
    patient_id: str
    hla_profile: list[HlaAllele] = Field(default_factory=list)
    antigen_expression: list[AntigenExpression] = Field(default_factory=list)


class PatientResponse(BaseModel):
    patient_id: str
    status: str
    best_target_antigen: str | None = None
    hla_profile: list[HlaAllele] = Field(default_factory=list)
    antigen_expression: list[AntigenExpression] = Field(default_factory=list)
    profile_object_key: str | None = None
    created_at: datetime | None = None


class CarDesignRequest(BaseModel):
    patient_id: str
    target_antigen: str | None = None
    car_version: str | None = None
    costimulatory_domains: list[str] = Field(default_factory=lambda: ["CD28", "4-1BB"])


class CarDesignResponse(BaseModel):
    design_id: str
    patient_id: str
    target_antigen: str
    car_version: str
    scfv_affinity: float | None = None
    costimulatory_domains: list[str] = Field(default_factory=list)
    design_summary: dict = Field(default_factory=dict)
    created_at: datetime | None = None


class FeatureContribution(BaseModel):
    feature: str
    value: float
    contribution: float
    direction: Literal["positive", "negative"]


class ModelExplanation(BaseModel):
    model_version: str
    predicted_outcome: str
    confidence: float
    top_features: list[FeatureContribution] = Field(default_factory=list)
    method: str = "feature_importance"


class SimulationRequest(BaseModel):
    patient_id: str
    design_id: str
    dose_cells: float = Field(default=1e8, gt=0)
    horizon_days: int | None = None


class LongitudinalPoint(BaseModel):
    day: int
    response: bool
    tumor_burden_pct: float | None = None


class SimulationResponse(BaseModel):
    simulation_id: str
    patient_id: str
    design_id: str
    status: str
    response_probability: float | None = None
    predicted_response: bool | None = None
    crs_grade: int | None = None
    neurotoxicity_risk: float | None = None
    efficacy_score: float | None = None
    safety_score: float | None = None
    longitudinal: list[LongitudinalPoint] = Field(default_factory=list)
    explanation: ModelExplanation | None = None
    created_at: datetime | None = None


class ProtocolRequest(BaseModel):
    patient_id: str
    design_id: str
    vector_type: Literal["lentiviral", "retroviral", "transposon"] = "lentiviral"
    target_cell_dose: float = Field(default=1e8, gt=0)


class ProtocolResponse(BaseModel):
    protocol_id: str
    patient_id: str
    design_id: str
    vector_type: str
    transduction_efficiency: float | None = None
    target_cell_dose: float | None = None
    steps: list[dict] = Field(default_factory=list)
    created_at: datetime | None = None


class TherapyPlanRequest(BaseModel):
    """End-to-end: design CAR + simulate + produce protocol."""

    patient_id: str
    target_antigen: str | None = None
    car_version: str | None = None
    dose_cells: float = Field(default=1e8, gt=0)


class TherapyPlanResponse(BaseModel):
    patient_id: str
    design: CarDesignResponse
    simulation: SimulationResponse
    protocol: ProtocolResponse


class BatchSimulateRequest(BaseModel):
    patient_ids: list[str] = Field(..., min_length=1, max_length=200)


class BatchJobResponse(BaseModel):
    job_id: str
    job_type: str
    status: str
    total_items: int
    completed_items: int
    results: list[SimulationResponse] = Field(default_factory=list)
