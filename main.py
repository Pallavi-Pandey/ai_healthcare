from fastapi import FastAPI
from routes.auth_routes import router as auth_router
from database import Base, engine

# Create all tables on startup (simple for initial phase; consider Alembic later)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare AI Backend")


@app.on_event("startup")
def startup_event():
    from database import get_db
    from models import Admin
    from utils.auth import hash_password
    import os

    db = next(get_db())
    try:
                # Use hardcoded credentials for the admin user
        admin_email = os.getenv("ADMIN_EMAIL", "admin")
        if not admin_email:
            print("ADMIN_EMAIL not set, skipping admin creation.")
            return

        admin_exists = db.query(Admin).filter(Admin.email == admin_email).first()
        if not admin_exists:
            print("Creating default admin user...")
            admin_password = os.getenv("ADMIN_PASSWORD")
            if not admin_password:
                raise ValueError("ADMIN_PASSWORD must be set to create default admin")

            new_admin = Admin(
                first_name=os.getenv("ADMIN_FIRST_NAME", "Admin"),
                last_name=os.getenv("ADMIN_LAST_NAME", "User"),
                phone_number=os.getenv("ADMIN_PHONE_NUMBER", "0000000000"),
                email=admin_email,
                password_hash=hash_password(admin_password),
            )
            db.add(new_admin)
            db.commit()
            print(f"Default admin user '{admin_email}' created successfully.")
        else:
            print(f"Admin user '{admin_email}' already exists.")
    finally:
        db.close()

app.include_router(auth_router, prefix="/auth", tags=["auth"]) 


@app.get("/")
def read_root():
    return {"message": "Healthcare AI Backend is running"}
