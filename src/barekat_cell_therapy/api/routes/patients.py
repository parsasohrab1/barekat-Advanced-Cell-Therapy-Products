"""Patient profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from barekat_cell_therapy.core.database import get_db
from barekat_cell_therapy.core.rbac import require_role
from barekat_cell_therapy.models.user import User
from barekat_cell_therapy.services.audit import write_audit
from barekat_cell_therapy.schemas import PatientCreate, PatientResponse
from barekat_cell_therapy.services import therapy

router = APIRouter()


@router.post("/patients/", response_model=PatientResponse, status_code=201)
def register_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(require_role("clinician")),
) -> PatientResponse:
    existing = therapy.get_patient(db, payload.patient_id)
    if existing:
        raise HTTPException(status_code=409, detail="Patient already exists")
    return therapy.create_patient(db, payload, actor_id=user.user_id if user else None)


@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(require_role("viewer")),
) -> PatientResponse:
    patient = therapy.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    # PHI read access is always traceable to an actor
    write_audit(db, "patient.read", "patient", patient_id, actor_id=user.user_id if user else None)
    return therapy.patient_to_response(patient)
