from interfaces.i_identity_provider import IdentityProvider
from interfaces.i_service import ServiceInterface
from models import Job
from repositories import JobRepository
from tools.exceptions import PermissionDeniedError, InvalidSalaryRangeError
from web.schemas.job import JobCreateSchema, JobUpdateSchema


class JobService(ServiceInterface):
    def __init__(
        self, job_repository: JobRepository, identity_provider: IdentityProvider
    ):
        self.job_repository = job_repository
        self.identity_provider = identity_provider

    async def get_all_jobs(self, limit: int, skip: int) -> list[Job]:
        jobs = await self.job_repository.retrieve_many(limit=limit, skip=skip)
        return jobs

    async def get_by_id(self, job_id: int) -> Job:
        job = await self.job_repository.retrieve(id=job_id)
        return job

    async def create(self, job_create_dto: JobCreateSchema) -> Job:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.is_company:
            raise PermissionDeniedError("Недостаточно прав на создание вакансии")
        job = await self.job_repository.create(
            job_create_dto=job_create_dto, user_id=current_user.id
        )
        return job

    async def update(self, job_id: int, job_update_schema: JobUpdateSchema) -> Job:
        existing_job = await self.job_repository.retrieve(id=job_id)
        current_user = await self.identity_provider.get_current_user()
        if existing_job.user_id != current_user.id:
            raise PermissionDeniedError("Недостаточно прав на изменение вакансии")
        new_salary_from = job_update_schema.salary_from or existing_job.salary_from
        new_salary_to = job_update_schema.salary_to or existing_job.salary_to
        if (
            new_salary_from is not None
            and new_salary_to is not None
            and new_salary_from > new_salary_to
        ):
            raise InvalidSalaryRangeError(
                salary_from=new_salary_from, salary_to=new_salary_to
            )

        updated_job = await self.job_repository.update(
            existing_job.id, job_update_schema
        )
        return updated_job
