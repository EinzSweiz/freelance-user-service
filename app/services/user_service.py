from app.domain.repositories.user_repository import AbstractUserRepository
from app.domain.entities.user_entity import User, UserRole
from app.domain.common.logger import AbstractLogger
from app.domain.exceptions import UserAlreadyExists, InvalidCredentials
from app.infrastructure.security.password_hasher import hash_password, verify_password
from app.infrastructure.security.jwt import create_access_token, create_refresh_token
from app.infrastructure.kafka.kafka_producer import KafkaProducer
from app.infrastructure.redis.redis_token_service import RedisTokenBlacklist
from app.config.kafka_config import KAFKA_TOPICS
from datetime import datetime
class UserService:
    def __init__(self, user_repo: AbstractUserRepository, logger: AbstractLogger, kafka_producer: KafkaProducer):
        self.user_repo = user_repo
        self.logger = logger
        self.kafka_producer = kafka_producer

    async def register(self, email: str, password: str, full_name: str, role: UserRole) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            self.logger.warning(f"Registration failed: user with email '{email}' already exists.")
            raise UserAlreadyExists(f"User with email {email} already exists")
        hashed = hash_password(password)
        user = User.create(email, hashed, role, full_name)
        await self.user_repo.create(user)
        self.logger.info(f"User registered: {user}")
        await self.kafka_producer.send(
            topic=KAFKA_TOPICS["user_registered"],
            event={
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "timestamp": datetime.now().isoformat()
            }
        )
        return user
    
    async def login(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if not user:
            self.logger.warning(f"Login failed: user with email '{email}' not found.")
            raise InvalidCredentials("Invalid email or password")
        
        if not verify_password(password, user.hashed_password):
            self.logger.warning(f"Login failed: incorrect password for user with email '{email}'.")
            raise InvalidCredentials("Invalid email or password")
        self.logger.info(f"User logged in: {user}")
        await self.kafka_producer.send(
            topic=KAFKA_TOPICS["user_logged_in"],
            event={
                "user_id": str(user.id),
                "timestamp": datetime.now().isoformat()
            }
        )
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        return user.id, access_token, refresh_token
    
    async def logout(self, jti: str, exp: int, user_id: str, token_blacklist_service: RedisTokenBlacklist):
        await token_blacklist_service.blacklist_token(jti, exp)
        self.logger.info(f"User logged out: {user_id}")

        await self.kafka_producer.send(
            topic=KAFKA_TOPICS["user_logged_out"],
            event={
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
