from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database import get_db
import models
import schemas
from utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    ADMIN_TOKEN,
)

router = APIRouter()

# OAuth2 scheme for Swagger UI "Authorize" button (uses access token only)
# Point to /auth/token which accepts form-data per OAuth2 password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/register/patient", response_model=schemas.PatientRead)
def register_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    # Check email uniqueness across patients
    existing = db.query(models.Patient).filter(models.Patient.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient with this email already exists")

    new_patient = models.Patient(
        first_name=payload.first_name,
        last_name=payload.last_name,
        dob=payload.dob,
        phone_number=payload.phone_number,
        email=payload.email,
        address=payload.address,
        password_hash=hash_password(payload.password),
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


@router.post("/register/doctor", response_model=schemas.DoctorRead)
def register_doctor(
    payload: schemas.DoctorCreate,
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
):
    # Simple admin gate for now
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin token required")

    existing = db.query(models.Doctor).filter(models.Doctor.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor with this email already exists")

    new_doctor = models.Doctor(
        first_name=payload.first_name,
        last_name=payload.last_name,
        specialty=payload.specialty,
        phone_number=payload.phone_number,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor



@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    role = payload.role.lower()
    if role not in ("patient", "doctor", "admin"):
        raise HTTPException(status_code=400, detail="Role must be 'patient', 'doctor', or 'admin'")

    if role == "patient":
        user = db.query(models.Patient).filter(models.Patient.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.patient_id
    elif role == "doctor":
        user = db.query(models.Doctor).filter(models.Doctor.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.doctor_id
    else:
        user = db.query(models.Admin).filter(models.Admin.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.admin_id

    access_token = create_access_token({"role": role, "user_id": user_id})
    refresh_token = create_refresh_token({"role": role, "user_id": user_id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/token", response_model=schemas.Token)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 Password flow compatible endpoint for Swagger UI.
    - username: email
    - password: password
    - scope: include the word 'doctor' to login as doctor; otherwise defaults to patient
    """
    email = form_data.username
    password = form_data.password
    scopes = set((form_data.scopes or []))
    role = "admin" if "admin" in scopes else ("doctor" if "doctor" in scopes else "patient")

    if role == "patient":
        user = db.query(models.Patient).filter(models.Patient.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.patient_id
    elif role == "doctor":
        user = db.query(models.Doctor).filter(models.Doctor.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.doctor_id
    else:
        user = db.query(models.Admin).filter(models.Admin.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.admin_id

    access_token = create_access_token({"role": role, "user_id": user_id})
    refresh_token = create_refresh_token({"role": role, "user_id": user_id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(payload: schemas.RefreshRequest):
    # Validate refresh token and issue new access + refresh
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
