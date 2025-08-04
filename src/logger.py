import structlog
import logging
from os import getenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def logger_config(process: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configures the logger for the application.
    
    :param process: The name of the process for which the logger is being configured.
    :param log_level: The logging level (default is INFO).
    :return: Configured logger instance.
    """

    # Set the logging level based on the provided log_level (environment variable or default)
    log_level = getattr(
        logging,
        getenv("LOG_LEVEL", log_level).upper(),
        logging.INFO
    )

    # Create a logger instance
    logger = structlog.get_logger(process)

    # Configure the logger
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set the logging level for the root logger
    logging.basicConfig(level=log_level, format='%(message)s')

    return logger