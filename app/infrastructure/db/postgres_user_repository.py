from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.entities.user_entity import User, UserRole
from app.domain.repositories.user_repository import AbstractUserRepository
from app.domain.common.logger import AbstractLogger
from app.infrastructure.db.models.user_model import UserModel, UserRoleEnum


class PostgresqlUserRepository(AbstractUserRepository):

    def __init__(self, session: AsyncSession, logger: AbstractLogger) -> None:
        self.session = session
        self.logger = logger

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        self.logger.debug(f"Fetching user by ID: {user_id}")
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        record = result.scalar_one_or_none()
        if record:
            self.logger.info(f"User found with ID: {user_id}")
        else:
            self.logger.warning(f"User not found with ID: {user_id}")
        return self._to_entity(record) if record else None
    
    async def get_by_email(self, email) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        record = result.scalar_one_or_none()
        if record:
            self.logger.info(f"User found with email: {email}")
        else:
            self.logger.warning(f"User not found with email: {email}")

        return self._to_entity(record) if record else None
    
    async def create(self, user: User) -> None:
        self.logger.debug(f"Creating user: {user}")
        db_user = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            role=UserRoleEnum(user.role.value),
            is_active=user.is_active,
            is_subscribed=user.is_subscribed,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        self.session.add(db_user)
        await self.session.commit()
        self.logger.info(f"User created with ID: {user.id}")

    async def update(self, user: User) -> None:
        self.logger.debug(f"Updating user: {user}")
        result = await self.session.execute(select(UserModel).where(UserModel.id == user.id))
        db_user = result.scalar_one_or_none()
        if db_user:
            db_user.full_name = user.full_name
            db_user.role = UserRoleEnum(user.role.value)
            db_user.email = user.email
            db_user.is_active = user.is_active
            db_user.is_subscribed = user.is_subscribed
            db_user.updated_at = user.updated_at
            await self.session.commit()
            self.logger.info(f"User updated with ID: {user.id}")

    async def soft_delete(self, user_id: UUID) -> None:
        self.logger.debug(f"Soft deleting user with ID: {user_id}")
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        db_user = result.scalar_one_or_none()
        if db_user:
            db_user.is_active = False
            await self.session.commit()
            self.logger.info(f"User soft deleted with ID: {user_id}")
    

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=UserRole(model.role.value),
            is_active=model.is_active,
            is_subscribed=model.is_subscribed,
            created_at=model.created_at,
            updated_at=model.updated_at
        )