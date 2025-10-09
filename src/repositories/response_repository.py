import logging
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from interfaces import IRepositoryAsync
from models import Job as JobModel
from models import Response as ResponseModel
from models import User as UserModel
from repositories.mapper import DynamicMapper
from storage.sqlalchemy.tables import Response
from tools.exceptions import EntityNotFoundError
from web.schemas.response import ResponseCreateSchema, ResponseUpdateSchema

logger = logging.getLogger(__name__)


class ResponseRepository(IRepositoryAsync):
    def __init__(
        self,
        session: Callable[..., AbstractContextManager[Session]],
        mapper: DynamicMapper,
    ):
        self.session = session
        self.mapper = mapper

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
        return self.mapper.map_to_model(response)

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
        response_model = self.mapper.map_to_model(
            response_from_db, include_relations=include_relations
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
            model = self.mapper.map_to_model(
                response, include_relations=include_relations
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

        new_response = self.mapper.map_to_model(response_from_db)
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

        return self.mapper.map_to_model(response_from_db)
