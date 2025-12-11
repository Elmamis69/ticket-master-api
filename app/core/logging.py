import logging
import sys
from app.core.config import settings

# Configure logging format
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Set log level based on environment
log_level = logging.DEBUG if settings.DEBUG else logging.INFO

# Configure root logger
logging.basicConfig(
    level=log_level,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger instance
logger = logging.getLogger("ticket_system")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    """
    return logging.getLogger(f"ticket_system.{name}")
