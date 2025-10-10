from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies.containers import Container, get_identity_provider
from interfaces.i_identity_provider import IdentityProvider
from services.factory import ServicesFactory
from web.schemas.job import JobSchema, JobCreateSchema, JobUpdateSchema

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", description="Получение списка всех вакансий")
@inject
async def read_jobs(
    limit: int = 100,
    skip: int = 0,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> list[JobSchema]:
    service = services_factory.get_job_service(identity_provider)
    jobs_model = await service.get_all_jobs(limit=limit, skip=skip)

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
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> JobSchema:
    service = services_factory.get_job_service(identity_provider)
    job_model = await service.get_by_id(job_id)

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


@router.post("", description="Создание новой вакансии")
@inject
async def create_job(
    job_create_dto: JobCreateSchema,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> JobSchema:
    service = services_factory.get_job_service(identity_provider)
    job = await service.create(job_create_dto)
    return JobSchema(
        id=job.id,
        user_id=job.user_id,
        title=job.title,
        description=job.description,
        salary_from=job.salary_from,
        salary_to=job.salary_to,
        is_active=job.is_active,
    )


@router.patch(
    "/{job_id}",
    description="Редактирование вакансии",
)
@inject
async def update_job(
    job_id: int,
    job_update_schema: JobUpdateSchema,
    services_factory: ServicesFactory = Depends(Provide[Container.services_factory]),
    identity_provider: IdentityProvider = Depends(get_identity_provider),
) -> JobSchema:
    service = services_factory.get_job_service(identity_provider)
    updated_job = await service.update(job_id, job_update_schema)
    return JobSchema(
        id=updated_job.id,
        user_id=updated_job.user_id,
        title=updated_job.title,
        description=updated_job.description,
        salary_from=updated_job.salary_from,
        salary_to=updated_job.salary_to,
        is_active=updated_job.is_active,
    )
