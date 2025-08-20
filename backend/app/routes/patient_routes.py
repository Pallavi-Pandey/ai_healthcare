from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.database import models
from app.schemas import UserRead, PatientUpdate  # Import specific schema classes
from app.utils.auth import get_current_user
from app.routes.auth_routes import oauth2_scheme  # Use absolute import

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/{patient_id}", response_model=schemas.UserRead)
async def get_patient_profile(
    patient_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get patient profile by ID.
    Only the patient themselves or an admin can view the profile.
    """
    # Get current user info
    current_user_info = get_current_user(token, expected_type="access")
    if not current_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    current_user_role, current_user_id = current_user_info
    
    # Check if the current user is the patient or an admin
    if current_user_role not in ["admin", "patient"] or \
       (current_user_role == "patient" and current_user_id != patient_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this patient's profile"
        )
    
    # Get the patient
    patient = db.query(models.User).filter(
        models.User.user_id == patient_id,
        models.User.role == "patient"
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return patient

@router.put("/{patient_id}", response_model=schemas.UserRead)
async def update_patient_profile(
    patient_id: int,
    patient_data: schemas.PatientUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update patient profile.
    Only the patient themselves can update their profile.
    """
    # Get current user info
    current_user_info = get_current_user(token, expected_type="access")
    if not current_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    current_user_role, current_user_id = current_user_info
    
    # Check if the current user is the patient
    if current_user_role != "patient" or current_user_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this patient's profile"
        )
    
    # Get the patient
    patient = db.query(models.User).filter(
        models.User.user_id == patient_id,
        models.User.role == "patient"
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Update patient data
    update_data = patient_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient_account(
    patient_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Delete patient account.
    Only the patient themselves can delete their account.
    """
    # Get current user info
    current_user_info = get_current_user(token, expected_type="access")
    if not current_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    current_user_role, current_user_id = current_user_info
    
    # Check if the current user is the patient
    if current_user_role != "patient" or current_user_id != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this account"
        )
    
    # Get the patient
    patient = db.query(models.User).filter(
        models.User.user_id == patient_id,
        models.User.role == "patient"
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Delete the patient
    db.delete(patient)
    db.commit()
    
    return None
