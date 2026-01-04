"""Main bot entry point for BlacklistGuard."""

import discord
from discord import Intents
from discord.ext import commands

from config import TOKEN, TEST_GUILD_ID, VERSION
from logging_config import logger
from database import conn, c

intents = Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready() -> None:
    synced = await bot.tree.sync(guild=discord.Object(id=TEST_GUILD_ID) if TEST_GUILD_ID else None)
    logger.info(f"BlacklistGuard v{VERSION} online | Synced {len(synced)} commands | {len(bot.guilds)} guilds")
    print(f"🛡️ BlacklistGuard v{VERSION} is ready!")

# Attach DB to bot for easy access in cogs
bot.conn = conn
bot.cursor = c

async def load_cogs():
    await bot.load_extension("cogs.blacklist_cog")
    await bot.load_extension("cogs.global_cog")
    await bot.load_extension("cogs.settings_cog")
    await bot.load_extension("cogs.raid_cog")

bot.loop.create_task(load_cogs())
bot.run(TOKEN)
