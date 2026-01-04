"""Server-specific settings and utilities."""

from discord.ext import commands
from discord.app_commands import checks
from discord import Interaction, TextChannel

from database import c, commit
from constants import EMOJI_SUCCESS, EMOJI_GLOBAL
from logging_config import logger


class SettingsCog(commands.Cog):
    """Manages server configuration for BlacklistGuard."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.app_commands.command(name="blacklist-setlog")
    @checks.has_permissions(manage_guild=True)
    async def set_log(self, i: Interaction, channel: TextChannel) -> None:
        """Set the channel for moderation logs."""
        c.execute("INSERT OR REPLACE INTO guild_settings (guild_id, log_channel_id) VALUES (?,?)",
                  (i.guild.id, channel.id))
        commit()
        logger.info(f"Log channel set to {channel.name} in {i.guild.name}")
        await i.response.send_message(f"{EMOJI_SUCCESS} Logs → {channel.mention}")

    @commands.app_commands.command(name="blacklist-clearlog")
    @checks.has_permissions(manage_guild=True)
    async def clear_log(self, i: Interaction) -> None:
        """Disable moderation logging."""
        c.execute("UPDATE guild_settings SET log_channel_id = NULL WHERE guild_id=?", (i.guild.id,))
        commit()
        logger.info(f"Logging disabled in {i.guild.name}")
        await i.response.send_message(f"{EMOJI_SUCCESS} Logging disabled")

    @commands.app_commands.command(name="blacklist-global-enable")
    @checks.has_permissions(manage_guild=True)
    async def enable_global(self, i: Interaction) -> None:
        """Enable global blacklist protection."""
        c.execute("INSERT OR REPLACE INTO guild_settings (guild_id, global_enabled) VALUES (?,1)", (i.guild.id,))
        commit()
        logger.info(f"Global enabled in {i.guild.name}")
        await i.response.send_message(f"{EMOJI_GLOBAL} Global protection **enabled**")

    @commands.app_commands.command(name="blacklist-global-disable")
    @checks.has_permissions(manage_guild=True)
    async def disable_global(self, i: Interaction) -> None:
        """Disable global blacklist protection."""
        c.execute("UPDATE guild_settings SET global_enabled = 0 WHERE guild_id=?", (i.guild.id,))
        commit()
        logger.info(f"Global disabled in {i.guild.name}")
        await i.response.send_message(f"{EMOJI_GLOBAL} Global protection **disabled**")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SettingsCog(bot))
