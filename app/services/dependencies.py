from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.infrastructure.db.db_session import get_session
from app.infrastructure.db.postgres_user_repository import PostgresqlUserRepository
from app.infrastructure.logger.logger import get_logger
from app.domain.common.logger import AbstractLogger
from app.services.user_service import UserService


def get_user_service(
    session: AsyncSession = Depends(get_session),
    logger: AbstractLogger = Depends(get_logger),
) -> UserService:
    repo = PostgresqlUserRepository(session, logger)
    return UserService(user_repo=repo, logger=logger)
