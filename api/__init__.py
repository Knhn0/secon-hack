from api.example import router as example_router
from api.users import router as user_router
from api.auth import router as auth_router
from api.reports import router as report_router

all_routers = [
    example_router,
    user_router,
    auth_router,
    report_router
]
