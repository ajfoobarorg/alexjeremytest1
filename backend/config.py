# This is a new file
from typing import List
import os

class Config:
    # Get the frontend URL from environment variable or use development default
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Dev server
        FRONTEND_URL,            # Production URL from environment
    ]

    # Production mode
    PRODUCTION: bool = os.environ.get("PRODUCTION", "false").lower() == "true"

    # Server host and port - Render will provide the PORT
    HOST: str = "0.0.0.0"  # Listen on all interfaces
    PORT: int = int(os.environ.get("PORT", "8000"))

config = Config() 