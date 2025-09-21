import logging
import os
from datetime import datetime

def setup_logging(level="INFO"):
    """Configure logging for the application with support for both file and console output."""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Convert string level to logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create handlers
    handlers = [
        logging.FileHandler(
            os.path.join(log_dir, f'coding_agent_v2_{datetime.now().strftime("%Y%m%d")}.log')
        ),
        logging.StreamHandler()  # Console output
    ]
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    # Set specific log levels for different modules
    logging.getLogger('openai').setLevel(logging.WARNING)   # Reduce OpenAI API logs
    
    # Disable propagation for uvicorn logs to prevent duplicate logging
    logging.getLogger("uvicorn").propagate = False
    logging.getLogger("uvicorn.access").propagate = False
    
    # Create logger for our application
    logger = logging.getLogger('CodingAgentV2')
    logger.info("CodingAgentV2 Logging configured successfully")