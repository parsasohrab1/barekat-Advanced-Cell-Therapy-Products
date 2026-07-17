"""سرویس‌های دامنه: بیمار، طراحی CAR، شبیه‌سازی، پروتکل."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from barekat_cell_therapy.core.storage import get_storage
from barekat_cell_therapy.models.patient import CarDesign, Patient, ProductionProtocol, Simulation
from barekat_cell_therapy.pipeline.car_design import design_car
from barekat_cell_therapy.pipeline.protocol import generate_protocol
from barekat_cell_therapy.pipeline.simulation import simulate_therapy
from barekat_cell_therapy.pipeline.target_selection import select_best_target
from barekat_cell_therapy.schemas import (
    AntigenExpression,
    CarDesignRequest,
    CarDesignResponse,
    FeatureContribution,
    HlaAllele,
    LongitudinalPoint,
    ModelExplanation,
    PatientCreate,
    PatientResponse,
    ProtocolRequest,
    ProtocolResponse,
    SimulationRequest,
    SimulationResponse,
    TherapyPlanRequest,
    TherapyPlanResponse,
)


def _parse_hla(raw: str | None) -> list[HlaAllele]:
    if not raw:
        return []
    data = json.loads(raw)
    return [HlaAllele(**item) for item in data]


def _parse_antigens(raw: str | None) -> list[AntigenExpression]:
    if not raw:
        return []
    data = json.loads(raw)
    return [AntigenExpression(**item) for item in data]


def _hla_dict(alleles: list[HlaAllele]) -> dict[str, int]:
    return {a.allele: a.copies for a in alleles}


def _antigen_dict(items: list[AntigenExpression]) -> dict[str, float]:
    return {a.antigen: a.expression_pct for a in items}


def create_patient(db: Session, payload: PatientCreate) -> PatientResponse:
    antigens = _antigen_dict(payload.antigen_expression)
    best = select_best_target(antigens) if antigens else None

    profile = {
        "patient_id": payload.patient_id,
        "hla": [a.model_dump() for a in payload.hla_profile],
        "antigens": [a.model_dump() for a in payload.antigen_expression],
        "best_target": best,
    }
    storage = get_storage()
    object_key = storage.profile_key(payload.patient_id)
    storage.upload_json(profile, object_key)

    patient = Patient(
        patient_id=payload.patient_id,
        status="profiled" if antigens else "registered",
        hla_profile_json=json.dumps([a.model_dump() for a in payload.hla_profile]),
        antigen_expression_json=json.dumps([a.model_dump() for a in payload.antigen_expression]),
        best_target_antigen=best,
        profile_object_key=object_key,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    try:
        from barekat_cell_therapy.core.metrics import PATIENT_COUNTER

        PATIENT_COUNTER.inc()
    except Exception:
        pass
    from barekat_cell_therapy.services.audit import write_audit

    write_audit(
        db,
        action="patient.create",
        resource_type="patient",
        resource_id=payload.patient_id,
        detail={"best_target": best},
    )
    return patient_to_response(patient)


def get_patient(db: Session, patient_id: str) -> Patient | None:
    return db.query(Patient).filter(Patient.patient_id == patient_id).first()


def patient_to_response(patient: Patient) -> PatientResponse:
    return PatientResponse(
        patient_id=patient.patient_id,
        status=patient.status,
        best_target_antigen=patient.best_target_antigen,
        hla_profile=_parse_hla(patient.hla_profile_json),
        antigen_expression=_parse_antigens(patient.antigen_expression_json),
        profile_object_key=patient.profile_object_key,
        created_at=patient.created_at,
    )


def create_car_design(db: Session, payload: CarDesignRequest) -> CarDesignResponse:
    patient = get_patient(db, payload.patient_id)
    if patient is None:
        raise ValueError(f"Patient not found: {payload.patient_id}")

    target = payload.target_antigen or patient.best_target_antigen
    if not target:
        raise ValueError("No target antigen available; provide target_antigen or antigen profile")

    design = design_car(
        patient_id=payload.patient_id,
        target_antigen=target,
        car_version=payload.car_version,
        costimulatory_domains=payload.costimulatory_domains or None,
    )

    storage = get_storage()
    object_key = storage.car_design_key(design["design_id"])
    storage.upload_json(design, object_key)

    row = CarDesign(
        design_id=design["design_id"],
        patient_id=payload.patient_id,
        target_antigen=design["target_antigen"],
        car_version=design["car_version"],
        scfv_affinity=design["scfv_affinity"],
        costimulatory_domains="+".join(design["costimulatory_domains"]),
        design_json=json.dumps(design),
        design_object_key=object_key,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return design_to_response(row, design)


def design_to_response(row: CarDesign, design: dict | None = None) -> CarDesignResponse:
    data = design or (json.loads(row.design_json) if row.design_json else {})
    domains = (
        row.costimulatory_domains.split("+")
        if row.costimulatory_domains
        else data.get("costimulatory_domains", [])
    )
    return CarDesignResponse(
        design_id=row.design_id,
        patient_id=row.patient_id,
        target_antigen=row.target_antigen,
        car_version=row.car_version,
        scfv_affinity=row.scfv_affinity,
        costimulatory_domains=domains,
        design_summary=data.get("structure", {}),
        created_at=row.created_at,
    )


def run_simulation(db: Session, payload: SimulationRequest) -> SimulationResponse:
    patient = get_patient(db, payload.patient_id)
    if patient is None:
        raise ValueError(f"Patient not found: {payload.patient_id}")

    design_row = db.query(CarDesign).filter(CarDesign.design_id == payload.design_id).first()
    if design_row is None:
        raise ValueError(f"CAR design not found: {payload.design_id}")

    result = simulate_therapy(
        patient_id=payload.patient_id,
        design_id=payload.design_id,
        target_antigen=design_row.target_antigen,
        car_version=design_row.car_version,
        antigen_expression=_antigen_dict(_parse_antigens(patient.antigen_expression_json)),
        hla_profile=_hla_dict(_parse_hla(patient.hla_profile_json)),
        dose_cells=payload.dose_cells,
        horizon_days=payload.horizon_days,
    )

    storage = get_storage()
    object_key = storage.simulation_key(result["simulation_id"])
    storage.upload_json(result, object_key)

    row = Simulation(
        simulation_id=result["simulation_id"],
        patient_id=payload.patient_id,
        design_id=payload.design_id,
        status=result["status"],
        response_probability=result["response_probability"],
        predicted_response=result["predicted_response"],
        crs_grade=result["crs_grade"],
        neurotoxicity_risk=result["neurotoxicity_risk"],
        efficacy_score=result["efficacy_score"],
        safety_score=result["safety_score"],
        longitudinal_json=json.dumps(result["longitudinal"]),
        explanation_json=json.dumps(
            {
                **result["explanation"],
                "clinical_narrative": result.get("clinical_narrative"),
                "inference_source": result.get("inference_source"),
            }
        ),
        result_object_key=object_key,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    try:
        from barekat_cell_therapy.core.metrics import SIMULATION_COUNTER

        outcome = "responder" if result.get("predicted_response") else "non_responder"
        SIMULATION_COUNTER.labels(outcome=outcome).inc()
    except Exception:
        pass
    return simulation_to_response(row, result)


def simulation_to_response(row: Simulation, result: dict | None = None) -> SimulationResponse:
    data = result or {}
    longitudinal = data.get("longitudinal")
    if longitudinal is None and row.longitudinal_json:
        longitudinal = json.loads(row.longitudinal_json)

    explanation = data.get("explanation")
    narrative = data.get("clinical_narrative")
    inference_source = data.get("inference_source")

    if row.explanation_json and explanation is None:
        stored = json.loads(row.explanation_json)
        narrative = narrative or stored.get("clinical_narrative")
        inference_source = inference_source or stored.get("inference_source")
        explanation = {
            k: stored[k]
            for k in ("model_version", "predicted_outcome", "confidence", "top_features", "method")
            if k in stored
        }

    expl = None
    if explanation:
        expl = ModelExplanation(
            model_version=explanation["model_version"],
            predicted_outcome=explanation["predicted_outcome"],
            confidence=explanation["confidence"],
            top_features=[FeatureContribution(**f) for f in explanation.get("top_features", [])],
            method=explanation.get("method", "feature_importance"),
        )

    return SimulationResponse(
        simulation_id=row.simulation_id,
        patient_id=row.patient_id,
        design_id=row.design_id,
        status=row.status,
        response_probability=row.response_probability,
        predicted_response=row.predicted_response,
        crs_grade=row.crs_grade,
        neurotoxicity_risk=row.neurotoxicity_risk,
        efficacy_score=row.efficacy_score,
        safety_score=row.safety_score,
        longitudinal=[LongitudinalPoint(**p) for p in (longitudinal or [])],
        explanation=expl,
        clinical_narrative=narrative,
        inference_source=inference_source,
        created_at=row.created_at,
    )


def create_protocol(db: Session, payload: ProtocolRequest) -> ProtocolResponse:
    design_row = db.query(CarDesign).filter(CarDesign.design_id == payload.design_id).first()
    if design_row is None:
        raise ValueError(f"CAR design not found: {payload.design_id}")

    protocol = generate_protocol(
        patient_id=payload.patient_id,
        design_id=payload.design_id,
        target_antigen=design_row.target_antigen,
        car_version=design_row.car_version,
        vector_type=payload.vector_type,
        target_cell_dose=payload.target_cell_dose,
    )

    storage = get_storage()
    object_key = storage.protocol_key(payload.patient_id, payload.design_id)
    storage.upload_json(protocol, object_key)

    row = ProductionProtocol(
        protocol_id=protocol["protocol_id"],
        patient_id=payload.patient_id,
        design_id=payload.design_id,
        vector_type=protocol["vector_type"],
        transduction_efficiency=protocol["transduction_efficiency"],
        target_cell_dose=protocol["target_cell_dose"],
        protocol_json=json.dumps(protocol),
        protocol_object_key=object_key,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ProtocolResponse(
        protocol_id=row.protocol_id,
        patient_id=row.patient_id,
        design_id=row.design_id,
        vector_type=row.vector_type,
        transduction_efficiency=row.transduction_efficiency,
        target_cell_dose=row.target_cell_dose,
        steps=protocol["steps"],
        created_at=row.created_at,
    )


def create_therapy_plan(db: Session, payload: TherapyPlanRequest) -> TherapyPlanResponse:
    design = create_car_design(
        db,
        CarDesignRequest(
            patient_id=payload.patient_id,
            target_antigen=payload.target_antigen,
            car_version=payload.car_version,
        ),
    )
    simulation = run_simulation(
        db,
        SimulationRequest(
            patient_id=payload.patient_id,
            design_id=design.design_id,
            dose_cells=payload.dose_cells,
        ),
    )
    protocol = create_protocol(
        db,
        ProtocolRequest(
            patient_id=payload.patient_id,
            design_id=design.design_id,
            target_cell_dose=payload.dose_cells,
        ),
    )
    return TherapyPlanResponse(
        patient_id=payload.patient_id,
        design=design,
        simulation=simulation,
        protocol=protocol,
    )
