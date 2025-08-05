import logging
import os

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger with the specified name.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        numeric_level = getattr(logging, log_level, logging.INFO)

        logger.setLevel(numeric_level)
        logger.propagate = False

        handler = logging.StreamHandler()
        handler.setLevel(numeric_level)

        formatter = logging.Formatter(
            "%(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
