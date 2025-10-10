import datetime
import logging

from fastapi import HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError, JWSError
from jose.exceptions import JWTClaimsError, ExpiredSignatureError
from passlib.context import CryptContext
from starlette import status

from config import AuthSettings
from interfaces.i_identity_provider import IdentityProvider
from models import User
from repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_settings = AuthSettings()
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    return pwd_context.verify(password, hash_)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(minutes=auth_settings.access_token_expire_minutes)
        }
    )
    return jwt.encode(
        to_encode, auth_settings.secret_key, algorithm=auth_settings.algorithm
    )


def decode_access_token(token: str):
    try:
        encoded_jwt = jwt.decode(
            token, auth_settings.secret_key, algorithms=[auth_settings.algorithm]
        )
    except ExpiredSignatureError as e:
        logger.exception("Expired JWT: %s", e)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Expired token")
    except (JWTError, JWTClaimsError, JWSError) as e:
        logger.exception("JWT decoding error: %s", e)
        return None

    return encoded_jwt


http_credentials_security = HTTPBearer()


class JWTIdentityProvider(IdentityProvider):
    def __init__(self, user_repository: UserRepository, token: str | None = None):
        self.user_repository = user_repository
        self.token = token

    async def get_current_user(
        self,
    ) -> User:
        cred_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Credentials are not valid"
        )
        if not self.token:
            raise cred_exception
        payload = decode_access_token(self.token)
        if payload is None:
            raise cred_exception
        email: str = payload.get("sub")
        if email is None:
            raise cred_exception
        user = await self.user_repository.retrieve(email=email, include_relations=False)
        if user is None:
            raise cred_exception
        return user
