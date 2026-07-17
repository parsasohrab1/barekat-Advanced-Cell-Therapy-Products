# barekat-Advanced-Cell-Therapy-Products

پلتفرم طراحی و شبیه‌سازی درمان‌های سلولی شخصی‌سازی‌شده (CAR-T) — نسخه **0.2** (فاز Trust).

## قابلیت‌ها

- ثبت پروفایل HLA و بیان آنتی‌ژن‌های توموری
- انتخاب هدف و طراحی ساختار CAR
- شبیه‌سازی پاسخ با **مدل آموزش‌دیده**، CRS، سمیت عصبی و Explainability
- روایت بالینی قابل‌فهم برای پزشک
- ارزیابی مدل (CV، Se/Sp با CI) و رجیستری نسخه
- Auth (JWT) + RBAC + Audit trail
- Prometheus metrics و داشبورد اپراتور

## راه‌اندازی سریع

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

## مثال

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

## مستندات

- [Architecture & roadmap](docs/ARCHITECTURE.md)
- [API](docs/API.md)
- [Infrastructure](docs/INFRASTRUCTURE.md)

## تکامل

| فاز | وضعیت |
|-----|--------|
| ۱ Scaffold | ✅ |
| ۲ Trust (مدل، explain، auth، audit، metrics) | ✅ |
| ۳ Clinical UX | ⏳ |
| ۴ Compliance سخت | ⏳ |
