"""
Structured logging configuration using loguru.
Why loguru?
- Better than standard logging library
- Automatic JSON formatting
- Colored output for development
- Easy context injection
- No boilerplate configuration
"""

import sys
from pathlib import Path
from loguru import logger

logger.remove()  # Remove default logger

# Add Console handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO",
)

__all__ = ["logger"]
