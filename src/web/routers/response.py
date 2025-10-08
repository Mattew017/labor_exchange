from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies import get_current_user, is_company, is_employee
from dependencies.containers import RepositoriesContainer
from models import User
from repositories.job_repository import JobRepository
from repositories.response_repository import ResponseRepository
from tools.exceptions import InactiveJobError, DuplicateResponseError
from web.schemas.response import ResponseSchema, ResponseCreateSchema

router = APIRouter(prefix="", tags=["responses"])


@router.get(
    "/responses",
    description="Получение списка всех откликов",
    dependencies=[Depends(is_employee)],
)
@inject
async def read_responses(
    limit: int = 100,
    skip: int = 0,
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> list[ResponseSchema]:
    responses_model = await response_repository.retrieve_many(
        limit,
        skip,
        include_relations=True,
    )

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
    dependencies=[Depends(is_company)],
)
@inject
async def read_job_responses(
    job_id: int,
    limit: int = 100,
    skip: int = 0,
    job_repository: JobRepository = Depends(
        Provide[RepositoriesContainer.job_repository]
    ),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> list[ResponseSchema]:
    job_model = await job_repository.retrieve(id=job_id)
    responses_model = await response_repository.retrieve_many(
        limit,
        skip,
        include_relations=True,
        job_id=job_id,
    )
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
    dependencies=[Depends(is_employee)],
)
@inject
async def create_response(
    job_id: int,
    response_create_dto: ResponseCreateSchema,
    job_repository: JobRepository = Depends(
        Provide[RepositoriesContainer.job_repository]
    ),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    job_model = await job_repository.retrieve(id=job_id)
    if not job_model.is_active:
        raise InactiveJobError()

    response_model = await response_repository.retrieve_many(
        limit=1, skip=0, job_id=job_id, user_id=current_user.id
    )
    if len(response_model) > 0:
        raise DuplicateResponseError()

    new_response = await response_repository.create(
        response_create_dto, job_id=job_id, user_id=current_user.id
    )
    return ResponseSchema(
        id=new_response.id,
        message=new_response.message,
        user_id=current_user.id,
        job_id=job_id,
    )
