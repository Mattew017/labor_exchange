from interfaces.i_identity_provider import IdentityProvider
from repositories import UserRepository, JobRepository, ResponseRepository
from services.auth import AuthService
from services.job import JobService
from services.response import ResponseService
from services.user import UserService


class ServicesFactory:
    def __init__(
        self,
        user_repository: UserRepository,
        job_repository: JobRepository,
        response_repository: ResponseRepository,
    ):
        self.user_repository = user_repository
        self.job_repository = job_repository
        self.response_repository = response_repository

    def get_auth_service(self) -> AuthService:
        return AuthService(
            user_repository=self.user_repository,
        )

    def get_user_service(self, identity_provider: IdentityProvider) -> UserService:
        return UserService(
            user_repository=self.user_repository, identity_provider=identity_provider
        )

    def get_job_service(self, identity_provider: IdentityProvider) -> JobService:
        return JobService(
            identity_provider=identity_provider,
            job_repository=self.job_repository,
        )

    def get_response_service(
        self, identity_provider: IdentityProvider
    ) -> ResponseService:
        return ResponseService(
            identity_provider=identity_provider,
            response_repository=self.response_repository,
            job_repository=self.job_repository,
        )
