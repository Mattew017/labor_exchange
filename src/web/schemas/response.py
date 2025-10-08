from pydantic import BaseModel


class ResponseSchema(BaseModel):
    id: int
    job_id: int
    user_id: int
    message: str | None = None


class ResponseCreateSchema(BaseModel):
    message: str | None = None


class ResponseUpdateSchema(BaseModel):
    message: str | None = None
