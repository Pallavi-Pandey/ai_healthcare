from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# Shared base schemas
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    dob: Optional[date] = None
    phone_number: Optional[str] = None
    email: EmailStr
    address: Optional[str] = None


class PatientCreate(PatientBase):
    password: str


class PatientRead(PatientBase):
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    specialty: Optional[str] = None
    phone_number: Optional[str] = None
    email: EmailStr


class DoctorCreate(DoctorBase):
    password: str


class DoctorRead(DoctorBase):
    doctor_id: int
    created_at: datetime

    class Config:
        from_attributes = True


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


# Auth helper schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # "patient" or "doctor"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
