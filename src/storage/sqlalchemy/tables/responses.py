from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sqlalchemy.client import Base


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор отклика")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="Идентификатор пользователя"
    )
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"), comment="Идентификатор вакансии"
    )

    # добавьте ваши колонки сюда
    message: Mapped[str | None] = mapped_column(
        comment="Сопроводительное письмо", nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="responses")  # noqa
    job: Mapped["Job"] = relationship(back_populates="responses")  # noqa

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_response"),
    )
