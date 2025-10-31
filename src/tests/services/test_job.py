from decimal import Decimal

import pytest

from tools.exceptions import InvalidSalaryRangeError
from web.schemas.job import JobCreateSchema, JobUpdateSchema


def get_create_job_dto():
    dto = JobCreateSchema(
        title="some title",
        description="description",
        salary_from=Decimal("22400"),
        salary_to=Decimal("22400"),
        is_active=True,
    )
    return dto


class TestJobService:
    @pytest.mark.asyncio
    async def test_create_job(self, job_service):
        dto = get_create_job_dto()
        new_job = await job_service.create(dto)

        assert new_job
        assert new_job.title == "some title"
        assert new_job.description == "description"
        assert new_job.salary_from == Decimal("22400")
        assert new_job.salary_to == Decimal("22400")
        assert new_job.is_active is True

    @pytest.mark.asyncio
    async def test_create_job_invalid_salary(self, job_service):
        with pytest.raises(InvalidSalaryRangeError):
            dto = JobCreateSchema(
                title="some title",
                description="description",
                salary_from=Decimal("100000"),
                salary_to=Decimal("50000"),
                is_active=True,
            )
            await job_service.create(dto)

    @pytest.mark.asyncio
    async def test_get_all(self, job_service):
        dto = get_create_job_dto()
        await job_service.create(dto)

        all_jobs = await job_service.get_all_jobs(limit=100, skip=0)

        assert all_jobs
        assert all_jobs[0].title == dto.title
        assert all_jobs[0].description == dto.description
        assert all_jobs[0].salary_from == dto.salary_from
        assert all_jobs[0].salary_to == dto.salary_from
        assert all_jobs[0].is_active == dto.is_active

    @pytest.mark.asyncio
    async def test_get_by_id(self, job_service):
        dto = get_create_job_dto()
        new_job = await job_service.create(dto)

        job = await job_service.get_by_id(job_id=new_job.id)
        assert job
        assert job.title == dto.title
        assert job.description == dto.description
        assert job.salary_from == dto.salary_from
        assert job.salary_to == dto.salary_to
        assert job.is_active == dto.is_active

    @pytest.mark.asyncio
    async def test_update(self, job_service):
        dto = get_create_job_dto()
        new_job = await job_service.create(dto)

        update_dto = JobUpdateSchema(
            title="updated title",
            description="updated description",
            salary_from=Decimal("100000"),
            salary_to=Decimal("100000"),
            is_active=False,
        )
        updated = await job_service.update(new_job.id, update_dto)
        assert updated.title == update_dto.title
        assert updated.description == update_dto.description
        assert updated.salary_from == update_dto.salary_from
        assert updated.salary_to == update_dto.salary_to
        assert updated.is_active == update_dto.is_active
