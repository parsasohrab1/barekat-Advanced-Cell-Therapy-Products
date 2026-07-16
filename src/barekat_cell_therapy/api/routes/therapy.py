"""Simulation and therapy plan endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from barekat_cell_therapy.core.database import get_db
from barekat_cell_therapy.models.patient import BatchJob, Simulation
from barekat_cell_therapy.schemas import (
    BatchJobResponse,
    BatchSimulateRequest,
    ProtocolRequest,
    ProtocolResponse,
    SimulationRequest,
    SimulationResponse,
    TherapyPlanRequest,
    TherapyPlanResponse,
)
from barekat_cell_therapy.services import therapy

router = APIRouter()


@router.post("/simulations/", response_model=SimulationResponse, status_code=201)
def create_simulation(
    payload: SimulationRequest, db: Session = Depends(get_db)
) -> SimulationResponse:
    try:
        return therapy.run_simulation(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/simulations/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: str, db: Session = Depends(get_db)) -> SimulationResponse:
    row = db.query(Simulation).filter(Simulation.simulation_id == simulation_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return therapy.simulation_to_response(row)


@router.post("/protocols/", response_model=ProtocolResponse, status_code=201)
def create_protocol(payload: ProtocolRequest, db: Session = Depends(get_db)) -> ProtocolResponse:
    try:
        return therapy.create_protocol(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/therapy/plan", response_model=TherapyPlanResponse, status_code=201)
def create_therapy_plan(
    payload: TherapyPlanRequest, db: Session = Depends(get_db)
) -> TherapyPlanResponse:
    try:
        return therapy.create_therapy_plan(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/simulations/batch", response_model=BatchJobResponse, status_code=202)
def batch_simulate(
    payload: BatchSimulateRequest, db: Session = Depends(get_db)
) -> BatchJobResponse:
    job_id = str(uuid.uuid4())
    job = BatchJob(
        job_id=job_id,
        job_type="simulate",
        status="pending",
        total_items=len(payload.patient_ids),
        completed_items=0,
    )
    db.add(job)
    db.commit()

    try:
        from barekat_cell_therapy.tasks import batch_simulate_task

        batch_simulate_task.delay(job_id, payload.patient_ids)
    except Exception:
        # Fallback: run inline if Celery unavailable
        from barekat_cell_therapy.tasks import batch_simulate_task as sync_task

        sync_task(job_id, payload.patient_ids)
        job = db.query(BatchJob).filter(BatchJob.job_id == job_id).first()

    return BatchJobResponse(
        job_id=job_id,
        job_type="simulate",
        status=job.status if job else "pending",
        total_items=len(payload.patient_ids),
        completed_items=job.completed_items if job else 0,
    )


@router.get("/jobs/{job_id}", response_model=BatchJobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> BatchJobResponse:
    import json

    job = db.query(BatchJob).filter(BatchJob.job_id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    results = []
    if job.results_json:
        try:
            results = [SimulationResponse(**r) for r in json.loads(job.results_json)]
        except Exception:
            results = []
    return BatchJobResponse(
        job_id=job.job_id,
        job_type=job.job_type,
        status=job.status,
        total_items=job.total_items,
        completed_items=job.completed_items,
        results=results,
    )
