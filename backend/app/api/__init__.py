"""
API package initializer — creates and configures the FastAPI app instance.

Drop this into backend/app/api/__init__.py.

Expect to add router modules under backend/app/api/routers/, e.g.:
- backend/app/api/routers/health.py
- backend/app/api/routers/users.py
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List, Optional

# Import DB init
from backend.app.db import init_db

# Configure module-level logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.api")


def create_app(
    title: str = "My API",
    version: str = "0.1.0",
    allowed_origins: Optional[List[str]] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.
    - Use an app factory so tests can create isolated instances.
    - Configure CORS, exception handlers, routers, and lifecycle events here.
    """
    if allowed_origins is None:
        # For development, you might use ["*"]; tighten this for production.
        allowed_origins = ["*"]

    app = FastAPI(
        title=title,
        version=version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Example: include routers (create these modules under backend/app/api/routers/)
    try:
        # Import here to avoid circular imports on package import
        # ImportError means the routers module/file doesn't exist yet — that's fine.
        from .routers import health, users, auth, models  # create these modules as needed
        app.include_router(health.router, prefix="/api/health", tags=["health"])
        app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
        app.include_router(users.router, prefix="/api/users", tags=["users"])
        app.include_router(models.router, prefix="/api/models", tags=["models"])
    except ImportError:
        # Routers not present yet (development). Log at debug with stacktrace.
        logger.debug("Routers not yet configured", exc_info=True)
    except Exception:
        # Something unexpected happened while importing or including routers — log as error.
        logger.exception("Failed to include routers")

    # HTTPException handler (preserve status_code/detail)
    @app.exception_handler(HTTPException)
    async def _http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # Generic exception handler (fallback)
    @app.exception_handler(Exception)
    async def _internal_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception for request %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )

    # Startup / shutdown events
    @app.on_event("startup")
    async def _startup_event():
        logger.info("API startup: initializing resources (DB/clients/etc.)")
        # Initialize DB connections, caches, background tasks, etc. here.
        # Create DB tables if they don't exist
        try:
            init_db()
        except Exception:
            logger.exception("Failed to initialize DB")

    @app.on_event("shutdown")
    async def _shutdown_event():
        logger.info("API shutdown: cleaning up resources")
        # Close DB connections, stop background tasks, etc. here.

    return app


# Expose the app instance for ASGI servers (uvicorn/gunicorn)
app = create_app()

# Optional: make the factory available for tests to import create_app
__all__ = ["app", "create_app"]
