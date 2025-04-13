import os

import dotenv
USE_DOCKER = os.getenv("USE_DOCKER", "false").lower() == "true"

dotenv.load_dotenv(".env.example")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST_DOCKER") if USE_DOCKER else os.getenv("DB_HOST")
if USE_DOCKER:
    MINIO_ENDPOINT = os.getenv("MINIO_DOCKER_ENDPOINT", "minio:9000")
else:
    MINIO_ENDPOINT = os.getenv("MINIO_LOCAL_ENDPOINT", "localhost:9000")
DB_PORT = os.getenv("DB_PORT")
DB_PASS = os.getenv("DB_PASS")
SECRET_JWT_KEY = os.getenv("SECRET_JWT_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_MINUTES"))

MINIO_PORT = os.getenv("MINIO_PORT")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MINIO_URL = f"http://{MINIO_ENDPOINT}:{MINIO_PORT}"
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
ALEMBIC_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
