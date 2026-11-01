import logging
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import admin, bookings, rooms
from app.api.errors import register_error_handlers
from app.container import Container, build_container
from app.logging_config import configure_logging
from app.metrics import OperationMetrics, outcome_for
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

    app.state.metrics = OperationMetrics()

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        started = time.perf_counter()
        request_id = uuid.uuid4().hex[:12]
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "unhandled error request_id=%s method=%s path=%s",
                request_id,
                request.method,
                request.url.path,
            )
            response = JSONResponse(
                {"error": {"code": "INTERNAL_ERROR", "message": "internal server error"}},
                status_code=500,
            )
        response.headers["X-Request-Id"] = request_id
        if request.url.path.startswith("/api"):
            elapsed_ms = (time.perf_counter() - started) * 1000
            route = request.scope.get("route")
            operation = f"{request.method} {route.path if route else request.url.path}"
            app.state.metrics.record(operation, response.status_code, elapsed_ms)
            logger.info(
                "operation=%r outcome=%s status=%s duration_ms=%.1f request_id=%s user=%s",
                operation,
                outcome_for(response.status_code),
                response.status_code,
                elapsed_ms,
                request_id,
                request.headers.get("X-User-Id", "-"),
            )
        return response

    @app.get("/metrics")
    def metrics(request: Request):
        return request.app.state.metrics.snapshot()

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
