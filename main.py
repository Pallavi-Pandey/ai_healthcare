from fastapi import FastAPI
from routes.auth_routes import router as auth_router
from routes.patient_routes import router as patient_router
from routes.doctor_routes import router as doctor_router
from database import Base, engine

# Create all tables on startup (simple for initial phase; consider Alembic later)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare AI Backend")


@app.on_event("startup")
def startup_event():
    from database import get_db
    from models import User
    from utils.auth import hash_password
    import os

    db = next(get_db())
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_exists = db.query(User).filter(User.email == admin_email).first()

        if not admin_exists:
            print("Creating default admin user...")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin@123")
            new_admin = User(
                first_name=os.getenv("ADMIN_FIRST_NAME", "Admin"),
                last_name=os.getenv("ADMIN_LAST_NAME", "User"),
                email=admin_email,
                password_hash=hash_password(admin_password),
                role='admin',
                specialty='Administration'
            )
            db.add(new_admin)
            db.commit()
            print(f"Default admin user '{admin_email}' created successfully.")
        else:
            print(f"Admin user '{admin_email}' already exists.")
    finally:
        db.close()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(patient_router, tags=["patients"])
app.include_router(doctor_router, tags=["doctors"])

@app.get("/")
def read_root():
    return {"message": "Healthcare AI Backend is running"}
