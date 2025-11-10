"""FastAPI application entry point for Data Dictionary Generator."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.middlewares import log_requests_middleware
from src.api.v1 import dictionaries, exports, search, versions
from src.core.config import settings
from src.core.database import engine
from src.core.exceptions import (
    DataDictException,
    ExportError,
    ExternalServiceError,
    NotFoundError,
    ProcessingError,
    ValidationError,
)
from src.core.logging import setup_logging
from src.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup: Initialize logging
    logger = setup_logging(
        log_level=settings.LOG_LEVEL,
        environment=settings.ENVIRONMENT,
    )
    logger.info(
        f"Starting {settings.APP_NAME} v{settings.APP_VERSION}",
        extra={"environment": settings.ENVIRONMENT},
    )

    # Create database tables (in production, use Alembic migrations instead)
    if settings.ENVIRONMENT == "development" and settings.DEBUG:
        logger.info("Creating database tables (development mode)")
        Base.metadata.create_all(bind=engine)

    yield

    # Shutdown
    logger.info("Shutting down application")
    engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated data dictionary generation from JSON files with AI-powered descriptions",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Logging Middleware
app.middleware("http")(log_requests_middleware)


# Exception Handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc: NotFoundError) -> JSONResponse:
    """Handle not found errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(ProcessingError)
async def processing_error_handler(request, exc: ProcessingError) -> JSONResponse:
    """Handle processing errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "PROCESSING_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(ExportError)
async def export_error_handler(request, exc: ExportError) -> JSONResponse:
    """Handle export errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "EXPORT_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(
    request, exc: ExternalServiceError
) -> JSONResponse:
    """Handle external service errors."""
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "EXTERNAL_SERVICE_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(DataDictException)
async def generic_error_handler(request, exc: DataDictException) -> JSONResponse:
    """Handle generic application errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


# API Routes
app.include_router(
    dictionaries.router,
    prefix="/api/v1/dictionaries",
    tags=["Dictionaries"],
)

app.include_router(
    versions.router,
    prefix="/api/v1/versions",
    tags=["Versions"],
)

app.include_router(
    exports.router,
    prefix="/api/v1/exports",
    tags=["Exports"],
)

app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["Search"],
)


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint with API information.

    Returns:
        dict: API information and available endpoints
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
