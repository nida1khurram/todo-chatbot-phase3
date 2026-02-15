import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up centralized logging configuration for the application
    """
    # Create a custom formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Suppress overly verbose logs from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    """
    return logging.getLogger(name)


def log_api_call(
    endpoint: str,
    method: str,
    user_id: Optional[int] = None,
    status_code: Optional[int] = None,
    response_time: Optional[float] = None
):
    """
    Log API call information
    """
    logger = get_logger("api")
    extra_info = []

    if user_id:
        extra_info.append(f"user_id={user_id}")
    if status_code:
        extra_info.append(f"status={status_code}")
    if response_time:
        extra_info.append(f"response_time={response_time:.3f}s")

    extra_info_str = f" ({', '.join(extra_info)})" if extra_info else ""
    logger.info(f"{method} {endpoint}{extra_info_str}")


def log_database_operation(operation: str, table: str, duration: Optional[float] = None):
    """
    Log database operation information
    """
    logger = get_logger("database")
    duration_str = f" (duration: {duration:.3f}s)" if duration else ""
    logger.info(f"{operation} on {table}{duration_str}")


def log_security_event(event_type: str, user_id: Optional[int] = None, ip_address: Optional[str] = None, details: str = ""):
    """
    Log security-related events
    """
    logger = get_logger("security")
    details_list = []

    if user_id:
        details_list.append(f"user_id={user_id}")
    if ip_address:
        details_list.append(f"ip={ip_address}")
    if details:
        details_list.append(details)

    details_str = f" ({', '.join(details_list)})" if details_list else ""
    logger.warning(f"Security event: {event_type}{details_str}")