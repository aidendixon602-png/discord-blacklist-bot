from discord import Embed, Guild, User
from datetime import datetime
from typing import Optional
from database import log_channel
from logging_config import logger

async def resolve_user(bot: "discord.Client", uid: int) -> Optional[User]:
    try:
        return await bot.fetch_user(uid)
    except Exception:
        logger.debug(f"User {uid} not resolvable")
        return None

async def send_log(guild: Guild, embed: Embed) -> None:
    if ch := log_channel(guild):
        try:
            await ch.send(embed=embed)
        except Exception as e:
            logger.error(f"Log send failed in {guild.name}: {e}")
