from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.database import models
from app.schemas import (
    DoctorCreate,
    DoctorUpdate,
    UserRead
)  # Import specific schema classes
from app.utils.auth import get_current_user, ADMIN_TOKEN, hash_password
from app.routes.auth_routes import oauth2_scheme  # Use absolute import

router = APIRouter(prefix="/doctors", tags=["doctors"])

def verify_admin(token: str = Depends(oauth2_scheme)):
    """Verify if the current user is an admin."""
    user_info = get_current_user(token, expected_type="access")
    if not user_info or user_info[0] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return user_info

@router.get("/", response_model=List[schemas.UserRead])
async def list_doctors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all doctors with pagination.
    """
    doctors = db.query(models.User).filter(
        models.User.role == "doctor"
    ).offset(skip).limit(limit).all()
    return doctors

@router.get("/{doctor_id}", response_model=schemas.UserRead)
async def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific doctor.
    """
    doctor = db.query(models.User).filter(
        models.User.user_id == doctor_id,
        models.User.role == "doctor"
    ).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    return doctor

@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor: schemas.DoctorCreate,
    db: Session = Depends(get_db),
    _: tuple = Depends(verify_admin)
):
    """
    Create a new doctor (admin only).
    """
    # Check if email already exists
    existing_user = db.query(models.User).filter(
        models.User.email == doctor.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new doctor
    db_doctor = models.User(
        **doctor.dict(exclude={"password"}),
        password_hash=hash_password(doctor.password),
        role="doctor"
    )
    
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    
    return db_doctor

@router.put("/{doctor_id}", response_model=schemas.UserRead)
async def update_doctor(
    doctor_id: int,
    doctor_update: schemas.DoctorUpdate,
    db: Session = Depends(get_db),
    _: tuple = Depends(verify_admin)
):
    """
    Update doctor details (admin only).
    """
    # Get the doctor
    db_doctor = db.query(models.User).filter(
        models.User.user_id == doctor_id,
        models.User.role == "doctor"
    ).first()
    
    if not db_doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Update doctor data
    update_data = doctor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_doctor, field, value)
    
    db.commit()
    db.refresh(db_doctor)
    
    return db_doctor

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: tuple = Depends(verify_admin)
):
    """
    Delete a doctor (admin only).
    """
    # Get the doctor
    db_doctor = db.query(models.User).filter(
        models.User.user_id == doctor_id,
        models.User.role == "doctor"
    ).first()
    
    if not db_doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Delete the doctor
    db.delete(db_doctor)
    db.commit()
    
    return None
