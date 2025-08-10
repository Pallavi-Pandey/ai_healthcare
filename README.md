# ai_healthcare


Here’s a full list of required API endpoints for your Healthcare – AI Appointment Scheduler project, grouped by functionality so it’s easy to implement.

📌 API Endpoints
1. Authentication & User Management
Method	Endpoint	Description
POST	/auth/register	Register a new patient account
POST	/auth/login	Patient login and JWT token generation
POST	/auth/logout	Logout user (invalidate token)
GET	/patients/{patient_id}	Get patient profile details
PUT	/patients/{patient_id}	Update patient profile
DELETE	/patients/{patient_id}	Delete patient account

2. Doctor Management
Method	Endpoint	Description
GET	/doctors	List all doctors
GET	/doctors/{doctor_id}	Get doctor details
POST	/doctors	Add a new doctor (admin only)
PUT	/doctors/{doctor_id}	Update doctor details (admin)
DELETE	/doctors/{doctor_id}	Delete doctor (admin)

3. Appointment Scheduling
Method	Endpoint	Description
GET	/appointments	List all appointments (filter by patient or doctor)
GET	/appointments/{appointment_id}	Get appointment details
POST	/appointments	Book a new appointment
PUT	/appointments/{appointment_id}	Update appointment date/status
DELETE	/appointments/{appointment_id}	Cancel appointment
GET	/appointments/availability/{doctor_id}	Get doctor’s available slots

4. Prescription Management
Method	Endpoint	Description
GET	/prescriptions	List prescriptions (filter by patient)
GET	/prescriptions/{prescription_id}	Get prescription details
POST	/prescriptions	Add new prescription (doctor/admin)
PUT	/prescriptions/{prescription_id}	Update prescription
DELETE	/prescriptions/{prescription_id}	Delete prescription

5. Medication Reminders
Method	Endpoint	Description
GET	/reminders	List all reminders for a patient
POST	/reminders	Create a new reminder (appointment or medication)
PUT	/reminders/{reminder_id}	Update reminder time/status
DELETE	/reminders/{reminder_id}	Delete reminder

6. AI Voice Call Integration
Method	Endpoint	Description
POST	/ai-call/schedule	AI call to schedule appointment
POST	/ai-call/reminder	AI call to remind patient of appointment or medication
POST	/ai-call/prescription	AI call to handle prescription refill
GET	/call-logs	List all AI call logs
GET	/call-logs/{call_id}	Get specific AI call log

7. Notifications & Messaging
Method	Endpoint	Description
POST	/notifications/send	Send SMS/WhatsApp/Email notification
GET	/notifications/{patient_id}	View notification history for a patient

8. Analytics & Reports (optional for admin dashboard)
Method	Endpoint	Description
GET	/analytics/appointments	Get appointment statistics
GET	/analytics/reminders	Get reminder success/missed rates
GET	/analytics/medication-adherence	Track medication adherence rates
