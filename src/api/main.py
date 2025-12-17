"""
Patient Appointment System - Main API
High-performance scheduling for healthcare providers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from src.api.routes import providers, appointments, patients, availability, waitlist
from src.utils.config import settings

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Patient Appointment System")
    yield
    logger.info("Shutting down Patient Appointment System")


app = FastAPI(
    title="Patient Appointment System",
    description="High-performance appointment scheduling for healthcare",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(providers.router, prefix="/providers", tags=["Providers"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(availability.router, prefix="/availability", tags=["Availability"])
app.include_router(waitlist.router, prefix="/waitlist", tags=["Waitlist"])


@app.get("/")
async def root():
    return {
        "service": "Patient Appointment System",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
