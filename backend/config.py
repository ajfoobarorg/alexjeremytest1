# This is a new file
from typing import List
import os

class Config:
    # Production mode
    PRODUCTION: bool = os.environ.get("PRODUCTION", "false").lower() == "true"

    # Frontend URL - in development use localhost, in production get from env
    FRONTEND_URL = os.environ.get("FRONTEND_URL", 
                                "https://superttt-hbr1.onrender.com" if PRODUCTION 
                                else "http://localhost:5173")
    
    # In development, allow localhost. In production, only allow the frontend URL
    ALLOWED_ORIGINS: List[str] = (
        [FRONTEND_URL] if PRODUCTION
        else ["http://localhost:5173"]
    )

    # Server host and port - Render will provide the PORT
    HOST: str = "0.0.0.0"  # Listen on all interfaces
    PORT: int = int(os.environ.get("PORT", "8000"))

config = Config() 