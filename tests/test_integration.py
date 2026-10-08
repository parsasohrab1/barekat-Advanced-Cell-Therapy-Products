"""Integrated-system tests: API + DB + storage + trained model + RBAC + audit (hermetic)."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from barekat_cell_therapy.api.main import create_app
from barekat_cell_therapy.core.config import Settings, get_settings
from barekat_cell_therapy.core.database import Base, engine
from barekat_cell_therapy.data.synthetic import generate_cell_therapy_data
from barekat_cell_therapy.ml.predictor import load_response_model
from barekat_cell_therapy.ml.trainer import train_response_model
from barekat_cell_therapy.models import patient as _p  # noqa: F401
from barekat_cell_therapy.models import user as _u  # noqa: F401

P = "/api/v1"
REPO_REGISTRY = Path(__file__).resolve().parents[1] / "data" / "models" / "registry.json"


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(engine)
    df = generate_cell_therapy_data(300, seed=1)
    train_response_model(df, output_dir=get_settings().model_path)
    load_response_model.cache_clear()
    return TestClient(create_app())


def _patient(pid):
    return {
        "patient_id": pid,
        "hla_profile": [{"allele": "HLA-A*02:01", "copies": 1}],
        "antigen_expression": [
            {"antigen": "CD19", "expression_pct": 78.5},
            {"antigen": "HER2", "expression_pct": 12.0},
        ],
    }


def test_end_to_end_plan_uses_trained_model(client):
    assert client.post(f"{P}/patients/", json=_patient("E2E_1")).status_code == 201
    r = client.post(f"{P}/therapy/plan", json={"patient_id": "E2E_1"})
    assert r.status_code == 201
    body = r.json()
    assert body["simulation"]["inference_source"] == "ml_model"
    assert body["simulation"]["explanation"]["method"] == "occlusion"
    assert 0 <= body["simulation"]["response_probability"] <= 1
    assert body["protocol"]["steps"]
    sim_id = body["simulation"]["simulation_id"]
    assert client.get(f"{P}/simulations/{sim_id}").json()["simulation_id"] == sim_id


def test_training_never_touches_repo_registry():
    before = REPO_REGISTRY.read_bytes() if REPO_REGISTRY.exists() else None
    df = generate_cell_therapy_data(60, seed=2)
    train_response_model(df, output_dir=get_settings().model_path)
    after = REPO_REGISTRY.read_bytes() if REPO_REGISTRY.exists() else None
    assert before == after


def test_rbac_and_audit(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "auth_required", True)
    assert client.post(f"{P}/patients/", json=_patient("RB_0")).status_code == 401

    def login(email, role, admin_tok=None):
        h = {"Authorization": f"Bearer {admin_tok}"} if admin_tok else None
        client.post(
            f"{P}/auth/register",
            json={"email": email, "password": "pw-123456", "role": role},
            headers=h,
        )
        return client.post(f"{P}/auth/login", json={"email": email, "password": "pw-123456"}).json()

    first = login("first@t.test", "admin")  # bootstrap; may already exist from earlier runs
    admin_tok = first["access_token"]
    # self-registration can never grant a privileged role
    evil = login("evil@t.test", "admin")
    assert evil["role"] == "viewer"
    viewer = {"Authorization": f"Bearer {evil['access_token']}"}
    assert client.post(f"{P}/patients/", json=_patient("RB_1"), headers=viewer).status_code == 403

    clin = login("c@t.test", "clinician", admin_tok)
    hc = {"Authorization": f"Bearer {clin['access_token']}"}
    assert client.post(f"{P}/patients/", json=_patient("RB_2"), headers=hc).status_code == 201
    assert client.get(f"{P}/patients/RB_2", headers=viewer).status_code == 200
    assert client.get(f"{P}/audit/", headers=hc).status_code == 403
    rows = client.get(f"{P}/audit/", headers={"Authorization": f"Bearer {admin_tok}"}).json()
    actions = {r["action"] for r in rows}
    assert {"patient.create", "patient.read", "user.login"} <= actions
    created = [r for r in rows if r["action"] == "patient.create" and r["resource_id"] == "RB_2"]
    assert created and created[0]["actor_id"] == clin["user_id"]


def test_missing_antigens_do_not_crash(client):
    payload = {"patient_id": "SPARSE_1", "antigen_expression": [], "hla_profile": []}
    assert client.post(f"{P}/patients/", json=payload).status_code == 201
    r = client.post(f"{P}/therapy/plan", json={"patient_id": "SPARSE_1", "target_antigen": "CD19"})
    assert r.status_code == 201
    assert json.dumps(r.json())  # serialisable, finite


def test_production_refuses_dev_security_defaults():
    with pytest.raises(ValueError):
        Settings(app_env="production")
    with pytest.raises(ValueError):
        Settings(app_env="production", secret_key="x" * 40, auth_required=False)
    assert Settings(app_env="production", secret_key="x" * 40, auth_required=True)
