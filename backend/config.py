# This is a new file
from typing import List
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    # Production mode
    PRODUCTION: bool = os.environ.get("PRODUCTION", "false").lower() == "true"
    
    # Log production status
    logger.info(f"Running in {'PRODUCTION' if PRODUCTION else 'DEVELOPMENT'} mode")

    # Frontend URL - in development use localhost, in production get from env
    FRONTEND_URL = os.environ.get("FRONTEND_URL", 
                                "https://superttt-hbr1.onrender.com" if PRODUCTION 
                                else "http://localhost:5173")
    
    # Log frontend URL
    logger.info(f"FRONTEND_URL set to: {FRONTEND_URL}")
    
    # In development, allow localhost. In production, only allow the frontend URL
    ALLOWED_ORIGINS: List[str] = (
        [FRONTEND_URL] if PRODUCTION
        else ["http://localhost:5173"]
    )
    
    # Log allowed origins before adding additional ones
    logger.info(f"Initial ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")

    # Server host and port - Render will provide the PORT
    HOST: str = "0.0.0.0"  # Listen on all interfaces
    PORT: int = int(os.environ.get("PORT", "8000"))

    # Always add the frontend domain explicitly to be sure
    if "https://superttt-hbr1.onrender.com" not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append("https://superttt-hbr1.onrender.com")
    
    # Log final allowed origins
    logger.info(f"Final ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")

config = Config() 