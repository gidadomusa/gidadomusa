"""
API package initializer — creates and configures the FastAPI app instance.

Drop this into backend/app/api/__init__.py.

Expect to add router modules under backend/app/api/routers/, e.g.:
- backend/app/api/routers/health.py
- backend/app/api/routers/users.py
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List

# Configure module-level logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.api")


def create_app(
    title: str = "My API",
    version: str = "0.1.0",
    allowed_origins: List[str] = None,
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
        from .routers import health, users  # create these modules as needed
        app.include_router(health.router, prefix="/api/health", tags=["health"])
        app.include_router(users.router, prefix="/api/users", tags=["users"])
    except Exception:
        # If routers are not present yet, log and continue — makes gradual migration easier.
        logger.debug("Routers not yet configured: %s", exc_info=True)

    # Generic exception handler (keep specific handlers for known exceptions)
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

    @app.on_event("shutdown")
    async def _shutdown_event():
        logger.info("API shutdown: cleaning up resources")
        # Close DB connections, stop background tasks, etc. here.

    return app


# Expose the app instance for ASGI servers (uvicorn/gunicorn)
app = create_app()

# Optional: make the factory available for tests to import create_app
__all__ = ["app", "create_app"]
