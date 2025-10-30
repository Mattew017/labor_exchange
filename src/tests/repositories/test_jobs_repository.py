from decimal import Decimal

import pytest

from tools.exceptions import EntityNotFoundError
from tools.fixtures.jobs import JobFactory
from tools.fixtures.responses import ResponseFactory
from tools.fixtures.users import UserFactory
from web.schemas.job import JobCreateSchema, JobUpdateSchema


async def __create_test_job(sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        job = JobFactory.build(user_id=user.id)
        session.add(user)
        session.add(job)
        session.flush()

    return user, job


@pytest.mark.asyncio
async def test_get_all(job_repository, sa_session):
    user, job = await __create_test_job(sa_session)

    all_jobs = await job_repository.retrieve_many()
    assert all_jobs
    assert len(all_jobs) == 1

    job_from_repo = all_jobs[0]
    assert job_from_repo.id == job.id
    assert job_from_repo.user_id == job.user_id
    assert job_from_repo.title == job.title
    assert job_from_repo.description == job.description
    assert job_from_repo.salary_from == job.salary_from
    assert job_from_repo.salary_to == job.salary_to


@pytest.mark.asyncio
async def test_get_all_with_relations(job_repository, sa_session):
    async with sa_session() as session:
        company = UserFactory.build(is_company=True)
        employee = UserFactory.build(is_company=False)
        job = JobFactory.build(user_id=company.id)
        response = ResponseFactory.build(job_id=job.id, user_id=employee.id)
        session.add(company)
        session.add(employee)
        session.add(job)
        session.add(response)
        session.flush()

    all_jobs = await job_repository.retrieve_many(include_relations=True)
    assert len(all_jobs) == 1

    job_from_repo = all_jobs[0]
    assert len(job_from_repo.responses) == 1
    assert job_from_repo.user
    assert job_from_repo.responses[0].id == response.id
    assert job_from_repo.title == job.title
    assert job_from_repo.description == job.description
    assert job_from_repo.salary_from == job.salary_from
    assert job_from_repo.salary_to == job.salary_to


@pytest.mark.asyncio
async def test_get_by_id(job_repository, sa_session):
    user, job = await __create_test_job(sa_session)

    job = await job_repository.retrieve(id=job.id)
    assert job is not None
    assert job.id == job.id


@pytest.mark.asyncio
async def test_create(job_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        session.add(user)
        session.flush()

    dto = JobCreateSchema(
        title="some title",
        description="description",
        salary_from=Decimal("22400"),
        salary_to=Decimal("22400"),
        is_active=True,
    )

    new_job = await job_repository.create(job_create_dto=dto, user_id=user.id)

    assert new_job is not None
    assert new_job.title == "some title"
    assert new_job.description == "description"


@pytest.mark.asyncio
async def test_update(job_repository, sa_session):
    _, job = await __create_test_job(sa_session)

    job_update_dto = JobUpdateSchema(
        title="new title!",
        description="description",
        salary_from=Decimal("22400"),
        salary_to=Decimal("22400"),
        is_active=True,
    )
    updated_job = await job_repository.update(id_=job.id, job_update_dto=job_update_dto)
    assert job.id == updated_job.id
    assert updated_job.title == "new title!"


@pytest.mark.asyncio
async def test_delete(job_repository, sa_session):
    _, job = await __create_test_job(sa_session)

    await job_repository.delete(id_=job.id)
    with pytest.raises(EntityNotFoundError):
        await job_repository.retrieve(id=job.id)
