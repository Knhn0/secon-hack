import enum

from db.db import Base
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column


class RoleEnum(str, enum.Enum):
    admin = "admin"
    employee = "employee"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    second_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, name="role_enum", native_enum=True, create_type=False),
                                           nullable=False)
    refresh_token: Mapped[str | None] = mapped_column()
