from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from interfaces import ISQLAlchemy
from models import User as UserModel, Job as JobModel, Response as ResponseModel
from repositories import UserRepository, JobRepository, ResponseRepository
from repositories.mapper import MapperFactory
from services.factory import ServicesFactory
from services.identity_provider import JWTIdentityProvider, http_credentials_security
from storage.sqlalchemy.tables import User, Job, Response


def setup_mappers() -> MapperFactory:
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


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["web.routers", "dependencies", "services"]
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

    identity_provider = providers.Factory(
        JWTIdentityProvider,
        user_repository=user_repository,
    )

    services_factory = providers.Factory(
        ServicesFactory,
        user_repository=user_repository,
        job_repository=job_repository,
        response_repository=response_repository,
    )


@inject
def get_identity_provider(
    token: HTTPAuthorizationCredentials = Depends(http_credentials_security),
    user_repository: UserRepository = Depends(Provide[Container.user_repository]),
) -> JWTIdentityProvider:
    return JWTIdentityProvider(user_repository=user_repository, token=token.credentials)
