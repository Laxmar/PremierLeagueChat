import sys
from loguru import logger

def setup_logger(level: str = "INFO") -> None:
    """
    Setup logger to output to console with specified level. 
    It's configure to work with streamlit and use loguru.
    Args:
        level: The logging level (e.g., "INFO", "DEBUG", "WARNING").
    """
    logger.remove() 
    logger.add(sys.stdout, level=level)  
