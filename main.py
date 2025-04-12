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
# Конфигурация MinIO
# MINIO_ENDPOINT = "localhost:9000"
# MINIO_ACCESS_KEY = "minioadmin"
# MINIO_SECRET_KEY = "minioadmin"
# MINIO_BUCKET = "uploads"
#
# minio_client = Minio(
#     MINIO_ENDPOINT,
#     access_key=MINIO_ACCESS_KEY,
#     secret_key=MINIO_SECRET_KEY,
#     secure=False  # True если используется https
# )
#
# if not minio_client.bucket_exists(MINIO_BUCKET):
#     minio_client.make_bucket(MINIO_BUCKET)

for router in all_routers:
    app.include_router(router)