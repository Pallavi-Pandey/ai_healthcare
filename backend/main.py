from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.base import init_db
from app.routes import auth_routes, appointment_routes, doctor_routes, patient_routes

app = FastAPI(title="AI Healthcare API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    await init_db()

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(patient_routes.router, prefix="/api/patients", tags=["Patients"])
app.include_router(doctor_routes.router, prefix="/api/doctors", tags=["Doctors"])
app.include_router(appointment_routes.router, prefix="/api/appointments", tags=["Appointments"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
