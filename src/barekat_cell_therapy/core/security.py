"""امنیت: JWT سبک با PyJWT و PBKDF2."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from barekat_cell_therapy.core.config import get_settings

ALGORITHM = "HS256"


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"{salt}${digest.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, digest = hashed_password.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), 120_000).hex()
    return secrets.compare_digest(check, digest)


def create_access_token(user_id: str, role: str, email: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user_id, "role": role, "email": email, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


class TokenDecodeError(Exception):
    pass


def verify_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise TokenDecodeError("توکن نامعتبر یا منقضی شده") from exc
