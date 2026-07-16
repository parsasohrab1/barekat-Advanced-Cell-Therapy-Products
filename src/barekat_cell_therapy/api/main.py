"""FastAPI application."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from barekat_cell_therapy import __version__
from barekat_cell_therapy.api.routes import designs, health, patients, therapy
from barekat_cell_therapy.core.config import get_settings

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
    app.include_router(patients.router, prefix=prefix, tags=["Patients"])
    app.include_router(designs.router, prefix=prefix, tags=["CAR Designs"])
    app.include_router(therapy.router, prefix=prefix, tags=["Therapy"])

    return app


app = create_app()
