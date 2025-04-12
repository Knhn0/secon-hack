from models.reports import Reports
from utils.repository import SQLAlchemyRepository


class ReportsRepository(SQLAlchemyRepository):
    model = Reports
