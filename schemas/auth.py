from typing import Annotated

from pydantic import BaseModel, Field, EmailStr

from schemas.users import UserBase


class UserLogin(BaseModel):
    email: Annotated[EmailStr, Field(description="Почта пользователя")]
    password: Annotated[
        str,
        Field(min_length=2, description="Пароль (минимум 2 символа)")
    ]


class UserRegister(UserBase):
    password: Annotated[
        str,
        Field(min_length=2, description="Пароль (минимум 2 символов)")
    ]


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
