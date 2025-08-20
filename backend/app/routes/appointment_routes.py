from datetime import datetime, time, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.base import get_db
from app.database import models
from app.schemas import (
    AppointmentCreate, 
    AppointmentUpdate,
    AppointmentFilter,
    AppointmentAvailability
)  # Import specific schema classes
from app.utils.auth import get_current_user
from app.routes.auth_routes import oauth2_scheme  # Use absolute import

router = APIRouter(prefix="/appointments", tags=["appointments"])

# Constants for appointment scheduling
APPOINTMENT_DURATION = timedelta(minutes=30)
WORKING_HOURS_START = time(9, 0)  # 9 AM
WORKING_HOURS_END = time(17, 0)    # 5 PM

def verify_doctor_or_patient(token: str, user_id: int = None):
    """Verify if the current user is the doctor, patient, or an admin."""
    user_info = get_current_user(token, expected_type="access")
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    role, current_user_id = user_info
    
    # If user_id is provided, check if the current user is that user or an admin
    if user_id and current_user_id != user_id and role != "admin":
        # For doctors, also allow if they're the attending doctor
        if role == "doctor":
            # This check will be done in the endpoint for better error messages
            pass
        elif role != "patient" or current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource"
            )
    
    return user_info

@router.get("/", response_model=List[schemas.AppointmentRead])
async def list_appointments(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    List appointments with optional filtering.
    Patients can only see their own appointments.
    Doctors can see their own appointments and their patients' appointments.
    Admins can see all appointments.
    """
    user_info = verify_doctor_or_patient(token)
    role, current_user_id = user_info
    
    # Build the query
    query = db.query(models.Appointment)
    
    # Apply filters based on user role
    if role == "patient":
        query = query.filter(models.Appointment.patient_id == current_user_id)
    elif role == "doctor":
        query = query.filter(
            or_(
                models.Appointment.doctor_id == current_user_id,
                models.Appointment.patient_id == current_user_id
            )
        )
    # Admin can see all appointments
    
    # Apply additional filters
    if patient_id:
        query = query.filter(models.Appointment.patient_id == patient_id)
    if doctor_id:
        query = query.filter(models.Appointment.doctor_id == doctor_id)
    if status:
        query = query.filter(models.Appointment.status == status)
    if start_date:
        query = query.filter(models.Appointment.appointment_date >= start_date)
    if end_date:
        query = query.filter(models.Appointment.appointment_date <= end_date)
    
    # Execute the query
    appointments = query.offset(skip).limit(limit).all()
    return appointments

@router.get("/{appointment_id}", response_model=schemas.AppointmentRead)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get details of a specific appointment.
    Only the patient, doctor, or admin can view the appointment.
    """
    user_info = verify_doctor_or_patient(token)
    role, current_user_id = user_info
    
    appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check permissions
    if role == "patient" and appointment.patient_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this appointment"
        )
    
    if role == "doctor" and appointment.doctor_id != current_user_id:
        # Doctors can only see their own appointments or their patients'
        patient = db.query(models.User).filter(
            models.User.user_id == appointment.patient_id,
            models.User.doctor_id == current_user_id
        ).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this appointment"
            )
    
    return appointment

@router.post("/", response_model=schemas.AppointmentRead, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Create a new appointment.
    Patients can book appointments for themselves.
    """
    user_info = verify_doctor_or_patient(token, appointment.patient_id)
    role, current_user_id = user_info
    
    # Verify the doctor exists and is a doctor
    doctor = db.query(models.User).filter(
        models.User.user_id == appointment.doctor_id,
        models.User.role == "doctor"
    ).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Verify the patient exists
    patient = db.query(models.User).filter(
        models.User.user_id == appointment.patient_id,
        models.User.role == "patient"
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check for scheduling conflicts
    existing_appointment = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.status != "cancelled",
        models.Appointment.appointment_date.between(
            appointment.appointment_date - APPOINTMENT_DURATION,
            appointment.appointment_date + APPOINTMENT_DURATION
        )
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Doctor is not available at the requested time"
        )
    
    # Create the appointment
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment

@router.put("/{appointment_id}", response_model=schemas.AppointmentRead)
async def update_appointment(
    appointment_id: int,
    appointment_update: schemas.AppointmentUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Update an existing appointment.
    Only the patient, doctor, or admin can update the appointment.
    """
    user_info = verify_doctor_or_patient(token)
    role, current_user_id = user_info
    
    # Get the existing appointment
    db_appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == appointment_id
    ).first()
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check permissions
    if role == "patient" and db_appointment.patient_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this appointment"
        )
    
    if role == "doctor" and db_appointment.doctor_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this appointment"
        )
    
    # Check for scheduling conflicts if updating the appointment time
    if appointment_update.appointment_date:
        existing_appointment = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == db_appointment.doctor_id,
            models.Appointment.status != "cancelled",
            models.Appointment.appointment_id != appointment_id,  # Exclude current appointment
            models.Appointment.appointment_date.between(
                appointment_update.appointment_date - APPOINTMENT_DURATION,
                appointment_update.appointment_date + APPOINTMENT_DURATION
            )
        ).first()
        
        if existing_appointment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Doctor is not available at the requested time"
            )
    
    # Update the appointment
    update_data = appointment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)
    
    db_appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment
