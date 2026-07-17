"""Auth endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from barekat_cell_therapy.core.database import get_db
from barekat_cell_therapy.core.rbac import get_current_user
from barekat_cell_therapy.core.security import create_access_token, hash_password, verify_password
from barekat_cell_therapy.models.user import User
from barekat_cell_therapy.schemas import TokenResponse, UserLogin, UserRegister, UserResponse
from barekat_cell_therapy.services.audit import write_audit

router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserResponse:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="ایمیل قبلاً ثبت شده")
    user = User(
        user_id=f"USR_{uuid.uuid4().hex[:10].upper()}",
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    write_audit(db, "user.register", "user", user.user_id, actor_id=user.user_id)
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="ایمیل یا رمز عبور نادرست")
    token = create_access_token(user.user_id, user.role, user.email)
    write_audit(db, "user.login", "user", user.user_id, actor_id=user.user_id)
    return TokenResponse(access_token=token, role=user.role, user_id=user.user_id)


@router.get("/auth/me", response_model=UserResponse)
def me(user: User | None = Depends(get_current_user)) -> UserResponse:
    if user is None:
        raise HTTPException(status_code=401, detail="احراز هویت لازم است")
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )
