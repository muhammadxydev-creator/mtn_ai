"""MongoDB database connection and session management using Motor and Beanie."""

from typing import AsyncGenerator, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from fastapi import Depends, HTTPException, status

from app.core.config import settings
from app.core.logging import get_logger
from app.models import Staff

logger = get_logger("database")

# MongoDB client
mongodb_client: AsyncIOMotorClient = None


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Dependency to get MongoDB database instance.
    
    Yields:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    if mongodb_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized"
        )
    db = mongodb_client[settings.MONGODB_DB_NAME]
    try:
        logger.debug("Getting MongoDB database instance")
        yield db
    finally:
        logger.debug("Releasing MongoDB database instance")


async def get_current_project_id(current_user: Staff = Depends(lambda: None)) -> str:
    """
    Dependency to get current project ID from authenticated user.
    This is a placeholder - actual implementation depends on auth context.
    """
    if hasattr(current_user, 'project_id'):
        return str(current_user.project_id)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not authenticated or no project_id"
    )


async def init_db() -> None:
    """Initialize MongoDB connection and Beanie ODM."""
    global mongodb_client
    
    logger.info(f"Connecting to MongoDB: {settings.MONGODB_URL}")
    
    try:
        # Create MongoDB client
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info("✅ MongoDB connected successfully")
        
        # Initialize Beanie with all document models
        from app.models import (
            Visitor,
            Platform,
            PlatformTypeDefinition,
            Project,
            Staff,
            Tag,
            AIProvider,
            AIModel,
            SystemSetup,
            VisitorSession,
            VisitorActivity,
            VisitorAssignmentRule,
            VisitorWaitingQueue,
            VisitorTag,
            VisitorCustomerUpdate,
            VisitorAIProfile,
            VisitorAIInsight,
            VisitorSystemInfo,
            VisitorAssignmentHistory,
            ChatFile,
            Permission,
            ChannelMember,
            ChannelMemoryClearance,
            ProjectAIConfig,
            AIProviderDefaultModel,
            ProjectOnboardingProgress,
            StoreCredential,
        )
        
        # Get the database
        db = mongodb_client[settings.MONGODB_DB_NAME]
        
        # Initialize Beanie with all document models
        await init_beanie(
            database=db,
            document_models=[
                Visitor,
                Platform,
                PlatformTypeDefinition,
                Project,
                Staff,
                Tag,
                AIProvider,
                AIModel,
                SystemSetup,
                VisitorSession,
                VisitorActivity,
                VisitorAssignmentRule,
                VisitorWaitingQueue,
                VisitorTag,
                VisitorCustomerUpdate,
                VisitorAIProfile,
                VisitorAIInsight,
                VisitorSystemInfo,
                VisitorAssignmentHistory,
                ChatFile,
                Permission,
                ChannelMember,
                ChannelMemoryClearance,
                ProjectAIConfig,
                AIProviderDefaultModel,
                ProjectOnboardingProgress,
                StoreCredential,
            ],
        )
        
        logger.info("✅ Beanie ODM initialized successfully")
        logger.info(f"Using MongoDB database: {settings.MONGODB_DB_NAME}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_db() -> None:
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        logger.info("Closing MongoDB connection")
        mongodb_client.close()
        logger.info("✅ MongoDB connection closed")


# Database health check
async def check_db_health() -> bool:
    """
    Check MongoDB connectivity.
    
    Returns:
        bool: True if MongoDB is healthy, False otherwise
    """
    try:
        if mongodb_client is None:
            logger.error("MongoDB client not initialized")
            return False
        
        await mongodb_client.admin.command('ping')
        logger.debug("MongoDB health check passed")
        return True
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return False
