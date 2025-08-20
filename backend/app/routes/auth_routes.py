from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.database.base import get_db
from app.database import models
from app.schemas import LoginRequest, RefreshRequest, UserInfo  # Import specific schema classes
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    ADMIN_TOKEN,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.post("/register", response_model=schemas.UserRead)
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db), x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token")):
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    if payload.role == 'doctor' and x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin token required for doctor registration")

    new_user = models.User(
        **payload.dict(exclude={"password"}),
        password_hash=hash_password(payload.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash) or user.role != payload.role.lower():
        raise HTTPException(status_code=401, detail="Invalid credentials or role")

    access_token = create_access_token({"role": user.role, "user_id": user.user_id})
    refresh_token = create_refresh_token({"role": user.role, "user_id": user.user_id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/token", response_model=schemas.Token)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username
    password = form_data.password
    scopes = set((form_data.scopes or []))
    role = "admin" if "admin" in scopes else ("doctor" if "doctor" in scopes else "patient")

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user or not verify_password(password, user.password_hash) or user.role != role:
        raise HTTPException(status_code=401, detail="Invalid credentials or role")

    access_token = create_access_token({"role": user.role, "user_id": user.user_id})
    refresh_token = create_refresh_token({"role": user.role, "user_id": user.user_id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(payload: schemas.RefreshRequest):
    info = get_current_user(payload.refresh_token, expected_type="refresh")
    if not info:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    role, user_id = info
    access_token = create_access_token({"role": role, "user_id": user_id})
    new_refresh = create_refresh_token({"role": role, "user_id": user_id})
    return {"access_token": access_token, "refresh_token": new_refresh, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserInfo)
def me(token: str = Depends(oauth2_scheme)):
    info = get_current_user(token, expected_type="access")
    if not info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    role, user_id = info
    return {"role": role, "user_id": user_id}
