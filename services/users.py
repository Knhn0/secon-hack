from fastapi import HTTPException, status
from schemas.users import UserUpdate
from utils.unitofwork import IUnitOfWork


class UserService:
    async def get_users(self, uow: IUnitOfWork):
        return await uow.users.find_all()

    async def edit_user(self, uow: IUnitOfWork, user: UserUpdate):
        exist_user = await uow.users.find_one(email=user.email)
        if exist_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn`t exist")

        user_dict = user.model_dump()
        user_id = await uow.users.edit_one(**user_dict)
        await uow.commit()
        return user_id

    async def delete_user(self, uow: IUnitOfWork, id: int):
        user_id = await uow.users.delete_one(id)
        await uow.commit()
        return user_id
