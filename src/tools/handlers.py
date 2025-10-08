import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from tools.exceptions import (
    EntityNotFoundError,
    InactiveJobError,
    DuplicateResponseError,
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
