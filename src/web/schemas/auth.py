from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8)]
