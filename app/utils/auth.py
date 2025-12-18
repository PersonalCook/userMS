import os
import bcrypt
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone

JWT_SECRET = os.getenv("JWT_SECRET") 
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

if not JWT_SECRET or not JWT_ALGORITHM:
    raise RuntimeError("JWT_SECRET and JWT_ALGORITHM must be set in the environment for user_service")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_jwt(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt(token: str) -> dict:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded
    except ExpiredSignatureError:
        raise InvalidTokenError("Token expired")
    except InvalidTokenError:
        raise InvalidTokenError("Invalid token")
