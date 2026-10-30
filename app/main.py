import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import admin, bookings, rooms
from app.api.errors import register_error_handlers
from app.container import Container, build_container
from app.logging_config import configure_logging
from app.version import __version__

logger = logging.getLogger("booking.request")


def create_app(container: Container | None = None) -> FastAPI:
    configure_logging()
    app = FastAPI(title="University Classroom Booking Service", version=__version__)
    app.state.container = container or build_container()
    logger.info(
        "starting version=%s db_path=%s", __version__, app.state.container.db_path or "-"
    )
    register_error_handlers(app)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("unhandled error method=%s path=%s", request.method, request.url.path)
            return JSONResponse(
                {"error": {"code": "INTERNAL_ERROR", "message": "internal server error"}},
                status_code=500,
            )
        if request.url.path.startswith("/api"):
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "request method=%s path=%s status=%s duration_ms=%.1f user=%s",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
                request.headers.get("X-User-Id", "-"),
            )
        return response

    @app.get("/health")
    def health(request: Request):
        container = request.app.state.container
        try:
            counts = container.health.check()
        except Exception as exc:
            logger.error("health check failed db_path=%s error=%s", container.db_path, exc)
            return JSONResponse(
                {"status": "degraded", "version": __version__, "database": "unavailable"},
                status_code=503,
            )
        return {"status": "ok", "version": __version__, "database": "ok", **counts}

    app.include_router(rooms.router)
    app.include_router(bookings.router)
    app.include_router(admin.router)

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()
