"""Bot configuration."""

from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

TOKEN: str = os.getenv("DISCORD_TOKEN") or ""
if not TOKEN:
    raise ValueError("DISCORD_TOKEN missing in .env")

TEST_GUILD_ID: Optional[int] = None
VERSION: str = "1.3.0"
