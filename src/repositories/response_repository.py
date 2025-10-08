import logging
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from interfaces import IRepositoryAsync
from models import Job as JobModel
from models import Response as ResponseModel
from models import User as UserModel
from storage.sqlalchemy.tables import Response
from tools.exceptions import EntityNotFoundError
from web.schemas.response import ResponseCreateSchema, ResponseUpdateSchema

logger = logging.getLogger(__name__)


class ResponseRepository(IRepositoryAsync):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(
        self, response_create_dto: ResponseCreateSchema, job_id: int, user_id: int
    ) -> ResponseModel:
        async with self.session() as session:
            response = Response(
                job_id=job_id,
                user_id=user_id,
                message=response_create_dto.message,
            )

            session.add(response)
            await session.commit()
            await session.refresh(response)

        logger.debug("Created response job_id=%d user_id=%d", job_id, user_id)
        return self.__to_response_model(response_from_db=response)

    async def retrieve(
        self, include_relations: bool = False, **kwargs
    ) -> ResponseModel:
        async with self.session() as session:
            query = select(Response).filter_by(**kwargs).limit(1)
            if include_relations:
                query = query.options(joinedload(Response.user)).options(
                    joinedload(Response.job)
                )

            res = await session.execute(query)
            response_from_db = res.scalars().first()
        if response_from_db is None:
            raise EntityNotFoundError("Отклик не найден")
        response_model = self.__to_response_model(
            response_from_db=response_from_db, include_relations=include_relations
        )
        logger.debug("Retrieved response id=%d", response_model.id)
        return response_model

    async def retrieve_many(
        self, limit: int = 100, skip: int = 0, include_relations: bool = False, **kwargs
    ) -> list[ResponseModel]:
        async with self.session() as session:
            query = select(Response).filter_by(**kwargs).limit(limit).offset(skip)
            if include_relations:
                query = query.options(joinedload(Response.user)).options(
                    joinedload(Response.job)
                )

            res = await session.execute(query)
            responses_from_db = res.scalars().all()

        responses_model = []
        for response in responses_from_db:
            model = self.__to_response_model(
                response_from_db=response, include_relations=include_relations
            )
            responses_model.append(model)

        return responses_model

    async def update(
        self, id_: int, response_update_dto: ResponseUpdateSchema
    ) -> ResponseModel:
        async with self.session() as session:
            query = select(Response).filter_by(id=id_).limit(1)
            res = await session.execute(query)
            response_from_db = res.scalars().first()

            if not response_from_db:
                raise EntityNotFoundError("Отклик не найден")

            response_from_db.message = (
                response_update_dto.message
                if response_update_dto.message
                else response_update_dto.message
            )

            session.add(response_from_db)
            await session.commit()
            await session.refresh(response_from_db)

        logger.debug("Updated response id=%d", id_)

        new_response = self.__to_response_model(response_from_db)
        return new_response

    async def delete(self, id_: int):
        async with self.session() as session:
            query = select(Response).filter_by(id=id_).limit(1)
            res = await session.execute(query)
            response_from_db = res.scalars().first()

            if response_from_db:
                await session.delete(response_from_db)
                await session.commit()
                logger.debug("Deleted response id=%d", id_)
            else:
                raise EntityNotFoundError("Отклик не найден")

        return self.__to_response_model(response_from_db)

    @staticmethod
    def __to_response_model(
        response_from_db: Response, include_relations: bool = False
    ) -> ResponseModel:
        response_user = None
        response_job = None
        if include_relations:
            response_user = UserModel(
                id=response_from_db.user_id,
                name=response_from_db.user.name,
                email=response_from_db.user.email,
                hashed_password=response_from_db.user.hashed_password,
                is_company=response_from_db.user.is_company,
            )
            response_job = JobModel(
                id=response_from_db.job_id,
                user_id=response_from_db.user.id,
                title=response_from_db.job.title,
                description=response_from_db.job.description,
                is_active=response_from_db.job.is_active,
                salary_from=response_from_db.job.salary_from,
                salary_to=response_from_db.job.salary_to,
            )
        response_model = ResponseModel(
            id=response_from_db.id,
            message=response_from_db.message,
            job=response_job,
            user=response_user,
        )

        return response_model
