# This is a new file
from typing import List
import os
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    # Better production detection:
    # 1. Check explicit PRODUCTION env var
    # 2. Check if we're running on Render (they set this env var)
    # 3. Check hostname (not localhost)
    EXPLICIT_PRODUCTION = os.environ.get("PRODUCTION", "false").lower() == "true"
    RENDER_SERVICE = os.environ.get("RENDER", "false").lower() == "true"
    HOSTNAME = socket.gethostname()
    IS_LOCALHOST = HOSTNAME == "localhost" or HOSTNAME.startswith("127.0.0")
    
    # Production if explicitly set, running on Render, or not on localhost
    PRODUCTION = EXPLICIT_PRODUCTION or RENDER_SERVICE or not IS_LOCALHOST
    
    # Log production status with details
    logger.info(f"Production detection: EXPLICIT={EXPLICIT_PRODUCTION}, RENDER={RENDER_SERVICE}, HOSTNAME={HOSTNAME}")
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