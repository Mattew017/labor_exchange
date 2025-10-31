import pytest_asyncio

from interfaces.i_identity_provider import IdentityProvider
from models import User
from services.factory import ServicesFactory
from tools.fixtures.jobs import JobFactory
from tools.fixtures.users import UserFactory


class MockIDP(IdentityProvider):
    def __init__(self, user: User):
        self.user = user

    async def get_current_user(self) -> User:
        return self.user


@pytest_asyncio.fixture(scope="function")
async def current_company_user(sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        session.add(user)
        session.flush()
    return user


@pytest_asyncio.fixture(scope="function")
async def test_job(sa_session, current_company_user):
    async with sa_session() as session:
        job = JobFactory.build(user_id=current_company_user.id, is_active=True)
        session.add(job)
        session.flush()
    return job


@pytest_asyncio.fixture(scope="function")
async def current_employee_user(sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=False)
        session.add(user)
        session.flush()
    return user


@pytest_asyncio.fixture(scope="function")
def identity_provider_company(current_company_user):
    return MockIDP(current_company_user)


@pytest_asyncio.fixture(scope="function")
def identity_provider_employee(current_employee_user):
    return MockIDP(current_employee_user)


@pytest_asyncio.fixture(scope="function")
def service_factory(user_repository, job_repository, response_repository):
    return ServicesFactory(user_repository, job_repository, response_repository)


@pytest_asyncio.fixture(scope="function")
def auth_service(service_factory):
    return service_factory.get_auth_service()


@pytest_asyncio.fixture(scope="function")
def user_service(service_factory, identity_provider_company):
    return service_factory.get_user_service(identity_provider_company)


@pytest_asyncio.fixture(scope="function")
def job_service(service_factory, identity_provider_company):
    return service_factory.get_job_service(identity_provider_company)


@pytest_asyncio.fixture(scope="function")
def response_service_employee(service_factory, identity_provider_employee):
    return service_factory.get_response_service(identity_provider_employee)


@pytest_asyncio.fixture(scope="function")
def response_service_company(service_factory, identity_provider_company):
    return service_factory.get_response_service(identity_provider_company)
