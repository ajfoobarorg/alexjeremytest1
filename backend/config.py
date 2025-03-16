# This is a new file
from typing import List
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    # Production flag
    IS_PRODUCTION = os.environ.get("IS_PRODUCTION", "false").lower() == "true"
    logger.info(f"Running in {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'} mode")

    # Get frontend URL directly from environment variable
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    logger.info(f"FRONTEND_URL set to: {FRONTEND_URL}")
    
    # Allow the frontend URL and localhost for development
    ALLOWED_ORIGINS: List[str] = [
        FRONTEND_URL,
        "http://localhost:5173",
        "https://superttt-hbr1.onrender.com"  # Always include the known frontend URL
    ]
    
    # Log allowed origins
    logger.info(f"ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")

    # Server host and port
    HOST: str = "0.0.0.0"  # Listen on all interfaces
    PORT: int = int(os.environ.get("PORT", "8000"))

config = Config() 