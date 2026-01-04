"""Utility functions."""

from discord import User
from typing import Optional

async def resolve_user(bot, uid: int) -> Optional[User]:
    try:
        return await bot.fetch_user(uid)
    except:
        return None
