from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.version import __version__


def create_app() -> FastAPI:
    app = FastAPI(title="University Classroom Booking Service", version=__version__)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()
