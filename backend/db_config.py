import os
import logging

logger = logging.getLogger(__name__)

# Detect environment
IS_PRODUCTION = os.environ.get("IS_PRODUCTION", "false").lower() == "true"

# Set database path
if IS_PRODUCTION:
    DB_PATH = "/var/data/tictactoe.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "tictactoe.db")

logger.info(f"Running in {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'} environment")
logger.info(f"Using database at: {DB_PATH}")

# Make sure the directory exists in production
if IS_PRODUCTION and not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) 