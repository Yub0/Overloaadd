# Standard Library
import sys

# Third Party
from loguru import logger


def overloaadd_logger() -> logger:
    """Initialize the logger."""
    logger.remove()
    logger.add(
        sink="overloaadd.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    logger.add(
        sink=sys.stdout,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    return logger
