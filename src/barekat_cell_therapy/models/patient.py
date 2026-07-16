"""ORM models for patients, CAR designs, and simulations."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from barekat_cell_therapy.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="registered")
    hla_profile_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    antigen_expression_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    best_target_antigen: Mapped[str | None] = mapped_column(String(32), nullable=True)
    profile_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CarDesign(Base):
    __tablename__ = "car_designs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    design_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    patient_id: Mapped[str] = mapped_column(String(64), index=True)
    target_antigen: Mapped[str] = mapped_column(String(32))
    car_version: Mapped[str] = mapped_column(String(16))
    scfv_affinity: Mapped[float | None] = mapped_column(Float, nullable=True)
    costimulatory_domains: Mapped[str | None] = mapped_column(String(128), nullable=True)
    design_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    design_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    simulation_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    patient_id: Mapped[str] = mapped_column(String(64), index=True)
    design_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    response_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_response: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    crs_grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    neurotoxicity_risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    efficacy_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    safety_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitudinal_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProductionProtocol(Base):
    __tablename__ = "production_protocols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    protocol_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    patient_id: Mapped[str] = mapped_column(String(64), index=True)
    design_id: Mapped[str] = mapped_column(String(64), index=True)
    vector_type: Mapped[str] = mapped_column(String(32), default="lentiviral")
    transduction_efficiency: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_cell_dose: Mapped[float | None] = mapped_column(Float, nullable=True)
    protocol_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    protocol_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    job_type: Mapped[str] = mapped_column(String(32), default="simulate")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    completed_items: Mapped[int] = mapped_column(Integer, default=0)
    results_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
