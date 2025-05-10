from fastapi import FastAPI
from app.presentation.http.user_handler import router as user_router
from app.presentation.http.exception_handlers import (
    user_already_exists_handler,
    invalid_credentials_handler
)
from app.infrastructure.security.middleware import JWTAuthMiddleware
from app.domain.exceptions import UserAlreadyExists, InvalidCredentials
from contextlib import asynccontextmanager
from app.infrastructure.logger.logger import get_logger
from app.infrastructure.kafka.kafka_topic_manager import KafkaTopicManager
from app.infrastructure.kafka.kafka_producer import KafkaProducer
from app.config.kafka_config import KAFKA_TOPICS
from app.infrastructure.logger.logger import get_logger
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get_logger("lifespan")
    logger.info("FastAPI lifespan started")

    # Create Kafka topics
    topic_manager = KafkaTopicManager(logger=logger)
    await topic_manager.create_topics(list(KAFKA_TOPICS.values()))

    # Start Kafka producer
    kafka_producer = KafkaProducer(bootstrap_servers="kafka:9092", logger=logger)
    await kafka_producer.connect()
    app.state.kafka_producer = kafka_producer

    yield

    # Cleanup
    logger.info("FastAPI lifespan stopped")
    await kafka_producer.stop()

app = FastAPI(lifespan=lifespan)
app.add_middleware(JWTAuthMiddleware)
app.include_router(user_router)

app.add_exception_handler(UserAlreadyExists, user_already_exists_handler)
app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)
