# barekat-Advanced-Cell-Therapy-Products

پلتفرم طراحی و شبیه‌سازی درمان‌های سلولی شخصی‌سازی‌شده (CAR-T) با استفاده از داده‌های ژنومی و ایمونولوژیک بیمار.

## قابلیت‌ها

- ثبت پروفایل HLA و بیان آنتی‌ژن‌های توموری
- انتخاب هدف و طراحی ساختار CAR
- شبیه‌سازی پاسخ درمانی، CRS و سمیت عصبی با Explainability
- تولید پروتکل ساخت سلول‌های مهندسی‌شده
- داده سنتتیک و مدل پیش‌بینی پاسخ

## راه‌اندازی سریع

```bash
cp .env.example .env
make setup
make infra
make migrate
make generate-data
make train
make api
```

یا با اسکریپت کامل:

```bash
bash scripts/setup.sh
```

- API Docs: http://localhost:8000/docs
- MinIO: http://localhost:9001

## مثال API

```bash
# ثبت بیمار
curl -X POST http://localhost:8000/api/v1/patients/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "CT_0001",
    "hla_profile": [{"allele": "HLA-A*02:01", "copies": 1}],
    "antigen_expression": [
      {"antigen": "CD19", "expression_pct": 78.5},
      {"antigen": "BCMA", "expression_pct": 12.0}
    ]
  }'

# طرح کامل درمان
curl -X POST http://localhost:8000/api/v1/therapy/plan \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "CT_0001", "dose_cells": 1e8}'
```

## ساختار

```
├── docker-compose.yml       # PostgreSQL, Redis, MinIO, API, Worker
├── src/barekat_cell_therapy/
│   ├── api/                 # FastAPI
│   ├── pipeline/            # target → design → simulate → protocol
│   ├── data/                # داده سنتتیک
│   ├── ml/                  # مدل پاسخ
│   └── tasks/               # Celery
├── scripts/
├── tests/
└── docs/INFRASTRUCTURE.md
```

مستندات زیرساخت: [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md)

## محدودیت‌های کلیدی

دقت مدل‌های پیش‌بینی، یکپارچه‌سازی مولتی‌امیکس، حریم خصوصی داده‌های بیمار، و Explainability برای پزشکان.
