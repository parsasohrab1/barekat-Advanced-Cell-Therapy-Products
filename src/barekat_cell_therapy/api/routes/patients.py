"""Patient profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from barekat_cell_therapy.core.database import get_db
from barekat_cell_therapy.schemas import PatientCreate, PatientResponse
from barekat_cell_therapy.services import therapy

router = APIRouter()


@router.post("/patients/", response_model=PatientResponse, status_code=201)
def register_patient(payload: PatientCreate, db: Session = Depends(get_db)) -> PatientResponse:
    existing = therapy.get_patient(db, payload.patient_id)
    if existing:
        raise HTTPException(status_code=409, detail="Patient already exists")
    return therapy.create_patient(db, payload)


@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)) -> PatientResponse:
    patient = therapy.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return therapy.patient_to_response(patient)
