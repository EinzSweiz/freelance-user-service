from dataclasses import dataclass, field, asdict
from enum import Enum
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional


class UserRole(str, Enum):
    CLIENT = "client"
    FREELANCER = "freelancer"


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_subscribed: bool
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        
    def update(self, full_name: Optional[str] = None, role: Optional[UserRole] = None, email: Optional[str] = None):
        if full_name:
            self.full_name = full_name
        if role:
            self.role = role
        if email:
            self.email = email
        self.updated_at = datetime.now()
        
    @staticmethod
    def create(email: str, hashed_password: str, role: UserRole, full_name: Optional[str] = None) -> "User":
        now = datetime.now()
        return User(
            id=uuid4(),
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=False,
            is_subscribed=False,
            created_at=now,
            updated_at=now
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "hashed_password": self.hashed_password,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_subscribed": self.is_subscribed,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=UUID(data["id"]),
            email=data["email"],
            hashed_password=data["hashed_password"],
            full_name=data.get("full_name"),
            role=UserRole(data["role"]),
            is_active=data["is_active"],
            is_subscribed=data["is_subscribed"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
