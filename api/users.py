from fastapi import APIRouter, Depends

from api.dependencies import UOWDep, get_current_user, check_role
from models.users import RoleEnum
from schemas.users import UserResponse
from services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_users(
        uow: UOWDep
) -> list[UserResponse]:
    return await UserService().get_users(uow)


@router.get("/me")
async def get_me(
        user: UserResponse = Depends(get_current_user)
):
    return user


@router.get("/admin", dependencies=[Depends(check_role([RoleEnum.admin]))])
async def get_admin():
    return "ok"
