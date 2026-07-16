.PHONY: setup infra generate-data train api worker test lint migrate

setup:
	pip install -e ".[dev]"

infra:
	docker compose up -d postgres redis minio minio-init

generate-data:
	python scripts/generate_data.py --patients 300

train:
	python scripts/train_model.py

api:
	uvicorn barekat_cell_therapy.api.main:app --reload --host 0.0.0.0 --port 8000

worker:
	celery -A barekat_cell_therapy.tasks.celery_app worker --loglevel=info

migrate:
	alembic upgrade head

test:
	pytest tests/ -v

lint:
	ruff check src tests scripts
