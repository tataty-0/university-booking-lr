import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.domain.errors import DomainError

logger = logging.getLogger("booking.errors")


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(error_body(exc.code, exc.message), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]
        location = ".".join(str(part) for part in first["loc"] if part != "body")
        return JSONResponse(
            error_body("VALIDATION_ERROR", f"{location}: {first['msg']}"), status_code=422
        )

    @app.exception_handler(OperationalError)
    async def database_busy(_: Request, exc: OperationalError) -> JSONResponse:
        logger.error("database operational error: %s", exc.orig)
        if "locked" in str(exc.orig):
            return JSONResponse(
                error_body("DATABASE_BUSY", "the database is busy, retry later"), status_code=503
            )
        return JSONResponse(
            error_body("INTERNAL_ERROR", "internal server error"), status_code=500
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error("database error: %s", exc)
        return JSONResponse(error_body("INTERNAL_ERROR", "internal server error"), status_code=500)
