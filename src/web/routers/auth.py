from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies.containers import Container
from services.factory import ServicesFactory

from web.schemas import LoginSchema, TokenSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("", response_model=TokenSchema)
@inject
async def login(
    login_data: LoginSchema,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
):
    service = services_factory.get_auth_service()
    res = await service.authenticate(
        email=login_data.email, password=login_data.password
    )

    return TokenSchema(access_token=res.acces_token, token_type=res.token_type)
