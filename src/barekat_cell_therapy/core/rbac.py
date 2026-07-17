"""RBAC ساده برای نقش‌های بالینی و عملیاتی."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from barekat_cell_therapy.core.database import get_db
from barekat_cell_therapy.core.security import TokenDecodeError, verify_access_token
from barekat_cell_therapy.models.user import User

bearer = HTTPBearer(auto_error=False)

ROLE_HIERARCHY = {
    "viewer": 1,
    "clinician": 2,
    "scientist": 3,
    "admin": 4,
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """اختیاری: اگر توکن نباشد None برمی‌گرداند (حالت توسعه)."""
    from barekat_cell_therapy.core.config import get_settings

    settings = get_settings()
    if credentials is None:
        if settings.auth_required:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="احراز هویت لازم است")
        return None
    try:
        payload = verify_access_token(credentials.credentials)
    except TokenDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = db.query(User).filter(User.user_id == payload["sub"]).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="کاربر یافت نشد")
    return user


def require_role(min_role: str):
    def _dep(user: User | None = Depends(get_current_user)) -> User | None:
        from barekat_cell_therapy.core.config import get_settings

        if user is None and not get_settings().auth_required:
            return None
        if user is None:
            raise HTTPException(status_code=401, detail="احراز هویت لازم است")
        if ROLE_HIERARCHY.get(user.role, 0) < ROLE_HIERARCHY.get(min_role, 99):
            raise HTTPException(status_code=403, detail="دسترسی کافی نیست")
        return user

    return _dep
