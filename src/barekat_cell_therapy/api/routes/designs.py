"""CAR design endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from barekat_cell_therapy.core.database import get_db
from barekat_cell_therapy.models.patient import CarDesign
from barekat_cell_therapy.schemas import CarDesignRequest, CarDesignResponse
from barekat_cell_therapy.services import therapy

router = APIRouter()


@router.post("/designs/", response_model=CarDesignResponse, status_code=201)
def create_design(payload: CarDesignRequest, db: Session = Depends(get_db)) -> CarDesignResponse:
    try:
        return therapy.create_car_design(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/designs/{design_id}", response_model=CarDesignResponse)
def get_design(design_id: str, db: Session = Depends(get_db)) -> CarDesignResponse:
    row = db.query(CarDesign).filter(CarDesign.design_id == design_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Design not found")
    return therapy.design_to_response(row)
