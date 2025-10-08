import logging

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from tools.exceptions import (
    EntityNotFoundError,
    InactiveJobError,
    DuplicateResponseError,
    InvalidSalaryRangeError,
)

logger = logging.getLogger(__name__)


def not_found_exception_handler(request: Request, exc: EntityNotFoundError):
    logger.exception("Not Found Error: %s", exc, exc_info=exc)
    return JSONResponse(status_code=404, content={"message": str(exc)})


def inactive_job_exception_handler(request: Request, exc: InactiveJobError):
    logger.exception("Inactive Job Error: %s", exc, exc_info=exc)
    return JSONResponse(status_code=409, content={"message": str(exc)})


def duplicate_response_exception_handler(request: Request, exc: DuplicateResponseError):
    logger.exception("Duplicate Response: %s", exc, exc_info=exc)
    return JSONResponse(status_code=409, content={"message": str(exc)})


def invalid_salary_range_exception_handler(
    request: Request, exc: InvalidSalaryRangeError
):
    logger.exception("Invalid Salary Range: %s", exc, exc_info=exc)
    return JSONResponse(status_code=422, content={"details": str(exc)})


def input_params_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    logger.exception("Input Parameters Validation Error: %s", exc, exc_info=exc)
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"details": str(exc)}),
    )
