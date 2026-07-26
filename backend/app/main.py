import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import Base, SessionLocal, engine
from app.api.routes import (
    attendance,
    audit_logs,
    auth,
    dashboard,
    departments,
    employees,
    insights,
    payroll,
    leaves,
    ai_tools,
    policies,
)
from app.core.config import settings
from app.core.middleware import ProductionMiddleware
from app.services.administrator import ensure_default_administrator

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.ENVIRONMENT.lower() != "production":
        Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_default_administrator(db)
    yield


app = FastAPI(
    title="Employee Management System API", version="1.0.0", lifespan=lifespan
)

allowed_origins = [
    origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()
]
if settings.ENVIRONMENT.lower() != "production":
    allowed_origins.append("http://localhost:5173")

app.add_middleware(ProductionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=(
        r"https://employee-management-system-[a-zA-Z0-9-]+"
        r"-venkatesh721s-projects\.vercel\.app"
    ),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(attendance.router)
app.include_router(dashboard.router)
app.include_router(insights.router)
app.include_router(audit_logs.router)
app.include_router(payroll.router)
app.include_router(leaves.router)
app.include_router(ai_tools.router)
app.include_router(policies.router)


@app.get("/")
def health_check():
    return {"status": "healthy", "service": "Employee Management System API"}


@app.get("/health/ready")
def readiness_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}
