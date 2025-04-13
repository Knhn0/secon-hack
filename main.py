from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import all_routers
app = FastAPI(title='SeconHack')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

for router in all_routers:
    app.include_router(router)