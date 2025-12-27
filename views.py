from discord.ui import View, button
from discord import ButtonStyle, Interaction, User
from typing import Optional
from database import c, conn, commit
from utils import resolve_user, send_log
from discord import Embed
from datetime import datetime
from logging_config import logger

class Confirm(View):
    def __init__(self, uid: int, action: str, mod: User, global_scope: bool, reason: str = "No reason provided") -> None:
        super().__init__(timeout=60)
        self.uid: int = uid
        self.action: str = action
        self.mod: User = mod
        self.global: bool = global_scope
        self.reason: str = reason

    async def interaction_check(self, i: Interaction) -> bool:
        return i.user == self.mod or (
            i.user.guild_permissions.administrator if self.global else i.user.guild_permissions.ban_members
        )

    async def finish(self, i: Interaction, msg: str) -> None:
        for child in self.children:
            child.disabled = True  # type: ignore
        await i.response.edit_message(content=msg, view=self)

    @button(label='Confirm', style=ButtonStyle.danger, emoji='✅')
    async def confirm(self, i: Interaction, _: button) -> None:
        user: Optional[User] = await resolve_user(i.client, self.uid)
        tag: str = str(user) if user else f"`{self.uid}`"
        scope: str = "global" if self.global else "local"

        table: str = "global_blacklist" if self.global else "blacklists"
        if self.action == 'add':
            params = (self.uid, self.reason) if self.global else (i.guild.id, self.uid, self.reason)
            c.execute(f'INSERT OR REPLACE INTO {table} ({"user_id, reason" if self.global else "guild_id, user_id, reason"}) VALUES ({",".join("?" * len(params))})', params)
            title, color = ('🌍 Global Blacklisted', 0xFF8800) if self.global else ('🔨 Blacklisted', 0xFF8800)
            msg = f'✅ {tag} added.'
        else:
            params = (self.uid,) if self.global else (i.guild.id, self.uid)
            c.execute(f'DELETE FROM {table} WHERE {"user_id=?" if self.global else "guild_id=? AND user_id=?"}', params)
            removed: bool = conn.total_changes > 0
            title, color = ('🌍 Global Unblacklisted', 0x00FF00) if self.global else ('✅ Unblacklisted', 0x00FF00 if removed else 0xAAAAAA)
            msg = f'✅ {tag} removed.' if removed else f'ℹ️ Not blacklisted.'

        commit()
        await self.finish(i, f"{msg}\n**Reason:** {self.reason}")

        logger.info(f"{'Global' if self.global else 'Local'} {self.action} | User {self.uid} | Mod {self.mod}")

        embed = Embed(title=title, color=color, timestamp=datetime.utcnow())
        embed.add_field(name="User", value=f"<@{self.uid}>\n{tag}", inline=False)
        embed.add_field(name="Moderator", value=self.mod.mention, inline=False)
        embed.add_field(name="Scope", value='Global 🌍' if self.global else 'Local', inline=False)
        embed.add_field(name="Reason", value=self.reason, inline=False)
        embed.set_footer(text=f"User ID: {self.uid}")
        if user and user.display_avatar:
            embed.set_thumbnail(url=user.display_avatar.url)
        await send_log(i.guild, embed)

    @button(label='Cancel', style=ButtonStyle.grey, emoji='❌')
    async def cancel(self, i: Interaction, _: button) -> None:
        user: Optional[User] = await resolve_user(i.client, self.uid)
        tag: str = str(user) if user else f"`{self.uid}`"
        await self.finish(i, f'❌ Cancelled: {tag}')
        logger.info(f"Cancel by {i.user} for {self.uid}")
