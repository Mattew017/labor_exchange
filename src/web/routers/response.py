from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies.containers import Container, get_identity_provider
from interfaces.i_identity_provider import IdentityProvider
from services.factory import ServicesFactory
from web.schemas.response import ResponseSchema, ResponseCreateSchema

router = APIRouter(prefix="", tags=["responses"])


@router.get(
    "/responses",
    description="Получение списка всех откликов",
)
@inject
async def read_responses(
    limit: int = 100,
    skip: int = 0,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> list[ResponseSchema]:
    service = services_factory.get_response_service(identity_provider)
    responses_model = await service.get_all_active_responses(limit, skip)
    responses_schema = []
    for model in responses_model:
        if model.job.is_active:
            responses_schema.append(
                ResponseSchema(
                    id=model.id,
                    job_id=model.job.id,
                    user_id=model.user.id,
                    message=model.message,
                )
            )
    return responses_schema


@router.get(
    "/jobs/{job_id}/responses",
    description="Получение списка всех откликов на определённую вакансию",
)
@inject
async def read_job_responses(
    job_id: int,
    limit: int = 100,
    skip: int = 0,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> list[ResponseSchema]:
    service = services_factory.get_response_service(identity_provider)
    responses_model = await service.get_by_job_id(job_id, limit, skip)

    responses_schema = []
    for model in responses_model:
        responses_schema.append(
            ResponseSchema(
                id=model.id,
                job_id=job_id,
                user_id=model.user.id,
                message=model.message,
            )
        )

    return responses_schema


@router.post(
    "/jobs/{job_id}/responses",
    description="Отклик на вакансию",
)
@inject
async def create_response(
    job_id: int,
    response_create_dto: ResponseCreateSchema,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> ResponseSchema:
    service = services_factory.get_response_service(identity_provider)
    result = await service.create(job_id, response_create_dto)
    new_response = result.response
    user_id = result.user_id
    return ResponseSchema(
        id=new_response.id,
        message=new_response.message,
        user_id=user_id,
        job_id=job_id,
    )
