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
| PostgreSQL | 5432 | Patients, CAR designs, simulations |
| Redis | 6379 | Celery queue and cache |
| MinIO | 9000/9001 | Profiles, designs, protocols |
| API | 8000 | Cell therapy REST API |
| Worker | — | Data generation, model training, batch simulation |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Service health check |
| POST | `/api/v1/patients/` | Register patient profile |
| GET | `/api/v1/patients/{id}` | Patient details |
| POST | `/api/v1/designs/` | CAR design |
| GET | `/api/v1/designs/{id}` | Design details |
| POST | `/api/v1/simulations/` | Response and safety simulation |
| POST | `/api/v1/protocols/` | Generate cell manufacturing protocol |
| POST | `/api/v1/therapy/plan` | Full plan: design + simulate + protocol |
| POST | `/api/v1/simulations/batch` | Batch simulation |

## Pipeline

```
Patient Profile → Target Selection → CAR Design → Response Simulation → Production Protocol
```

| Stage | Module | Description |
|-------|--------|-------------|
| Target Selection | `pipeline/target_selection.py` | Select the best tumor antigen |
| CAR Design | `pipeline/car_design.py` | Chimeric receptor structure |
| Simulation | `pipeline/simulation.py` | Response, CRS, neurotoxicity prediction |
| Protocol | `pipeline/protocol.py` | Cell manufacturing instructions |

## Project Structure

```
├── docker-compose.yml
├── Dockerfile
├── src/barekat_cell_therapy/
│   ├── api/                 # FastAPI endpoints
│   ├── core/                # settings, DB, storage
│   ├── data/                # synthetic data generation
│   ├── ml/                  # response prediction model
│   ├── models/              # ORM
│   ├── pipeline/            # target → design → simulate → protocol
│   ├── schemas/             # Pydantic
│   ├── services/            # domain logic
│   └── tasks/               # Celery
├── scripts/
├── data/
├── tests/
└── alembic/
```

## Makefile Commands

```bash
make setup          # install dependencies
make infra          # start Docker
make generate-data  # generate synthetic data
make train          # train the model
make evaluate       # evaluate the model
make api            # run the API
make worker         # Celery worker
make migrate        # database migration
make test           # run tests
```

## Maturity (v0.2)

The trained model in inference, explainability, evaluation, JWT/audit, `/metrics` and the `/dashboard/` dashboard are active.
Details: [ARCHITECTURE.md](ARCHITECTURE.md) and [API.md](API.md).
