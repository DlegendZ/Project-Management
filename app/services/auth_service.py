from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from app.config import settings
from app.exceptions import UnauthorizedException

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS
)

ALGORITHM = "HS256"


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def create_access_token(user_id: int, role: str, token_version: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": str(user_id),
            "role": role,
            "token_version": token_version,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int, token_version: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload = {
            "sub": str(user_id),
            "token_version": token_version,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                raise UnauthorizedException("invalid_token", "Invalid token type")
            return payload
        except ExpiredSignatureError:
            raise UnauthorizedException("token_expired", "Token has expired")
        except JWTError:
            raise UnauthorizedException("invalid_token", "Invalid token")

    @staticmethod
    def decode_refresh_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                raise UnauthorizedException("invalid_token", "Invalid token type")
            return payload
        except ExpiredSignatureError:
            raise UnauthorizedException("token_expired", "Refresh token has expired")
        except JWTError:
            raise UnauthorizedException("invalid_token", "Invalid refresh token")
