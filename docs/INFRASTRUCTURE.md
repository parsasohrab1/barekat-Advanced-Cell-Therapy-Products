# Infrastructure

## Architecture

```
┌──────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Patient Omics   │────▶│  FastAPI     │────▶│  PostgreSQL     │
│  HLA / Antigens  │     │  REST API    │     │  (Patients)     │
└──────────────────┘     └──────┬───────┘     └─────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
             ┌──────────┐  ┌──────────┐  ┌─────────────┐
             │  Celery  │  │  MinIO   │  │  ML Model   │
             │  Worker  │  │  (S3)    │  │  (sklearn)  │
             └──────────┘  └──────────┘  └─────────────┘
                    │
                    ▼
   Pipeline: Target Selection → CAR Design → Simulation → Protocol
```

## Quick Start

```bash
cp .env.example .env
docker compose up -d postgres redis minio minio-init
pip install -e ".[dev]"
alembic upgrade head
python scripts/generate_data.py --patients 300
python scripts/train_model.py
uvicorn barekat_cell_therapy.api.main:app --reload
```

- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## Services

| Service | Port | Role |
|---------|------|------|
| PostgreSQL | 5432 | بیماران، طرح‌های CAR، شبیه‌سازی‌ها |
| Redis | 6379 | صف Celery و کش |
| MinIO | 9000/9001 | پروفایل‌ها، طرح‌ها، پروتکل‌ها |
| API | 8000 | REST API درمان سلولی |
| Worker | — | تولید داده، آموزش مدل، batch simulation |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | بررسی سلامت سرویس‌ها |
| POST | `/api/v1/patients/` | ثبت پروفایل بیمار |
| GET | `/api/v1/patients/{id}` | جزئیات بیمار |
| POST | `/api/v1/designs/` | طراحی CAR |
| GET | `/api/v1/designs/{id}` | جزئیات طرح |
| POST | `/api/v1/simulations/` | شبیه‌سازی پاسخ و ایمنی |
| POST | `/api/v1/protocols/` | تولید پروتکل ساخت سلول |
| POST | `/api/v1/therapy/plan` | طرح کامل: design + simulate + protocol |
| POST | `/api/v1/simulations/batch` | شبیه‌سازی دسته‌ای |

## Pipeline

```
Patient Profile → Target Selection → CAR Design → Response Simulation → Production Protocol
```

| Stage | Module | Description |
|-------|--------|-------------|
| Target Selection | `pipeline/target_selection.py` | انتخاب بهترین آنتی‌ژن توموری |
| CAR Design | `pipeline/car_design.py` | ساختار گیرنده کایمریک |
| Simulation | `pipeline/simulation.py` | پیش‌بینی پاسخ، CRS، سمیت عصبی |
| Protocol | `pipeline/protocol.py` | دستورالعمل تولید سلول |

## Project Structure

```
├── docker-compose.yml
├── Dockerfile
├── src/barekat_cell_therapy/
│   ├── api/                 # FastAPI endpoints
│   ├── core/                # تنظیمات، DB، storage
│   ├── data/                # تولید داده سنتتیک
│   ├── ml/                  # مدل پیش‌بینی پاسخ
│   ├── models/              # ORM
│   ├── pipeline/            # target → design → simulate → protocol
│   ├── schemas/             # Pydantic
│   ├── services/            # منطق دامنه
│   └── tasks/               # Celery
├── scripts/
├── data/
├── tests/
└── alembic/
```

## Makefile Commands

```bash
make setup          # نصب وابستگی‌ها
make infra          # راه‌اندازی Docker
make generate-data  # تولید داده سنتتیک
make train          # آموزش مدل
make evaluate       # ارزیابی مدل
make api            # اجرای API
make worker         # Celery worker
make migrate        # مهاجرت پایگاه داده
make test           # اجرای تست‌ها
```

## Maturity (v0.2)

مدل آموزش‌دیده در inference، explainability، ارزیابی، JWT/audit، `/metrics` و داشبورد `/dashboard/` فعال است.
جزئیات: [ARCHITECTURE.md](ARCHITECTURE.md) و [API.md](API.md).
