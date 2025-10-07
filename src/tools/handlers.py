import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from tools.exceptions import EntityNotFoundError

logger = logging.getLogger(__name__)


def not_found_exception_handler(request: Request, exc: EntityNotFoundError):
    logger.exception("Not Found Error: %s", exc, exc_info=exc)
    return JSONResponse(status_code=404, content={"message": str(exc)})
