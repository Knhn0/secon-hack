from fastapi import Depends, HTTPException, status
from jwt.exceptions import PyJWTError
import utils.jwt_utils as auth_utils
from schemas.auth import TokenInfo, UserRegister
from schemas.users import UserFull
from schemas.auth import UserLogin
from utils.unitofwork import IUnitOfWork


class AuthService:
    async def login(
            self,
            uow: IUnitOfWork,
            user: UserLogin
    ) -> TokenInfo:
        un_authed_exc = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="invalid email or password")
        exist_user: UserFull = await uow.users.find_one(email=user.email)
        if not exist_user:
            raise un_authed_exc

        if not auth_utils.validate_password(
                user.password,
                exist_user.password
        ):
            raise un_authed_exc

        tokens: TokenInfo = auth_utils.generate_tokens(exist_user.id, exist_user.role)
        await uow.users.edit_one(exist_user.id, refresh_token=tokens.refresh_token)
        await uow.commit()
        return tokens

    async def register(
            self,
            uow: IUnitOfWork,
            user: UserRegister
    ):
        exist_user = await uow.users.find_one(email=user.email)
        if exist_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Почта уже используется")

        user.password = auth_utils.hash_password(password=user.password)
        user_dict = user.model_dump()
        user_id = await uow.users.add_one(user_dict)
        await uow.commit()

        tokens: TokenInfo = auth_utils.generate_tokens(user_id, user.role)
        await uow.users.edit_one(user_id, refresh_token=tokens.refresh_token)
        await uow.commit()
        return tokens

    async def refresh(
            self,
            uow: IUnitOfWork,
            refresh_token: str
    ):
        un_auth_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")
        try:
            payload = auth_utils.decode_jwt(refresh_token)
            user_id = int(payload.get("sub"))
        except PyJWTError:
            raise un_auth_exc

        user: UserFull = await uow.users.find_one(id=user_id)
        if not user or user.refresh_token != refresh_token:
            raise un_auth_exc

        tokens: TokenInfo = auth_utils.generate_tokens(user_id, user.role)
        await uow.users.edit_one(_id=user_id, refresh_token=tokens.refresh_token)
        await uow.commit()
        return tokens
