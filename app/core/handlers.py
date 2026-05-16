from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException, ValidationException
from app.core.logger import get_logger


logger = get_logger("app.errors")


def _build_error_response(
    error_type: str,
    message: str,
    status_code: int,
) -> dict:
    return {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
        },
    }


def _resolve_http_message(detail: object) -> str:
    if isinstance(detail, str):
        return detail
    return "Request failed"


def _resolve_validation_message(exc: RequestValidationError) -> str:
    for error in exc.errors():
        location = error.get("loc", ())
        if location and location[0] == "body":
            return "Invalid request body"
    return "Invalid request data"


def _json_error(
    error_type: str,
    message: str,
    status_code: int,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=_build_error_response(
            error_type=error_type,
            message=message,
            status_code=status_code,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        logger.warning(
            "%s %s -> %s (%s): %s",
            request.method,
            request.url.path,
            exc.error_type,
            exc.status_code,
            exc.message,
        )
        return _json_error(
            error_type=exc.error_type,
            message=exc.message,
            status_code=exc.status_code,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        message = _resolve_http_message(exc.detail)
        logger.warning(
            "%s %s -> HTTPException (%s): %s",
            request.method,
            request.url.path,
            exc.status_code,
            message,
        )
        return _json_error(
            error_type=exc.__class__.__name__,
            message=message,
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        validation_error = ValidationException(
            message=_resolve_validation_message(exc)
        )
        logger.warning(
            "%s %s -> %s (%s): %s | errors=%s",
            request.method,
            request.url.path,
            validation_error.error_type,
            validation_error.status_code,
            validation_error.message,
            exc.errors(),
        )
        return _json_error(
            error_type=validation_error.error_type,
            message=validation_error.message,
            status_code=validation_error.status_code,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "%s %s -> InternalServerError",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return _json_error(
            error_type="InternalServerError",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
