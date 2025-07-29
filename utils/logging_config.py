import logging
import sys
from pathlib import Path

def setup_logging():
    """Setup comprehensive logging configuration"""
    
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
            logging.FileHandler(log_dir / "hackrx.log")
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
    perf_handler = logging.FileHandler(log_dir / "performance.log")
    perf_handler.setFormatter(logging.Formatter(log_format, date_format))
    perf_logger.addHandler(perf_handler)
    
    # Create security logger
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_handler = logging.FileHandler(log_dir / "security.log")
    security_handler.setFormatter(logging.Formatter(log_format, date_format))
    security_logger.addHandler(security_handler)
    
    logging.info("Logging configuration initialized") 