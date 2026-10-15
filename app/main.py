from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import rooms
from app.api.errors import register_error_handlers
from app.container import Container, build_container
from app.version import __version__


def create_app(container: Container | None = None) -> FastAPI:
    app = FastAPI(title="University Classroom Booking Service", version=__version__)
    app.state.container = container or build_container()
    register_error_handlers(app)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    app.include_router(rooms.router)

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()
