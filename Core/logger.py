import logging
import os


def setup_logger():
    """
    Sets up a detailed logger for the application.
    Logs to console and file with timestamps, levels, and messages.
    """
    logger = logging.getLogger("economia_app")
    logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logging

    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("logs/app.log")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
