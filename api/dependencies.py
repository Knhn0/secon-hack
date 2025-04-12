from typing import Annotated, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import utils.jwt_utils as jwt_utils
from jwt.exceptions import PyJWTError

from models.users import RoleEnum
from schemas.users import UserResponse, UserFull
from utils.unitofwork import IUnitOfWork, UnitOfWork


async def get_uow() -> IUnitOfWork:
    uow = UnitOfWork()
    await uow.__aenter__()
    try:
        yield uow
    finally:
        await uow.__aexit__(None, None, None)


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]

security = HTTPBearer()


async def get_current_user(
        uow: UOWDep,
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    token = credentials.credentials
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid credentials",
    )
    try:
        payload = jwt_utils.decode_jwt(token)
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exc
    except PyJWTError:
        raise credentials_exc

    user_full: UserFull = await uow.users.find_one(id=user_id)
    if user_full is None:
        raise credentials_exc

    return UserResponse.model_validate(user_full)


def check_role(allowed_roles: list[RoleEnum]) -> Callable:
    async def role_checker(user: UserResponse = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return role_checker
