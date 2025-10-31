import pytest
from pydantic import ValidationError

from web.schemas import UserCreateSchema, UserUpdateSchema


class TestUserService:

    @pytest.mark.asyncio
    async def test_create_user(self, user_service):
        dto = UserCreateSchema(
            name="test_user",
            email="test_user@test.com",
            password="test_user",
            password2="test_user",
            is_company=True,
        )
        new_user = await user_service.create(dto)
        assert new_user
        assert new_user.email == "test_user@test.com"
        assert new_user.name == "test_user"

    @pytest.mark.asyncio
    async def test_create_user_missmatched_passwords(self, user_service):
        with pytest.raises(ValidationError):
            dto = UserCreateSchema(
                name="test_user",
                email="test_user@test.com",
                password="first_password",
                password2="missmatch_password",
                is_company=True,
            )
            await user_service.create(dto)

    @pytest.mark.asyncio
    async def test_create_user_short_password(self, user_service):
        with pytest.raises(ValidationError):
            dto = UserCreateSchema(
                name="test_user",
                email="test_user@test.com",
                password="123",
                password2="123",
                is_company=True,
            )
            await user_service.create(dto)

    @pytest.mark.asyncio
    async def test_get_all(self, user_service):
        all_users = await user_service.get_all_users(limit=100, skip=0)
        assert all_users
        assert len(all_users) == 1

    @pytest.mark.asyncio
    async def test_get_by_id(self, user_service, identity_provider_company):
        current = await identity_provider_company.get_current_user()
        user = await user_service.get_user_by_id(user_id=current.id)
        assert user.id == current.id

    @pytest.mark.asyncio
    async def test_update(self, user_service):
        updated = await user_service.edit_user(
            UserUpdateSchema(name="new_name", email="new_email@email.com", is_company=True)
        )
        assert updated.name == "new_name"
        assert updated.email == "new_email@email.com"
