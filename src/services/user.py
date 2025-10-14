from interfaces.i_identity_provider import IdentityProvider
from interfaces.i_service import ServiceInterface
from models import User
from repositories import UserRepository
from services.identity_provider import hash_password
from tools.exceptions import PermissionDeniedError
from web.schemas import UserUpdateSchema, UserCreateSchema


class UserService(ServiceInterface):
    def __init__(
        self, user_repository: UserRepository, identity_provider: IdentityProvider
    ):
        self.user_repository = user_repository
        self.identity_provider = identity_provider

    async def edit_user(self, user_update_schema: UserUpdateSchema) -> User:
        current_user = await self.identity_provider.get_current_user()
        existing_user = await self.user_repository.retrieve(
            email=user_update_schema.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise PermissionDeniedError("Недостаточно прав на это действие")

        updated_user = await self.user_repository.update(
            current_user.id, user_update_schema
        )
        return updated_user

    async def get_all_users(self, limit: int, skip: int) -> list[User]:
        users = await self.user_repository.retrieve_many(limit=limit, skip=skip)
        return users

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.user_repository.retrieve(id=user_id)
        return user

    async def create(self, user_create_dto: UserCreateSchema) -> User:
        hashed_password = hash_password(user_create_dto.password)
        user = await self.user_repository.create(user_create_dto, hashed_password)
        return user
