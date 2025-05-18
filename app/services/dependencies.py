from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.infrastructure.db.db_session import get_session
from app.infrastructure.db.postgres_user_repository import PostgresqlUserRepository
from app.infrastructure.logger.logger import get_logger
from app.domain.common.logger import AbstractLogger
from app.infrastructure.kafka.kafka_producer import get_kafka_producer, KafkaProducer
from app.services.user_service import UserService


def get_user_service(
    session: AsyncSession = Depends(get_session),
    logger: AbstractLogger = Depends(get_logger),
    kafka_producer: KafkaProducer = Depends(get_kafka_producer),
) -> UserService:
    repo = PostgresqlUserRepository(session, logger)
    return UserService(user_repo=repo, logger=logger, kafka_producer=kafka_producer)
