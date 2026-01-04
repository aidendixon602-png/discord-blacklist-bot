"""Logging configuration."""

import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)
LOG_FILE = f"logs/bot_{datetime.now():%Y-%m-%d}.log"

logger = logging.getLogger("BlacklistGuard")
logger.setLevel(logging.INFO)
logger.handlers.clear()

console = logging.StreamHandler()
console.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S"))
logger.addHandler(console)

file = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=7, encoding="utf-8")
file.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
logger.addHandler(file)

logger.info("Logging ready")
