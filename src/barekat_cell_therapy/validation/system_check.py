"""Integrated-system check, run in a subprocess with a hermetic environment.

Environment (set by the runner): DATABASE_URL=sqlite, STORAGE_BACKEND=local, MODEL_PATH=<trained
model dir>, AUTH_REQUIRED=true. Prints one JSON document on the last stdout line.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from fastapi.testclient import TestClient

from barekat_cell_therapy.api.main import create_app
from barekat_cell_therapy.core.database import Base, SessionLocal, engine
from barekat_cell_therapy.data.synthetic import TUMOR_ANTIGENS
from barekat_cell_therapy.models import patient as _p  # noqa: F401  (register tables)
from barekat_cell_therapy.models import user as _u  # noqa: F401
from barekat_cell_therapy.models.user import AuditLog

P = "/api/v1"
PW = "pw-123456"


def _hdr(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _user(client, admin_token, email, role):
    client.post(
        f"{P}/auth/register",
        json={"email": email, "password": PW, "role": role},
        headers=_hdr(admin_token) if admin_token else None,
    )
    return client.post(f"{P}/auth/login", json={"email": email, "password": PW}).json()


def _patient_payload(rng, pid):
    return {
        "patient_id": pid,
        "hla_profile": [{"allele": "HLA-A*02:01", "copies": int(rng.integers(0, 3))}],
        "antigen_expression": [
            {"antigen": a, "expression_pct": float(np.clip(rng.gamma(2, 15), 0, 100))}
            for a in TUMOR_ANTIGENS
        ],
    }


def main() -> None:
    Base.metadata.create_all(engine)
    client = TestClient(create_app())
    rng = np.random.default_rng(1)

    admin = _user(client, None, "admin@trl5.test", "admin")  # bootstrap user
    clin = _user(client, admin["access_token"], "clin@trl5.test", "clinician")
    sci = _user(client, admin["access_token"], "sci@trl5.test", "scientist")
    # self-registration asking for admin must be downgraded to viewer
    client.post(
        f"{P}/auth/register", json={"email": "evil@trl5.test", "password": PW, "role": "admin"}
    )
    evil = client.post(f"{P}/auth/login", json={"email": "evil@trl5.test", "password": PW}).json()

    pl = _patient_payload(rng, "RBAC_1")
    hc, hv, hs = _hdr(clin["access_token"]), _hdr(evil["access_token"]), _hdr(sci["access_token"])
    bad_antigen = {
        "patient_id": "X",
        "antigen_expression": [{"antigen": "CD19", "expression_pct": 500}],
    }
    checks = {
        "anonymous_blocked": client.post(f"{P}/patients/", json=pl).status_code == 401,
        "self_register_downgraded": evil["role"] == "viewer",
        "viewer_cannot_write": client.post(f"{P}/patients/", json=pl, headers=hv).status_code
        == 403,
        "clinician_can_write": client.post(f"{P}/patients/", json=pl, headers=hc).status_code
        == 201,
        "viewer_can_read": client.get(f"{P}/patients/RBAC_1", headers=hv).status_code == 200,
        "clinician_blocked_from_audit": client.get(f"{P}/audit/", headers=hc).status_code == 403,
        "scientist_reads_audit": client.get(f"{P}/audit/", headers=hs).status_code == 200,
        "bad_token_rejected": client.get(
            f"{P}/patients/RBAC_1", headers=_hdr("garbage")
        ).status_code
        == 401,
        "duplicate_patient_409": client.post(f"{P}/patients/", json=pl, headers=hc).status_code
        == 409,
        "unknown_patient_404": client.post(
            f"{P}/therapy/plan", json={"patient_id": "NOPE"}, headers=hc
        ).status_code
        == 404,
        "invalid_payload_422": client.post(
            f"{P}/patients/", json=bad_antigen, headers=hc
        ).status_code
        == 422,
    }

    n = 30
    lat, ok, ml = [], 0, 0
    for i in range(n):
        pid = f"VAL_{i:03d}"
        client.post(f"{P}/patients/", json=_patient_payload(rng, pid), headers=hc)
        t = time.perf_counter()
        r = client.post(f"{P}/therapy/plan", json={"patient_id": pid}, headers=hc)
        lat.append(time.perf_counter() - t)
        if r.status_code == 201:
            sim = r.json()["simulation"]
            got = client.get(f"{P}/simulations/{sim['simulation_id']}", headers=hc)
            if got.status_code == 200:
                ok += 1
            ml += sim["inference_source"] == "ml_model"

    def concurrent_plan(i):
        r = client.post(f"{P}/therapy/plan", json={"patient_id": f"VAL_{i % n:03d}"}, headers=hc)
        return r.status_code == 201

    with ThreadPoolExecutor(8) as ex:
        conc = list(ex.map(concurrent_plan, range(24)))

    with SessionLocal() as db:
        by_action: dict[str, int] = {}
        for (a,) in db.query(AuditLog.action).all():
            by_action[a] = by_action.get(a, 0) + 1
    plans = by_action.get("simulation.run", 0)
    # every plan must leave one design, one simulation and one protocol audit row
    audit_per_plan = (
        by_action.get("design.create", 0)
        + by_action.get("simulation.run", 0)
        + by_action.get("protocol.create", 0)
    ) / max(plans, 1)

    print(
        json.dumps(
            {
                "rbac_checks": checks,
                "rbac_pass_fraction": sum(checks.values()) / len(checks),
                "n_plans": n,
                "success_rate": ok / n,
                "ml_model_fraction": ml / n,
                "latency_p50_s": round(float(np.percentile(lat, 50)), 4),
                "latency_p95_s": round(float(np.percentile(lat, 95)), 4),
                "concurrent_success_rate": sum(conc) / len(conc),
                "audit_actions": by_action,
                "audit_events_per_plan": round(audit_per_plan, 3),
            }
        )
    )


if __name__ == "__main__":
    main()
