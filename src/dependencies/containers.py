from dependency_injector import containers, providers

from interfaces.i_sqlalchemy import ISQLAlchemy
from repositories import UserRepository, JobRepository, ResponseRepository
from repositories.mapper import MapperFactory
from storage.sqlalchemy.tables import Job, User, Response
from models import User as UserModel
from models import Job as JobModel
from models import Response as ResponseModel


def setup_mappers():
    factory = MapperFactory()
    factory.register(
        UserModel,
        User,
        [
            ("jobs", JobModel, Job),
            ("responses", ResponseModel, Response),
        ],
    )
    factory.register(
        JobModel,
        Job,
        [
            ("user", UserModel, User),
            ("responses", ResponseModel, Response),
        ],
    )
    factory.register(
        ResponseModel,
        Response,
        [
            ("user", UserModel, User),
            ("job", JobModel, Job),
        ],
    )
    return factory


class RepositoriesContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["web.routers", "dependencies"]
    )

    db = providers.Singleton(ISQLAlchemy)

    mapper_factory = providers.Singleton(setup_mappers)

    user_mapper = providers.Singleton(
        lambda factory: factory.get_mapper(UserModel, User), mapper_factory
    )
    job_mapper = providers.Singleton(
        lambda factory: factory.get_mapper(JobModel, Job), mapper_factory
    )
    response_mapper = providers.Singleton(
        lambda factory: factory.get_mapper(ResponseModel, Response), mapper_factory
    )

    user_repository = providers.Factory(
        UserRepository,
        session=db.provided.get_db,
        mapper=user_mapper,
    )

    job_repository = providers.Factory(
        JobRepository,
        session=db.provided.get_db,
        mapper=job_mapper,
    )

    response_repository = providers.Factory(
        ResponseRepository,
        session=db.provided.get_db,
        mapper=response_mapper,
    )
