from utils.repository import SQLAlchemyRepository
from models.users import Users


class UsersRepository(SQLAlchemyRepository):
    model = Users
