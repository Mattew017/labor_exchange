from decimal import Decimal
from typing import Any

from pydantic import BaseModel, model_validator, Field

from tools.exceptions import InvalidSalaryRangeError


class JobSchema(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    salary_from: Decimal
    salary_to: Decimal
    is_active: bool


class JobCreateSchema(BaseModel):
    title: str = Field(min_length=10, max_length=100)
    description: str = Field(min_length=10, max_length=5000)
    salary_from: Decimal | None = Field(default=None, ge=22400)
    salary_to: Decimal | None = Field(default=None, ge=22400)
    is_active: bool

    @model_validator(mode="before")
    @classmethod
    def validate_salary_range(cls, data: dict[str, Any]) -> dict[str, Any]:
        salary_from = data.get("salary_from")
        salary_to = data.get("salary_to")

        if (
            salary_from is not None
            and salary_to is not None
            and salary_from > salary_to
        ):
            raise InvalidSalaryRangeError(salary_from, salary_to)

        return data


class JobUpdateSchema(JobCreateSchema):
    title: str | None = Field(default=None, min_length=10, max_length=100)
    description: str | None = Field(default=None, min_length=10, max_length=5000)
    salary_from: Decimal | None = Field(default=None, ge=22400)
    salary_to: Decimal | None = Field(default=None, ge=22400)
    is_active: bool | None = None
