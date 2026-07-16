"""Celery tasks."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from barekat_cell_therapy.core.database import SessionLocal
from barekat_cell_therapy.data.synthetic import generate_cell_therapy_data
from barekat_cell_therapy.ml.trainer import train_response_model
from barekat_cell_therapy.models.patient import BatchJob
from barekat_cell_therapy.schemas import CarDesignRequest, SimulationRequest
from barekat_cell_therapy.services.therapy import create_car_design, run_simulation
from barekat_cell_therapy.tasks.celery_app import celery_app


@celery_app.task(name="barekat_cell_therapy.generate_synthetic_data")
def generate_synthetic_data_task(n_patients: int = 300) -> dict:
    df = generate_cell_therapy_data(n_patients=n_patients)
    path = "data/raw/synthetic_patients.csv"
    df.to_csv(path, index=False)
    return {"path": path, "n_patients": len(df)}


@celery_app.task(name="barekat_cell_therapy.train_model")
def train_model_task(csv_path: str = "data/raw/synthetic_patients.csv") -> dict:
    import pandas as pd

    df = pd.read_csv(csv_path)
    return train_response_model(df)


@celery_app.task(name="barekat_cell_therapy.batch_simulate")
def batch_simulate_task(job_id: str, patient_ids: list[str]) -> dict:
    db = SessionLocal()
    try:
        job = db.query(BatchJob).filter(BatchJob.job_id == job_id).first()
        if job:
            job.status = "running"
            db.commit()

        results = []
        for pid in patient_ids:
            design = create_car_design(db, CarDesignRequest(patient_id=pid))
            sim = run_simulation(
                db,
                SimulationRequest(patient_id=pid, design_id=design.design_id),
            )
            results.append(sim.model_dump(mode="json"))
            if job:
                job.completed_items = len(results)
                db.commit()

        if job:
            job.status = "completed"
            job.results_json = json.dumps(results)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

        return {"job_id": job_id, "completed": len(results)}
    except Exception as exc:
        if job:
            job.status = "failed"
            job.results_json = json.dumps({"error": str(exc)})
            db.commit()
        raise
    finally:
        db.close()
