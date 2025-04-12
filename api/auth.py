from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.dependencies import UOWDep
from schemas.auth import UserLogin, UserRegister, TokenInfo
from services.auth import AuthService

router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login(
        uow: UOWDep,
        user: UserLogin
) -> TokenInfo:
    return await AuthService().login(uow, user)


@router.post("/register")
async def register(
        uow: UOWDep,
        user: UserRegister
) -> TokenInfo:
    return await AuthService().register(uow, user)


security = HTTPBearer()


@router.post("/refresh")
async def refresh(
        uow: UOWDep,
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return await AuthService().refresh(uow, credentials.credentials)
