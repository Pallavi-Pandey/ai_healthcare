from fastapi import FastAPI
from routes.auth_routes import router as auth_router
from database import Base, engine

# Create all tables on startup (simple for initial phase; consider Alembic later)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare AI Backend")

app.include_router(auth_router, prefix="/auth", tags=["auth"]) 


@app.get("/")
def read_root():
    return {"message": "Healthcare AI Backend is running"}
