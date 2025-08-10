from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# --- User Schemas ---
class UserBase(BaseModel):
    first_name: str
    last_name: str
    dob: Optional[date] = None
    phone_number: Optional[str] = None
    email: EmailStr
    address: Optional[str] = None
    specialty: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = 'patient'

class UserRead(UserBase):
    user_id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Other Schemas ---
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    status: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentRead(AppointmentBase):
    appointment_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PrescriptionBase(BaseModel):
    patient_id: int
    doctor_id: int
    medication_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionRead(PrescriptionBase):
    prescription_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReminderBase(BaseModel):
    patient_id: int
    type: str
    reference_id: Optional[int] = None
    reminder_time: datetime
    status: Optional[str] = None

class ReminderCreate(ReminderBase):
    pass

class ReminderRead(ReminderBase):
    reminder_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CallLogBase(BaseModel):
    patient_id: int
    call_type: Optional[str] = None
    call_time: datetime
    call_status: Optional[str] = None
    notes: Optional[str] = None

class CallLogCreate(CallLogBase):
    pass

class CallLogRead(CallLogBase):
    call_id: int

    class Config:
        from_attributes = True

# --- Auth Schemas ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserInfo(BaseModel):
    role: str
    user_id: int

# Patient specific schemas
class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[date] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

# Doctor specific schemas
class DoctorBase(UserBase):
    specialty: str
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    available_hours: Optional[dict] = None

class DoctorCreate(DoctorBase):
    password: str
    email: EmailStr

class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    specialty: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    available_hours: Optional[dict] = None
