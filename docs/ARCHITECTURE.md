# Architecture — barekat Advanced Cell Therapy Products

## Overview

Platform for designing and simulating personalized cell therapy (CAR-T):

```
Patient Omics → Target Selection → CAR Design → ML Simulation → Protocol → Clinician Narrative
```

## Components

| Layer | Tech | Role |
|-------|------|------|
| API | FastAPI | REST for patient, design, simulation, ML, Auth |
| Worker | Celery + Redis | Batch simulation, train, generate |
| DB | PostgreSQL | patients, designs, simulations, users, audit |
| Object store | MinIO | Profiles, designs, results |
| ML | scikit-learn RF | Response prediction + feature importance |

## Domain Model

- **Patient**: HLA + tumor antigen expression
- **CarDesign**: Receptor structure (scFv, costim, CD3ζ)
- **Simulation**: Response probability, CRS, neurotoxicity, explainability
- **ProductionProtocol**: Cell manufacturing instructions
- **User / AuditLog**: Identity and operation tracing

## Inference

1. If `data/models/response_predictor_v1.pkl` exists → inference with the model + real explainability
2. Otherwise → heuristic labeled `inference_source=heuristic`

## Evolution Roadmap

| Phase | Status | Content |
|-----|--------|--------|
| 1 — Scaffold | ✅ | Docker, API, pipeline, synthetic data |
| 2 — Trust | ✅ | Model in serve, explainability, eval, auth, audit, metrics, dashboard |
| 3 — Clinical UX | ⏳ | Richer UI, protocol PDF, HITL |
| 4 — Compliance | ⏳ | PHI encryption, GDPR delete, stricter Part 11 |
| 5 — Platform | ⏳ | MLflow, K8s, drift monitoring |

## Current Status (Appendix)

| Capability | Status |
|--------|--------|
| Patient registration / CAR design / simulation / protocol | ✅ |
| Trained model in inference | ✅ |
| Explainability + clinical narrative | ✅ |
| Evaluation + model registry | ✅ |
| JWT Auth + RBAC + Audit | ✅ |
| Prometheus `/metrics` | ✅ |
| Operator dashboard | ✅ (minimal) |
| Full React frontend | ❌ |
| MLflow / K8s | ❌ |
