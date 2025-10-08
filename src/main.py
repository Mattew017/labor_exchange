import logging
import os
from pathlib import Path

import uvicorn
from dependency_injector import providers
from fastapi import FastAPI

from config import DBSettings
from dependencies.containers import RepositoriesContainer
from storage.sqlalchemy.client import SqlAlchemyAsync
from tools.exceptions import (
    EntityNotFoundError,
    InactiveJobError,
    DuplicateResponseError,
)
from tools.handlers import (
    not_found_exception_handler,
    inactive_job_exception_handler,
    duplicate_response_exception_handler,
)
from web.routers import auth_router, user_router, job_router

env_file_name = ".env." + os.environ.get("STAGE", "dev")
env_file_path = Path(__file__).parent.resolve() / env_file_name


def add_exception_handlers(application: FastAPI):
    application.add_exception_handler(EntityNotFoundError, not_found_exception_handler)
    application.add_exception_handler(InactiveJobError, inactive_job_exception_handler)
    application.add_exception_handler(
        DuplicateResponseError, duplicate_response_exception_handler
    )


def create_app():
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    repo_container = RepositoriesContainer()
    settings = DBSettings(_env_file=env_file_path)

    # выбор синхронных / асинхронных реализаций
    repo_container.db.override(
        providers.Factory(
            SqlAlchemyAsync,
            pg_settings=settings,
        ),
    )

    # инициализация приложения
    app = FastAPI()
    app.container = repo_container

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(job_router)

    return app


app = create_app()
add_exception_handlers(app)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
