from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, check_role
from models.users import RoleEnum
from schemas.users import UserResponse

router = APIRouter()


@router.get('/ping')
async def ping():
    return 'pong'


@router.get("/security_ping", dependencies=[Depends(check_role([RoleEnum.admin, RoleEnum.employee]))])
async def secure_ping():
    return "pong"
