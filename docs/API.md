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
| POST | `/auth/register` | ثبت کاربر |
| POST | `/auth/login` | دریافت JWT |
| GET | `/auth/me` | پروفایل جاری |

Roles: `viewer` < `clinician` < `scientist` < `admin`  
`AUTH_REQUIRED=false` در توسعه اجازه دسترسی بدون توکن می‌دهد.

## Patients / Designs / Therapy

| Method | Path | Description |
|--------|------|-------------|
| POST | `/patients/` | ثبت پروفایل |
| GET | `/patients/{id}` | جزئیات |
| POST | `/designs/` | طراحی CAR |
| GET | `/designs/{id}` | جزئیات طرح |
| POST | `/simulations/` | شبیه‌سازی |
| GET | `/simulations/{id}` | نتیجه |
| POST | `/protocols/` | پروتکل تولید |
| POST | `/therapy/plan` | end-to-end |
| POST | `/simulations/batch` | batch async |
| GET | `/jobs/{id}` | وضعیت job |

## ML

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ml/registry` | نسخه‌های مدل |
| POST | `/ml/evaluate` | ارزیابی CV روی dataset |

## Audit

| Method | Path | Description |
|--------|------|-------------|
| GET | `/audit/` | آخرین رویدادها (scientist+) |
