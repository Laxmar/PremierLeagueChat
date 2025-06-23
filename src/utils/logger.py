from pathlib import Path
import sys

from loguru import logger

def setup_logger(level: str = "INFO", file_path: Path | None = None) -> None:
    """
    Setup logger to output to console with specified level. 
    It's configure to work with streamlit and use loguru.
    Args:
        level: The logging level (e.g., "INFO", "DEBUG", "WARNING").
        file_path: The path to the log file. If None, logging to file is disabled.
    """
    logger.remove() 
    logger.add(sys.stdout, level=level.upper())
    if file_path:
        file_path.parent.mkdir(exist_ok=True)
        logger.add(file_path, level=level.upper())
