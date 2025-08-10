from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
import models
import schemas
from utils.auth import hash_password, verify_password, create_access_token, get_current_user, ADMIN_TOKEN

router = APIRouter()


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
    if role not in ("patient", "doctor"):
        raise HTTPException(status_code=400, detail="Role must be 'patient' or 'doctor'")

    if role == "patient":
        user = db.query(models.Patient).filter(models.Patient.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.patient_id
    else:
        user = db.query(models.Doctor).filter(models.Doctor.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user_id = user.doctor_id

    token = create_access_token({"role": role, "user_id": user_id})
    return {"access_token": token, "token_type": "bearer"}
