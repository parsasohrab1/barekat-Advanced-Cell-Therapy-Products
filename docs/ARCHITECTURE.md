# Architecture — barekat Advanced Cell Therapy Products

## Overview

پلتفرم طراحی و شبیه‌سازی درمان سلولی شخصی‌سازی‌شده (CAR-T):

```
Patient Omics → Target Selection → CAR Design → ML Simulation → Protocol → Clinician Narrative
```

## Components

| Layer | Tech | Role |
|-------|------|------|
| API | FastAPI | REST برای بیمار، طرح، شبیه‌سازی، ML، Auth |
| Worker | Celery + Redis | batch simulation، train، generate |
| DB | PostgreSQL | patients, designs, simulations, users, audit |
| Object store | MinIO | پروفایل‌ها، طرح‌ها، نتایج |
| ML | scikit-learn RF | پیش‌بینی پاسخ + feature importance |

## Domain Model

- **Patient**: HLA + بیان آنتی‌ژن توموری
- **CarDesign**: ساختار گیرنده (scFv, costim, CD3ζ)
- **Simulation**: احتمال پاسخ، CRS، سمیت عصبی، explainability
- **ProductionProtocol**: دستورالعمل تولید سلول
- **User / AuditLog**: هویت و ردیابی عملیات

## Inference

1. اگر `data/models/response_predictor_v1.pkl` موجود باشد → inference با مدل + explainability واقعی
2. در غیر این صورت → heuristic با برچسب `inference_source=heuristic`

## نقشه راه تکامل

| فاز | وضعیت | محتوا |
|-----|--------|--------|
| ۱ — Scaffold | ✅ | Docker، API، pipeline، داده سنتتیک |
| ۲ — Trust | ✅ | مدل در serve، explainability، eval، auth، audit، metrics، dashboard |
| ۳ — Clinical UX | ⏳ | UI غنی‌تر، PDF پروتکل، HITL |
| ۴ — Compliance | ⏳ | PHI encryption، GDPR delete، Part 11 سخت‌گیرانه‌تر |
| ۵ — Platform | ⏳ | MLflow، K8s، drift monitoring |

## وضعیت فعلی (پیوست)

| قابلیت | وضعیت |
|--------|--------|
| ثبت بیمار / طراحی CAR / شبیه‌سازی / پروتکل | ✅ |
| مدل آموزش‌دیده در inference | ✅ |
| Explainability + روایت بالینی | ✅ |
| Evaluation + model registry | ✅ |
| JWT Auth + RBAC + Audit | ✅ |
| Prometheus `/metrics` | ✅ |
| Dashboard اپراتور | ✅ (minimal) |
| Frontend React کامل | ❌ |
| MLflow / K8s | ❌ |
