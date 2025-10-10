from dataclasses import dataclass

from interfaces.i_identity_provider import IdentityProvider
from interfaces.i_service import ServiceInterface
from models import Response
from repositories import ResponseRepository, JobRepository
from tools.exceptions import (
    InactiveJobError,
    DuplicateResponseError,
    PermissionDeniedError,
)
from web.schemas.response import ResponseCreateSchema


@dataclass(frozen=True, slots=True)
class CreateResponseOutputDTO:
    response: Response
    user_id: int


class ResponseService(ServiceInterface):
    def __init__(
        self,
        response_repository: ResponseRepository,
        job_repository: JobRepository,
        identity_provider: IdentityProvider,
    ):
        self.response_repository = response_repository
        self.job_repository = job_repository
        self.identity_provider = identity_provider

    async def get_all_active_responses(self, limit: int, skip: int) -> list[Response]:
        current_user = await self.identity_provider.get_current_user()
        if current_user.is_company:
            raise PermissionDeniedError("Недостаточно прав")
        responses_model = await self.response_repository.retrieve_many(
            limit,
            skip,
            include_relations=True,
        )
        responses_model = [r for r in responses_model if r.job.is_active]
        return responses_model

    async def get_by_job_id(self, job_id: str, limit: int, skip: int) -> list[Response]:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.is_company:
            raise PermissionDeniedError(
                "Просматривать отклики на вакансию может только работодатель"
            )
        job_model = await self.job_repository.retrieve(id=job_id)
        responses_model = await self.response_repository.retrieve_many(
            limit,
            skip,
            include_relations=True,
            job_id=job_model.id,
        )
        return responses_model

    async def create(
        self,
        job_id: int,
        response_create_dto: ResponseCreateSchema,
    ) -> CreateResponseOutputDTO:
        current_user = await self.identity_provider.get_current_user()
        if current_user.is_company:
            raise PermissionDeniedError("Компания не может откликаться")
        job_model = await self.job_repository.retrieve(id=job_id)
        if not job_model.is_active:
            raise InactiveJobError()

        response_model = await self.response_repository.retrieve_many(
            limit=1, skip=0, job_id=job_id, user_id=current_user.id
        )
        if len(response_model) > 0:
            raise DuplicateResponseError()

        new_response = await self.response_repository.create(
            response_create_dto, job_id=job_id, user_id=current_user.id
        )
        return CreateResponseOutputDTO(response=new_response, user_id=current_user.id)
