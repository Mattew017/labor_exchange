import logging

from fastapi import Request
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from tools.exceptions import (
    EntityNotFoundError,
    InactiveJobError,
    DuplicateResponseError,
    InvalidSalaryRangeError,
    PermissionDeniedError,
)

logger = logging.getLogger(__name__)


def not_found_exception_handler(request: Request, exc: EntityNotFoundError):
    logger.exception("Not Found Error: %s", exc, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc)}
    )


def inactive_job_exception_handler(request: Request, exc: InactiveJobError):
    logger.exception("Inactive Job Error: %s", exc, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"message": str(exc)}
    )


def duplicate_response_exception_handler(request: Request, exc: DuplicateResponseError):
    logger.exception("Duplicate Response: %s", exc, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"message": str(exc)}
    )


def invalid_salary_range_exception_handler(
    request: Request, exc: InvalidSalaryRangeError
):
    logger.exception("Invalid Salary Range: %s", exc, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"details": str(exc)}
    )


def input_params_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    logger.exception("Input Parameters Validation Error: %s", exc, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"details": str(exc)}),
    )


def permission_denied_exception_handler(request: Request, exc: PermissionDeniedError):
    logger.exception("Permission Denied: %s", exc, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"message": str(exc)}
    )
