import logging
import sys
from logging.handlers import RotatingFileHandler
from config import settings

def setup_logging():
    # Set log level from config
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File Handler (rotating logs, max 5MB per file, keep 3 files)
    file_handler = RotatingFileHandler(
        'backend.log',
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Root Logger Setup
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Disable some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logging.info("Logging initialized at LEVEL: %s", settings.LOG_LEVEL)

# Auto-setup on import
if __name__ == "__main__":
    setup_logging()
