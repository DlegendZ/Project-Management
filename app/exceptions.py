from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str, details=None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class UnauthorizedException(AppException):
    def __init__(self, code: str = "token_required", message: str = "Authentication required"):
        super().__init__(401, code, message)


class ForbiddenException(AppException):
    def __init__(self, code: str = "permission_denied", message: str = "Insufficient permissions"):
        super().__init__(403, code, message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, "resource_not_found", message)


class ConflictException(AppException):
    def __init__(self, code: str = "conflict", message: str = "Conflict"):
        super().__init__(409, code, message)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(400, "bad_request", message)


def error_response(code: str, message: str, details=None):
    return {"error": {"code": code, "message": message, "details": details}}


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error(f"IntegrityError: {exc}")
        msg = str(exc.orig).lower() if exc.orig else ""
        if "email" in msg:
            code, message = "duplicate_email", "Email already registered"
        elif "username" in msg:
            code, message = "duplicate_username", "Username already taken"
        elif "assignment" in msg or "task_id" in msg:
            code, message = "duplicate_assignment", "User already assigned to this task"
        else:
            code, message = "conflict", "A conflict occurred"
        return JSONResponse(
            status_code=409,
            content=error_response(code, message, None),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content=error_response("internal_error", "An unexpected error occurred", None),
        )
