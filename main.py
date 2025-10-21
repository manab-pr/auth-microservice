"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

from config import settings
from auth.container import Container
from auth.presentation.http.handlers import auth_router
from auth.presentation.http import dependencies
from logging_config import setup_logging, get_logger

# Setup logging
setup_logging(log_level="DEBUG" if settings.debug else "INFO")
logger = get_logger(__name__)


# Global clients
mongodb_client = None
redis_client = None
container = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    global mongodb_client, redis_client, container

    logger.info("🚀 Starting application...")

    try:
        # Initialize MongoDB
        logger.info("📦 Connecting to MongoDB...")
        mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        mongodb_database = mongodb_client[settings.mongodb_database]
        logger.info(f"Connected to MongoDB database: {settings.mongodb_database}")

        # Initialize Redis
        logger.info("📦 Connecting to Redis...")
        redis_client = redis.from_url(settings.redis_url, decode_responses=False)
        await redis_client.ping()  # Test connection
        logger.info("Connected to Redis successfully")

        # Initialize container
        logger.info("🔧 Initializing dependency injection container...")
        container = Container(
            mongodb_database=mongodb_database,
            redis_client=redis_client,
            jwt_secret_key=settings.jwt_secret_key,
            jwt_algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.access_token_expire_minutes,
            refresh_token_expire_days=settings.refresh_token_expire_days,
        )

        # Set container in dependencies
        dependencies.set_container(container)

        logger.info("✅ Application started successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down application...")

    if mongodb_client:
        mongodb_client.close()
        logger.info("📦 MongoDB connection closed")

    if redis_client:
        await redis_client.close()
        logger.info("📦 Redis connection closed")

    logger.info("✅ Application shut down successfully!")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Authentication service built with clean architecture",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(auth_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FastAPI Auth Service",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
