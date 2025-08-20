import os
from database import Base, engine, get_db
from models import User
from utils.auth import hash_password

def reset_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    # Create the default admin user
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

if __name__ == "__main__":
    reset_database()
