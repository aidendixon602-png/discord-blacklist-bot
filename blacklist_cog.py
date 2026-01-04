"""Local blacklist management commands."""

from discord.ext import commands
from discord.app_commands import checks
from discord import Interaction

from core.blacklist_manager import BlacklistManager
from views import Confirm
from utils import resolve_user
from constants import EMOJI_SUCCESS, EMOJI_WARNING
from logging_config import logger


class BlacklistCog(commands.Cog):
    """Handles per-server (local) blacklist operations."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _initiate_action(
        self,
        i: Interaction,
        user_id: str,
        action: str,  # "add" or "remove"
        reason: str = "No reason provided"
    ) -> None:
        if not user_id.isdigit():
            return await i.response.send_message(f"{EMOJI_WARNING} Invalid user ID.", ephemeral=True)

        uid = int(user_id)
        user = await resolve_user(self.bot, uid)
        tag = str(user) if user else f"`{uid}`"

        logger.info(f"Local blacklist {action} | User: {uid} ({tag}) | Mod: {i.user.id}")

        view = Confirm(
            uid=uid,
            action=action,
            mod=i.user,
            global_scope=False,
            reason=reason
        )
        await i.response.send_message(
            f"{EMOJI_WARNING} **Local**: {action.capitalize()} **{tag}** from this server?\n"
            f"**Reason:** {reason}",
            view=view
        )

    @commands.app_commands.command(name="blacklist-add")
    @checks.has_permissions(ban_members=True)
    async def add_local(
        self,
        i: Interaction,
        user_id: str,
        reason: str = "No reason provided"
    ) -> None:
        """Add a user to the local server blacklist."""
        await self._initiate_action(i, user_id, "add", reason)

    @commands.app_commands.command(name="blacklist-remove")
    @checks.has_permissions(ban_members=True)
    async def remove_local(self, i: Interaction, user_id: str) -> None:
        """Remove a user from the local server blacklist."""
        await self._initiate_action(i, user_id, "remove")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BlacklistCog(bot))
