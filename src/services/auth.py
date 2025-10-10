from dataclasses import dataclass

from fastapi import HTTPException, status

from interfaces.i_service import ServiceInterface
from repositories.user_repository import UserRepository
from services.identity_provider import verify_password, create_access_token


@dataclass(frozen=True, slots=True)
class AuthenticateUserOutputDTO:
    acces_token: str
    token_type: str


class AuthService(ServiceInterface):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate(
        self, email: str, password: str
    ) -> AuthenticateUserOutputDTO:

        user = await self.user_repository.retrieve(email=email, include_relations=False)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        access_token = create_access_token(data={"sub": user.email})
        return AuthenticateUserOutputDTO(acces_token=access_token, token_type="bearer")
