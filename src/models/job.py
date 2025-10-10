from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models import User
    from models import Response


@dataclass
class Job:
    id: int
    user_id: int
    title: str
    description: str
    salary_from: Decimal
    salary_to: Decimal
    is_active: bool

    user: Optional["User"] = None
    responses: list["Response"] = field(default_factory=list)
