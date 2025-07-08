"""
Logging configuration for the Source Manager application.
"""
import logging
import logging.handlers
from pathlib import Path
# We only import the LOGS_DIR path, which is a core path setting.
from config.app_config import LOGS_DIR

# --- Logging constants are now defined HERE, not in app_config.py ---
LOG_LEVEL = "DEBUG"  # Set the default logging level (e.g., "DEBUG", "INFO", "WARNING")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logging():
    """
    Sets up application-wide logging. This should be called once
    at the very beginning of the application's execution.
    """
    # Ensure the logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Avoid adding handlers multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Create a standard formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # --- Console Handler ---
    # Logs INFO level and above to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # --- Rotating File Handler (for all logs) ---
    # Logs all DEBUG level and above messages to a rotating file
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "source_manager.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # --- Error File Handler ---
    # Specifically logs ERROR level and above to its own file
    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    logging.info("Logging configured successfully.")

