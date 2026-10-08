"""Run the full TRL-5 validation and render JSON + Markdown evidence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from barekat_cell_therapy import __version__
from barekat_cell_therapy.validation.criteria import (
    MODEL_CRITERIA,
    ROBUSTNESS_CRITERIA,
    SYSTEM_CRITERIA,
)
from barekat_cell_therapy.validation.model_validation import run_model_validation


def run_system_check(model_dir: str, workdir: str) -> dict:
    env = {
        **os.environ,
        "APP_ENV": "development",
        "DATABASE_URL": f"sqlite:///{Path(workdir).as_posix()}/trl5.db",
        "STORAGE_BACKEND": "local",
        "LOCAL_STORAGE_DIR": f"{Path(workdir).as_posix()}/uploads",
        "MODEL_PATH": model_dir,
        "AUTH_REQUIRED": "true",
        "AUDIT_LOG_ENABLED": "true",
        "METRICS_ENABLED": "true",
        "LOG_LEVEL": "WARNING",
    }
    proc = subprocess.run(
        [sys.executable, "-m", "barekat_cell_therapy.validation.system_check"],
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"system check failed:\n{proc.stderr[-3000:]}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _rows(criteria, values: dict[str, float], scope: str) -> list[dict]:
    return [
        {
            "scope": scope,
            "id": c.id,
            "description": c.description,
            "rule": f"{c.op} {c.threshold}",
            "measured": round(float(values[c.id]), 4),
            "pass": bool(c.check(values[c.id])),
        }
        for c in criteria
    ]


def evaluate(model: dict, system: dict) -> dict:
    rows: list[dict] = []
    for name, m in model["cohorts"].items():
        vals = {
            "M1": m["auc"],
            "M2": m["auc_over_oracle"],
            "M3": m["ece"],
            "M4": m["brier_minus_baseline"],
            "M5": m["balanced_accuracy"],
            "M6": m["worst_subgroup_auc"],
        }
        rows += _rows(MODEL_CRITERIA, vals, name)
    r = model["robustness"]
    rows += _rows(
        ROBUSTNESS_CRITERIA,
        {
            "R1": r["noise_auc_drop"],
            "R2": r["missing_auc_drop"],
            "R3": r["invalid_predictions"],
            "R4": r["prediction_mismatches"],
        },
        "robustness",
    )
    rows += _rows(
        SYSTEM_CRITERIA,
        {
            "S1": system["success_rate"],
            "S2": system["latency_p95_s"],
            "S3": system["audit_events_per_plan"],
            "S4": system["rbac_pass_fraction"],
            "S5": system["ml_model_fraction"],
            "S6": system["concurrent_success_rate"],
        },
        "system",
    )
    return {"criteria": rows, "all_passed": all(x["pass"] for x in rows)}


def render_markdown(report: dict) -> str:
    ev = report["evaluation"]
    verdict = "ALL CRITERIA MET" if ev["all_passed"] else "CRITERIA NOT MET"
    out = [
        f"# TRL-5 Validation Evidence - v{report['version']}",
        f"\nGenerated: {report['generated_at']}  ",
        f"**Verdict: {verdict}**\n",
        "> Scope: in-silico validation of an integrated decision-support system in a simulated "
        "operational environment, on *synthetic* cohorts. It is evidence for TRL 5 of the "
        "software system; it is NOT clinical validation. See docs/TRL.md for the limits.\n",
        "| Scope | ID | Criterion | Rule | Measured | Result |",
        "|---|---|---|---|---|---|",
    ]
    for c in ev["criteria"]:
        res = "PASS" if c["pass"] else "**FAIL**"
        out.append(
            f"| {c['scope']} | {c['id']} | {c['description']} | {c['rule']} | "
            f"{c['measured']} | {res} |"
        )
    raw = {k: report[k] for k in ("model", "system")}
    out.append("\n## Raw measurements\n")
    out.append("```json\n" + json.dumps(raw, indent=2, ensure_ascii=False) + "\n```\n")
    return "\n".join(out)


def run_all(out_dir: str = "docs/validation") -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        model_dir = str(Path(tmp) / "models")
        model = run_model_validation(model_dir)
        system = run_system_check(model_dir, tmp)
    report = {
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": model,
        "system": system,
    }
    report["evaluation"] = evaluate(model, system)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "trl5_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out / "TRL5_REPORT.md").write_text(render_markdown(report), encoding="utf-8")
    return report
