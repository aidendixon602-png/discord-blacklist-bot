"""Global (cross-server) blacklist management."""

from discord.ext import commands
from discord.app_commands import checks
from discord import Interaction

from core.blacklist_manager import BlacklistManager
from views import Confirm
from utils import resolve_user
from constants import EMOJI_GLOBAL
from logging_config import logger


class GlobalCog(commands.Cog):
    """Handles shared global blacklist operations (admin only)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _initiate_global_action(
        self,
        i: Interaction,
        user_id: str,
        action: str,
        reason: str
    ) -> None:
        if not user_id.isdigit():
            return await i.response.send_message("❌ Invalid user ID.", ephemeral=True)

        uid = int(user_id)
        user = await resolve_user(self.bot, uid)
        tag = str(user) if user else f"`{uid}`"

        logger.info(f"Global blacklist {action} | User: {uid} ({tag}) | Admin: {i.user.id}")

        view = Confirm(
            uid=uid,
            action=action,
            mod=i.user,
            global_scope=True,
            reason=reason
        )
        await i.response.send_message(
            f"{EMOJI_GLOBAL} **GLOBAL**: {action.capitalize()} **{tag}** from the shared blacklist?\n"
            f"**Reason:** {reason}",
            view=view
        )

    @commands.app_commands.command(name="blacklist-global-add")
    @checks.has_permissions(administrator=True)
    async def add_global(self, i: Interaction, user_id: str, reason: str) -> None:
        """Add a user to the global blacklist (affects all enabled servers)."""
        await self._initiate_global_action(i, user_id, "add", reason)

    @commands.app_commands.command(name="blacklist-global-remove")
    @checks.has_permissions(administrator=True)
    async def remove_global(self, i: Interaction, user_id: str) -> None:
        """Remove a user from the global blacklist."""
        await self._initiate_global_action(i, user_id, "remove", "Removed from global")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GlobalCog(bot))
