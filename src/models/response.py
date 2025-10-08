from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.job import Job
    from models.user import User


@dataclass
class Response:
    id: int
    message: str | None = None

    job: Optional["Job"] = None
    user: Optional["User"] = None
