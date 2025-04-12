from typing import Annotated

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from models.users import RoleEnum


class UserBase(BaseModel):
    first_name: Annotated[
        str,
        Field(min_length=2, max_length=100, description="Имя (от 2 до 100 символов)")
    ]
    second_name: Annotated[
        str | None,
        Field(
            default=None,
            min_length=2,
            max_length=100,
            description="Отчество (необязательно, от 2 до 100 символов)"
        )
    ] = None
    last_name: Annotated[
        str,
        Field(min_length=2, max_length=50, description="Фамилия (от 2 до 50 символов)")
    ]
    email: Annotated[EmailStr, Field(description="Почта пользователя")]
    role: Annotated[
        RoleEnum,
        Field(default=RoleEnum.employee, description="Роль пользователя (employee или admin)")
    ]


class UserFull(UserBase):
    id: Annotated[int, Field()]
    password: Annotated[
        str,
        Field(min_length=2, description="Пароль (минимум 2 символов)")
    ]
    refresh_token: Annotated[str, Field()]


class UserUpdate(BaseModel):
    first_name: Annotated[
        str | None,
        Field(default=None, min_length=2, max_length=100, description="Имя (от 2 до 100 символов)")
    ] = None
    second_name: Annotated[
        str | None,
        Field(default=None, min_length=2, max_length=100, description="Отчество (если требуется обновить)")
    ] = None
    last_name: Annotated[
        str | None,
        Field(default=None, min_length=2, max_length=50, description="Фамилия (от 2 до 50 символов)")
    ] = None
    email: Annotated[EmailStr | None, Field(description="Почта пользователя")]
    role: Annotated[
        RoleEnum | None,
        Field(default=None, description="Роль пользователя (employee или admin)")
    ] = None


class UserResponse(UserBase):
    id: Annotated[int, Field()]

    model_config = ConfigDict(extra="forbid", from_attributes=True)
