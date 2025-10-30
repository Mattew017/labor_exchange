from dataclasses import dataclass

import pytest

from storage.sqlalchemy.tables import Job, Response, User
from tools.exceptions import EntityNotFoundError
from tools.fixtures.jobs import JobFactory
from tools.fixtures.responses import ResponseFactory
from tools.fixtures.users import UserFactory
from web.schemas.response import ResponseCreateSchema, ResponseUpdateSchema


@dataclass(frozen=True, slots=True)
class CreateTestResponseDTO:
    company: User
    job: Job
    employee: User
    response: Response


async def __create_test_response(sa_session) -> CreateTestResponseDTO:
    async with sa_session() as session:
        company = UserFactory.build(is_company=True)
        job = JobFactory.build(user_id=company.id)
        employee = UserFactory.build(is_company=False)
        response = ResponseFactory.build(job_id=job.id, user_id=employee.id)
        session.add(company)
        session.add(employee)
        session.add(job)
        session.add(response)
        session.flush()

    return CreateTestResponseDTO(
        company=company, job=job, employee=employee, response=response
    )


@pytest.mark.asyncio
async def test_get_all(response_repository, sa_session):
    test_data = await __create_test_response(sa_session)
    response = test_data.response

    all_responses = await response_repository.retrieve_many()
    assert all_responses
    assert len(all_responses) == 1

    response_from_db = all_responses[0]
    assert response_from_db.id == response.id
    assert response_from_db.message == response.message


@pytest.mark.asyncio
async def test_get_all_with_relations(response_repository, sa_session):
    test_data = await __create_test_response(sa_session)
    job = test_data.job
    employee = test_data.employee
    response = test_data.response

    all_responses = await response_repository.retrieve_many(include_relations=True)
    assert len(all_responses) == 1

    response_from_db = all_responses[0]
    assert response_from_db.id == response.id
    assert response_from_db.message == response.message

    assert response_from_db.job.id == job.id
    assert response_from_db.user.id == employee.id


@pytest.mark.asyncio
async def test_get_by_id(response_repository, sa_session):
    test_data = await __create_test_response(sa_session)
    response = test_data.response

    response_from_db = await response_repository.retrieve(id=response.id)
    assert response_from_db is not None
    assert response_from_db.id == response.id
    assert response_from_db.message == response.message


@pytest.mark.asyncio
async def test_create(response_repository, sa_session):
    test_data = await __create_test_response(sa_session)
    job = test_data.job

    # новый соискатель для отклика
    async with sa_session() as session:
        employee = UserFactory.build(is_company=False)
        session.add(employee)
        session.flush()

    dto = ResponseCreateSchema(message="otklik to vacancy")
    new_response = await response_repository.create(
        response_create_dto=dto, job_id=job.id, user_id=employee.id
    )

    assert new_response is not None
    assert new_response.message == "otklik to vacancy"


@pytest.mark.asyncio
async def test_update(response_repository, sa_session):
    test_data = await __create_test_response(sa_session)
    response = test_data.response
    response_update_dto = ResponseUpdateSchema(message="updated otklik to vacancy")

    updated_response = await response_repository.update(
        id_=response.id, response_update_dto=response_update_dto
    )

    assert response.id == updated_response.id
    assert updated_response.message == "updated otklik to vacancy"


@pytest.mark.asyncio
async def test_delete(response_repository, sa_session):
    test_data = await __create_test_response(sa_session)
    response = test_data.response

    await response_repository.delete(id_=response.id)
    with pytest.raises(EntityNotFoundError):
        await response_repository.retrieve(id=response.id)
