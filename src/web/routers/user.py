from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies.containers import Container, get_identity_provider
from interfaces.i_identity_provider import IdentityProvider
from services.factory import ServicesFactory
from web.schemas import UserCreateSchema, UserSchema, UserUpdateSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
@inject
async def read_users(
    limit: int = 100,
    skip: int = 0,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> list[UserSchema]:
    service = services_factory.get_user_service(identity_provider=identity_provider)
    users_model = await service.get_all_users(limit, skip)

    users_schema = []
    for model in users_model:
        users_schema.append(
            UserSchema(
                id=model.id,
                name=model.name,
                email=model.email,
                is_company=model.is_company,
            )
        )
    return users_schema


@router.get("/{user_id}")
@inject
async def read_users(
    user_id: int,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> UserSchema:
    service = services_factory.get_user_service(identity_provider=identity_provider)
    user_model = await service.get_user_by_id(user_id)
    user_schema = UserSchema(
        id=user_model.id,
        name=user_model.name,
        email=user_model.email,
        is_company=user_model.is_company,
    )
    return user_schema


@router.post("")
@inject
async def create_user(
    user_create_dto: UserCreateSchema,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> UserSchema:
    service = services_factory.get_user_service(identity_provider=identity_provider)
    user = await service.create(user_create_dto)

    return UserSchema(**asdict(user))


@router.put("")
@inject
async def update_user(
    user_update_schema: UserUpdateSchema,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> UserSchema:

    service = services_factory.get_user_service(identity_provider=identity_provider)
    updated_user = await service.edit_user(user_update_schema)
    return UserSchema(**asdict(updated_user))
