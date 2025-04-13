from datetime import datetime, timedelta
import jwt
import bcrypt

import config
from schemas.auth import TokenInfo


def encode_jwt(
        payload: dict,
        expire_minutes: int,
        key: str = config.SECRET_JWT_KEY,
        algorithm: str = config.JWT_ALGORITHM,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now
    )
    encoded = jwt.encode(to_encode, key, algorithm=algorithm)
    return encoded


def generate_tokens(
        id,
        role
) -> TokenInfo:
    access_payload = {
        "sub": str(id),
        "role": role
    }

    refresh_payload = {
        "sub": str(id),
        "type": "refresh"
    }
    access_token = encode_jwt(access_payload, expire_minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = encode_jwt(refresh_payload, expire_minutes=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer"
    )

def decode_jwt(
        token: str | bytes,
        key: str = config.SECRET_JWT_KEY,
        algorithm: str = config.JWT_ALGORITHM
):
    decoded = jwt.decode(token, key, algorithms=[algorithm])
    return decoded


def hash_password(
        password: str
) -> str:
    bytes_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return bytes_pass.decode("utf-8")


def validate_password(
        password: str,
        hashed_password: str
):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
