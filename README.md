# barekat-Advanced-Cell-Therapy-Products

Platform for designing and simulating personalized cell therapies (CAR-T) — version **0.2** (Trust phase).

## Features

- Recording HLA profiles and tumor antigen expression
- Target selection and CAR construct design
- Response simulation with a **trained model**, CRS, neurotoxicity and Explainability
- Clinical narrative understandable to physicians
- Model evaluation (CV, Se/Sp with CI) and version registry
- Auth (JWT) + RBAC + Audit trail
- Prometheus metrics and operator dashboard

## Quick Start

```bash
cp .env.example .env
make setup
make infra
make migrate
make generate-data
make train
make evaluate
make api
```

- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8000/dashboard/
- Metrics: http://localhost:8000/metrics
- MinIO: http://localhost:9001

## Example

```bash
curl -X POST http://localhost:8000/api/v1/patients/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "CT_0001",
    "hla_profile": [{"allele": "HLA-A*02:01", "copies": 1}],
    "antigen_expression": [{"antigen": "CD19", "expression_pct": 78.5}]
  }'

curl -X POST http://localhost:8000/api/v1/therapy/plan \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "CT_0001", "dose_cells": 1e8}'
```

## Documentation

- [Architecture & roadmap](docs/ARCHITECTURE.md)
- [API](docs/API.md)
- [Infrastructure](docs/INFRASTRUCTURE.md)

## Roadmap

| Phase | Status |
|-----|--------|
| 1 Scaffold | ✅ |
| 2 Trust (model, explain, auth, audit, metrics) | ✅ |
| 3 Clinical UX | ⏳ |
| 4 Strict Compliance | ⏳ |
