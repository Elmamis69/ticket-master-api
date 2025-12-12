from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import get_logger
from app.db.influxdb import influx_db

logger = get_logger("main")

# Create FastAPI application
app = FastAPI(
    title="Ticket System API",
    description="Sistema de gestión de tickets similar a Cherwell/Service Desk",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.
    """
    logger.info("Starting Ticket System API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Connect to InfluxDB
    try:
        influx_db.connect()
    except Exception as e:
        logger.error(f"Failed to connect to InfluxDB: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.
    """
    logger.info("Shutting down Ticket System API...")
    influx_db.close()


@app.get("/")
async def root():
    """
    Root endpoint for health check.
    """
    return {
        "message": "Ticket System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


# Include API routers
from app.api.v1 import routes_auth

app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# TODO: Uncomment when implemented
from app.api.v1 import routes_tickets, routes_comments, routes_analytics
app.include_router(routes_tickets.router, prefix="/api/v1", tags=["Tickets"])
app.include_router(routes_comments.router, prefix="/api/v1", tags=["Comments"])
app.include_router(routes_analytics.router, prefix="/api/v1", tags=["Analytics"])