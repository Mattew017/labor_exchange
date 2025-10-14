from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sqlalchemy.client import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор вакансии")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="Идентификатор пользователя"
    )

    # добавьте ваши колонки сюда
    title: Mapped[str] = mapped_column(comment="Название вакансии")
    description: Mapped[str] = mapped_column(comment="Описание вакансии")
    salary_from: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Зарплата от", nullable=True
    )
    salary_to: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Зарплата до", nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        comment="Активна ли вакансия", default=True, server_default="True"
    )
    created_at: Mapped[datetime] = mapped_column(
        comment="Дата создания записи", default=datetime.utcnow
    )
    user: Mapped["User"] = relationship(back_populates="jobs")  # noqa
    responses: Mapped["Response"] = relationship(back_populates="job")  # noqa
