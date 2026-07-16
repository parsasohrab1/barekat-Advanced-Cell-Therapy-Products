"""Initial schema for cell therapy platform

Revision ID: 001
Revises:
Create Date: 2026-07-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="registered"),
        sa.Column("hla_profile_json", sa.Text(), nullable=True),
        sa.Column("antigen_expression_json", sa.Text(), nullable=True),
        sa.Column("best_target_antigen", sa.String(32), nullable=True),
        sa.Column("profile_object_key", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patients_patient_id", "patients", ["patient_id"], unique=True)

    op.create_table(
        "car_designs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("design_id", sa.String(64), nullable=False),
        sa.Column("patient_id", sa.String(64), nullable=False),
        sa.Column("target_antigen", sa.String(32), nullable=False),
        sa.Column("car_version", sa.String(16), nullable=False),
        sa.Column("scfv_affinity", sa.Float(), nullable=True),
        sa.Column("costimulatory_domains", sa.String(128), nullable=True),
        sa.Column("design_json", sa.Text(), nullable=True),
        sa.Column("design_object_key", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_car_designs_design_id", "car_designs", ["design_id"], unique=True)
    op.create_index("ix_car_designs_patient_id", "car_designs", ["patient_id"])

    op.create_table(
        "simulations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("simulation_id", sa.String(64), nullable=False),
        sa.Column("patient_id", sa.String(64), nullable=False),
        sa.Column("design_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("response_probability", sa.Float(), nullable=True),
        sa.Column("predicted_response", sa.Boolean(), nullable=True),
        sa.Column("crs_grade", sa.Integer(), nullable=True),
        sa.Column("neurotoxicity_risk", sa.Float(), nullable=True),
        sa.Column("efficacy_score", sa.Float(), nullable=True),
        sa.Column("safety_score", sa.Float(), nullable=True),
        sa.Column("longitudinal_json", sa.Text(), nullable=True),
        sa.Column("explanation_json", sa.Text(), nullable=True),
        sa.Column("result_object_key", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_simulations_simulation_id", "simulations", ["simulation_id"], unique=True)
    op.create_index("ix_simulations_patient_id", "simulations", ["patient_id"])
    op.create_index("ix_simulations_design_id", "simulations", ["design_id"])

    op.create_table(
        "production_protocols",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("protocol_id", sa.String(64), nullable=False),
        sa.Column("patient_id", sa.String(64), nullable=False),
        sa.Column("design_id", sa.String(64), nullable=False),
        sa.Column("vector_type", sa.String(32), nullable=False, server_default="lentiviral"),
        sa.Column("transduction_efficiency", sa.Float(), nullable=True),
        sa.Column("target_cell_dose", sa.Float(), nullable=True),
        sa.Column("protocol_json", sa.Text(), nullable=True),
        sa.Column("protocol_object_key", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_production_protocols_protocol_id", "production_protocols", ["protocol_id"], unique=True
    )
    op.create_index("ix_production_protocols_patient_id", "production_protocols", ["patient_id"])
    op.create_index("ix_production_protocols_design_id", "production_protocols", ["design_id"])

    op.create_table(
        "batch_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.String(36), nullable=False),
        sa.Column("job_type", sa.String(32), nullable=False, server_default="simulate"),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("total_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("results_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_batch_jobs_job_id", "batch_jobs", ["job_id"], unique=True)


def downgrade() -> None:
    op.drop_table("batch_jobs")
    op.drop_table("production_protocols")
    op.drop_table("simulations")
    op.drop_table("car_designs")
    op.drop_table("patients")
