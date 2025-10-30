import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import DBSettings
from dependencies.containers import setup_mappers
from main import app
from models import Job as JobModel
from models import Response as ResponseModel
from models import User as UserModel
from repositories import JobRepository, ResponseRepository, UserRepository
from storage.sqlalchemy.tables import Job, Response, User
from tools.fixtures.users import UserFactory

env_file_name = ".env." + os.environ.get("STAGE", "test")
env_file_path = Path(__file__).parent.parent.resolve() / env_file_name
settings = DBSettings(_env_file=env_file_path)


@pytest.fixture(scope="session")
def client_app():
    client = TestClient(app)
    return client


@pytest.fixture(scope="session")
def sa_engine():
    engine = create_async_engine(str(settings.pg_async_dsn))
    return engine


@pytest_asyncio.fixture(scope="function")
async def sa_session(sa_engine):
    connection = await sa_engine.connect()
    trans = await connection.begin()

    Session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)  # noqa
    session = Session()

    deletion = session.delete

    async def mock_delete(instance):
        insp = inspect(instance)
        if not insp.persistent:
            session.expunge(instance)
        else:
            await deletion(instance)

        return await asyncio.sleep(0)

    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    @asynccontextmanager
    async def db():
        yield session

    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    try:
        yield db
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
        await sa_engine.dispose()


@pytest.fixture(scope="session")
def repos_mapper():
    mapper_factory = setup_mappers()
    return mapper_factory


@pytest_asyncio.fixture(scope="function")
async def user_repository(sa_session, repos_mapper):
    repository = UserRepository(session=sa_session, mapper=repos_mapper.get_mapper(UserModel, User))
    yield repository


@pytest_asyncio.fixture(scope="function")
async def job_repository(sa_session, repos_mapper):
    repository = JobRepository(session=sa_session, mapper=repos_mapper.get_mapper(JobModel, Job))
    yield repository


@pytest_asyncio.fixture(scope="function")
async def response_repository(sa_session, repos_mapper):
    repository = ResponseRepository(
        session=sa_session, mapper=repos_mapper.get_mapper(ResponseModel, Response)
    )
    yield repository


# регистрация фабрик
@pytest_asyncio.fixture(scope="function", autouse=True)
def setup_factories(sa_session: AsyncSession) -> None:
    UserFactory.session = sa_session
