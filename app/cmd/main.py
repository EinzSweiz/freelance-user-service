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
from app.infrastructure.db.db_session import engine
from sqlalchemy import text
import asyncio
import asyncpg
from sqlalchemy.exc import OperationalError, DBAPIError
logger = get_logger("UserService")
async def wait_for_db(max_retries=10, delay=2):
    for attempt in range(max_retries):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("✅ Database is ready!")
                return
        except (OperationalError, asyncpg.InvalidCatalogNameError, DBAPIError) as e:
            logger.warning(f"❌ DB not ready (attempt {attempt + 1}/{max_retries}) — {e}")
            await asyncio.sleep(delay)

    raise RuntimeError("❌ Could not connect to the database after retries")
@asynccontextmanager
async def lifespan(app: FastAPI):
    await wait_for_db()
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
