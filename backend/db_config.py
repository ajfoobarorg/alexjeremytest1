import os
import logging
from config import config

logger = logging.getLogger(__name__)

# Set database path
if config.IS_PRODUCTION:
    DB_PATH = "/var/data/tictactoe.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "tictactoe.db")

logger.info(f"Running in {'PRODUCTION' if config.IS_PRODUCTION else 'DEVELOPMENT'} environment")
logger.info(f"Using database at: {DB_PATH}")

# Make sure the directory exists in production
if config.IS_PRODUCTION and not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)