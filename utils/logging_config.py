import logging
import sys
import os
from pathlib import Path

def setup_logging():
    """Setup comprehensive logging configuration"""
    
    # Fix Windows console encoding for Unicode characters
    if os.name == 'nt':  # Windows
        try:
            # Set console to UTF-8
            os.system('chcp 65001 > nul')
        except:
            pass
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "hackrx.log", encoding='utf-8')
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Create performance logger
    perf_logger = logging.getLogger("performance")
    perf_logger.setLevel(logging.INFO)
    perf_handler = logging.FileHandler(log_dir / "performance.log", encoding='utf-8')
    perf_handler.setFormatter(logging.Formatter(log_format, date_format))
    perf_logger.addHandler(perf_handler)
    
    # Create security logger
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_handler = logging.FileHandler(log_dir / "security.log", encoding='utf-8')
    security_handler.setFormatter(logging.Formatter(log_format, date_format))
    security_logger.addHandler(security_handler)
    
    logging.info("Logging configuration initialized") 