import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4
from enum import Enum
from app.infrastructure.db.db_session import Base
from datetime import datetime



class UserRoleEnum(str, Enum):
    CLIENT = "client"
    FREELANCER = "freelancer"


class UserModel(Base):
    __tablename__ = "users"

    id = sa.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = sa.Column(sa.String, unique=True, nullable=False)
    hashed_password = sa.Column(sa.String, nullable=False)
    full_name = sa.Column(sa.String, nullable=True)
    role = sa.Column(sa.Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.CLIENT)
    is_active = sa.Column(sa.Boolean, default=True)
    is_subscribed = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
