import pytest

from tools.exceptions import PermissionDeniedError
from web.schemas.response import ResponseCreateSchema


class TestResponseServiceEmployee:
    @pytest.mark.asyncio
    async def test_create_response(self, response_service_employee, test_job):
        result = await response_service_employee.create(
            job_id=test_job.id,
            response_create_dto=ResponseCreateSchema(
                message="message",
            ),
        )
        new_response = result.response
        assert new_response
        assert new_response.message == "message"

    @pytest.mark.asyncio
    async def test_get_all(self, response_service_employee, test_job):
        result = await response_service_employee.create(
            job_id=test_job.id,
            response_create_dto=ResponseCreateSchema(
                message="message",
            ),
        )
        new_response = result.response
        all_responses = await response_service_employee.get_all_active_responses(limit=100, skip=0)
        assert all_responses
        assert all_responses[0].id == new_response.id
        assert all_responses[0].message == new_response.message

    @pytest.mark.asyncio
    async def test_get_by_id(self, response_service_employee, test_job):
        with pytest.raises(PermissionDeniedError):
            await response_service_employee.get_by_job_id(job_id=test_job.id, limit=100, skip=0)


class TestResponseServiceCompany:
    @pytest.mark.asyncio
    async def test_create(self, response_service_company, test_job):
        with pytest.raises(PermissionDeniedError):
            await response_service_company.create(
                job_id=test_job.id,
                response_create_dto=ResponseCreateSchema(
                    message="message",
                ),
            )

    @pytest.mark.asyncio
    async def test_get_all(self, response_service_company, test_job):
        with pytest.raises(PermissionDeniedError):
            await response_service_company.get_all_active_responses(limit=100, skip=0)

    @pytest.mark.asyncio
    async def test_get_by_id(self, response_service_company, test_job):
        await response_service_company.get_by_job_id(job_id=test_job.id, limit=100, skip=0)
