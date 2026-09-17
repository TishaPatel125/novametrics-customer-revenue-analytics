from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.v1.router import api_router
from app.models.user import User
from app.core.security import get_password_hash


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and admin user exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="Lead Analyst",
                is_superuser=True,
                role="admin",
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="Production-Grade Customer Intelligence & Revenue Analytics Platform API.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS setup for dashboard and web clients


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "api_version": "v1",
    }
