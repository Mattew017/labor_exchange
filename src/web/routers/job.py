from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_current_user, is_company
from dependencies.containers import RepositoriesContainer
from models import User
from repositories.job_repository import JobRepository
from web.schemas.job import JobSchema, JobCreateSchema, JobUpdateSchema

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", description="Получение списка всех вакансий")
@inject
async def read_jobs(
    limit: int = 100,
    skip: int = 0,
    job_repository: JobRepository = Depends(
        Provide[RepositoriesContainer.job_repository]
    ),
) -> list[JobSchema]:
    jobs_model = await job_repository.retrieve_many(limit, skip)

    jobs_schema = []
    for model in jobs_model:
        jobs_schema.append(
            JobSchema(
                id=model.id,
                user_id=model.user_id,
                title=model.title,
                description=model.description,
                salary_from=model.salary_from,
                salary_to=model.salary_to,
                is_active=model.is_active,
            )
        )
    return jobs_schema


@router.get("/{job_id}", description="Получение информации о вакансии по id")
@inject
async def read_job(
    job_id: int,
    job_repository: JobRepository = Depends(
        Provide[RepositoriesContainer.job_repository]
    ),
) -> JobSchema:
    job_model = await job_repository.retrieve(id=job_id)

    job_schema = JobSchema(
        id=job_model.id,
        user_id=job_model.user_id,
        title=job_model.title,
        description=job_model.description,
        salary_from=job_model.salary_from,
        salary_to=job_model.salary_to,
        is_active=job_model.is_active,
    )
    return job_schema


@router.post(
    "", description="Создание новой вакансии", dependencies=[Depends(is_company)]
)
@inject
async def create_job(
    job_create_dto: JobCreateSchema,
    job_repository: JobRepository = Depends(
        Provide[RepositoriesContainer.job_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> JobSchema:
    job = await job_repository.create(
        job_create_dto=job_create_dto, user_id=current_user.id
    )
    return JobSchema(
        id=job.id,
        user_id=current_user.id,
        title=job.title,
        description=job.description,
        salary_from=job.salary_from,
        salary_to=job.salary_to,
        is_active=job.is_active,
    )


@router.patch(
    "/{job_id}",
    description="Редактирование вакансии",
    dependencies=[Depends(is_company)],
)
@inject
async def update_job(
    job_id: int,
    job_update_schema: JobUpdateSchema,
    job_repository: JobRepository = Depends(
        Provide[RepositoriesContainer.job_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> JobSchema:
    existing_job = await job_repository.retrieve(id=job_id)
    if existing_job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав"
        )
    new_salary_from = job_update_schema.salary_from or existing_job.salary_from
    new_salary_to = job_update_schema.salary_to or existing_job.salary_to
    if (
        new_salary_from is not None
        and new_salary_to is not None
        and new_salary_from > new_salary_to
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{new_salary_from=} cannot be greater than {new_salary_to=}",
        )
    try:
        updated_job = await job_repository.update(existing_job.id, job_update_schema)
        return JobSchema(
            id=updated_job.id,
            user_id=current_user.id,
            title=updated_job.title,
            description=updated_job.description,
            salary_from=updated_job.salary_from,
            salary_to=updated_job.salary_to,
            is_active=updated_job.is_active,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Вакансия не найдена"
        )
