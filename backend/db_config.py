import os
import logging
import sqlite3
from config import config
from datetime import datetime

logger = logging.getLogger(__name__)

# Custom datetime adapter for SQLite
def adapt_datetime(dt: datetime) -> str:
    return dt.isoformat()

def convert_datetime(s: bytes) -> datetime:
    return datetime.fromisoformat(s.decode())

# Register the adapters
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

# Environment setup
ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEVELOPMENT')
logger.info(f"Running in {ENVIRONMENT} environment")

if ENVIRONMENT == 'DEVELOPMENT':
    DB_PATH = os.path.join(os.path.dirname(__file__), 'tictactoe.db')
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'prod_tictactoe.db')

logger.info(f"Using database at: {DB_PATH}")

# Make sure the directory exists in production
if config.IS_PRODUCTION and not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)