import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
import sys
from typing import Any

LOG_DIR: str = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE: str = os.path.join(LOG_DIR, f"bot_{datetime.now().strftime('%Y-%m-%d')}.log")

logger: logging.Logger = logging.getLogger("BlacklistBot")
logger.setLevel(logging.INFO)
logger.handlers.clear()

console: logging.StreamHandler = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%H:%M:%S'))
logger.addHandler(console)

file: RotatingFileHandler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=7, encoding='utf-8')
file.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s'))
logger.addHandler(file)

def handle_exception(exc_type: type, exc_value: Exception, exc_traceback: Any) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        logger.info("Bot stopped")
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

logger.info("Logging ready")
