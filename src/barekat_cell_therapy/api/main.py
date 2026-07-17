"""FastAPI application — maturity phase 2."""

from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from barekat_cell_therapy import __version__
from barekat_cell_therapy.api.routes import audit, auth, designs, health, ml, patients, therapy
from barekat_cell_therapy.core.config import get_settings
from barekat_cell_therapy.core.metrics import metrics_payload

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("starting_app", env=settings.app_env, version=__version__)
    yield
    logger.info("shutting_down_app")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="barekat-Advanced-Cell-Therapy-Products",
        description="پلتفرم طراحی و شبیه‌سازی درمان‌های سلولی شخصی‌سازی‌شده (CAR-T)",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = settings.api_prefix
    app.include_router(health.router, prefix=prefix, tags=["Health"])
    app.include_router(auth.router, prefix=prefix, tags=["Auth"])
    app.include_router(patients.router, prefix=prefix, tags=["Patients"])
    app.include_router(designs.router, prefix=prefix, tags=["CAR Designs"])
    app.include_router(therapy.router, prefix=prefix, tags=["Therapy"])
    app.include_router(ml.router, prefix=prefix, tags=["ML"])
    app.include_router(audit.router, prefix=prefix, tags=["Audit"])

    if settings.metrics_enabled:

        @app.get("/metrics", include_in_schema=False)
        def prometheus_metrics() -> Response:
            payload, content_type = metrics_payload()
            return Response(content=payload, media_type=content_type)

    static_dir = Path(__file__).resolve().parents[3] / "static"
    if static_dir.exists():
        app.mount("/dashboard", StaticFiles(directory=str(static_dir), html=True), name="dashboard")

    return app


app = create_app()
