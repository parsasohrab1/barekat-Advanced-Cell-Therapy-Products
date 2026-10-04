# API Reference

Base: `/api/v1` — Docs: `/docs` — Dashboard: `/dashboard/` — Metrics: `/metrics`

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/live` | Liveness |
| GET | `/health/ready` | Readiness (DB) |
| GET | `/health` | Aggregate health |

## Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Obtain JWT |
| GET | `/auth/me` | Current profile |

Roles: `viewer` < `clinician` < `scientist` < `admin`  
`AUTH_REQUIRED=false` allows access without a token during development.

## Patients / Designs / Therapy

| Method | Path | Description |
|--------|------|-------------|
| POST | `/patients/` | Register profile |
| GET | `/patients/{id}` | Details |
| POST | `/designs/` | CAR design |
| GET | `/designs/{id}` | Design details |
| POST | `/simulations/` | Simulation |
| GET | `/simulations/{id}` | Result |
| POST | `/protocols/` | Production protocol |
| POST | `/therapy/plan` | end-to-end |
| POST | `/simulations/batch` | batch async |
| GET | `/jobs/{id}` | Job status |

## ML

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ml/registry` | Model versions |
| POST | `/ml/evaluate` | CV evaluation on a dataset |

## Audit

| Method | Path | Description |
|--------|------|-------------|
| GET | `/audit/` | Latest events (scientist+) |
