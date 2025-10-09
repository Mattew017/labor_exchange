from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from interfaces import IRepositoryAsync
from models import Job as JobModel
from models import Response as ResponseModel
from models import User as UserModel
from repositories.mapper import DynamicMapper
from storage.sqlalchemy.tables import User
from tools.exceptions import EntityNotFoundError
from web.schemas import UserCreateSchema, UserUpdateSchema


class UserRepository(IRepositoryAsync):
    def __init__(
        self,
        session: Callable[..., AbstractContextManager[Session]],
        mapper: DynamicMapper,
    ):
        self.session = session
        self.mapper = mapper

    async def create(
        self, user_create_dto: UserCreateSchema, hashed_password: str
    ) -> UserModel:
        async with self.session() as session:
            user = User(
                name=user_create_dto.name,
                email=user_create_dto.email,
                is_company=user_create_dto.is_company,
                hashed_password=hashed_password,
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

        return self.mapper.map_to_model(user, include_relations=False)

    async def retrieve(self, include_relations: bool = False, **kwargs) -> UserModel:
        async with self.session() as session:
            query = select(User).filter_by(**kwargs).limit(1)
            if include_relations:
                query = query.options(selectinload(User.jobs)).options(
                    selectinload(User.responses)
                )

            res = await session.execute(query)
            user_from_db = res.scalars().first()
            if not user_from_db:
                raise EntityNotFoundError("Пользователь не найден")

        user_model = self.mapper.map_to_model(
            user_from_db, include_relations=include_relations
        )
        return user_model

    async def retrieve_many(
        self, limit: int = 100, skip: int = 0, include_relations: bool = False
    ) -> list[UserModel]:
        async with self.session() as session:
            query = select(User).limit(limit).offset(skip)
            if include_relations:
                query = query.options(selectinload(User.jobs)).options(
                    selectinload(User.responses)
                )

            res = await session.execute(query)
            users_from_db = res.scalars().all()

        users_model = []
        for user in users_from_db:
            model = self.mapper.map_to_model(user, include_relations=include_relations)
            users_model.append(model)

        return users_model

    async def update(self, id_: int, user_update_dto: UserUpdateSchema) -> UserModel:
        async with self.session() as session:
            query = select(User).filter_by(id=id_).limit(1)
            res = await session.execute(query)
            user_from_db = res.scalars().first()

            if not user_from_db:
                raise EntityNotFoundError("Пользователь не найден")

            name = (
                user_update_dto.name
                if user_update_dto.name is not None
                else user_from_db.name
            )
            email = (
                user_update_dto.email
                if user_update_dto.email is not None
                else user_from_db.email
            )
            is_company = (
                user_update_dto.is_company
                if user_update_dto.is_company is not None
                else user_from_db.is_company
            )

            user_from_db.name = name
            user_from_db.email = email
            user_from_db.is_company = is_company

            session.add(user_from_db)
            await session.commit()
            await session.refresh(user_from_db)

        new_user = self.mapper.map_to_model(user_from_db, include_relations=False)
        return new_user

    async def delete(self, id_: int):
        async with self.session() as session:
            query = select(User).filter_by(id=id_).limit(1)
            res = await session.execute(query)
            user_from_db = res.scalars().first()

            if user_from_db:
                await session.delete(user_from_db)
                await session.commit()
            else:
                raise EntityNotFoundError("Пользователь не найден")

        return self.mapper.map_to_model(user_from_db, include_relations=False)
