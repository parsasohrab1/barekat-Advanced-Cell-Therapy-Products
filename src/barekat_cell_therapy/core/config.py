"""تنظیمات مرکزی پلتفرم درمان سلولی."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        protected_namespaces=("settings_",),
    )

    # Application
    app_name: str = "barekat-cell-therapy"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql://barekat:barekat@localhost:5432/barekat_cell_therapy"

    # Redis & Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Object Storage
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "barekat"
    s3_secret_key: str = "barekatsecret"
    s3_bucket: str = "barekat-cell-therapy"
    s3_region: str = "us-east-1"

    # Pipeline
    pipeline_mode: Literal["simulated", "production"] = "simulated"
    pipeline_work_dir: str = "/data/processed"

    # CAR Design
    default_car_version: str = "CARv3"
    supported_targets: str = "CD19,CD20,BCMA,HER2,EGFR,PD-L1,MUC1,CEA"
    min_antigen_expression: float = 10.0

    # Simulation
    simulation_horizon_days: int = 90
    crs_risk_threshold: float = 0.7
    neurotoxicity_risk_threshold: float = 0.3

    # Privacy & Compliance
    phi_encryption_enabled: bool = False
    audit_log_enabled: bool = True

    # Auth
    secret_key: str = "barekat-cell-therapy-dev-secret-change-me"
    access_token_expire_minutes: int = 480
    auth_required: bool = False

    # ML Models
    model_path: str = "data/models"
    response_model: str = "response_predictor_v1.pkl"

    # Observability
    metrics_enabled: bool = True
    log_json: bool = False
    log_level: str = "INFO"

    @property
    def target_antigens(self) -> list[str]:
        return [t.strip() for t in self.supported_targets.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
