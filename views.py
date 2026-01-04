"""Confirmation view."""

from discord.ui import View, button
from discord import ButtonStyle, Interaction, Embed, User
from datetime import datetime
from typing import Optional

from database import c, conn
from utils import resolve_user
from constants import COLOR_SUCCESS, COLOR_ERROR
from logging_config import logger

class Confirm(View):
    def __init__(self, uid: int, action: str, mod: User, global_scope: bool, reason: str = "No reason provided"):
        super().__init__(timeout=60)
        self.uid = uid
        self.action = action
        self.mod = mod
        self.global = global_scope
        self.reason = reason

    async def interaction_check(self, i: Interaction) -> bool:
        return i.user == self.mod or i.user.guild_permissions.administrator

    async def finish(self, i: Interaction, msg: str) -> None:
        for child in self.children:
            child.disabled = True
        await i.response.edit_message(content=msg, view=self)

    async def _send_log(self, i: Interaction, user: Optional[User], title: str, color: int) -> None:
        tag = str(user) if user else f"`{self.uid}`"
        embed = Embed(title=title, color=color, timestamp=datetime.utcnow())
        embed.add_field(name="User", value=f"<@{self.uid}>\n{tag}", inline=False)
        embed.add_field(name="Moderator", value=self.mod.mention, inline=False)
        embed.add_field(name="Scope", value="Global 🌐" if self.global else "Local", inline=False)
        embed.add_field(name="Reason", value=self.reason, inline=False)
        embed.set_footer(text=f"User ID: {self.uid}")
        if user and user.display_avatar:
            embed.set_thumbnail(url=user.display_avatar.url)

        row = i.client.cursor.execute("SELECT log_channel_id FROM guild_settings WHERE guild_id=?", (i.guild.id,)).fetchone()
        if row and row[0]:
            channel = i.guild.get_channel(row[0])
            if channel:
                await channel.send(embed=embed)

    @button(label="Confirm", style=ButtonStyle.danger, emoji="✅")
    async def confirm(self, i: Interaction, _) -> None:
        user = await resolve_user(i.client, self.uid)
        tag = str(user) if user else f"`{self.uid}`"

        cursor = i.client.cursor
        conn = i.client.conn

        if self.action == "add":
            if self.global:
                cursor.execute("INSERT OR REPLACE INTO global_blacklist (user_id, reason) VALUES (?,?)", (self.uid, self.reason))
                title = "🌐 Global Blacklisted"
                color = 0xE67E22
            else:
                cursor.execute("INSERT OR REPLACE INTO blacklists (guild_id, user_id, reason) VALUES (?,?,?)",
                               (i.guild.id, self.uid, self.reason))
                title = "🚫 Blacklisted"
                color = 0xE67E22
            msg = f"✅ **{tag}** added."
        else:
            if self.global:
                cursor.execute("DELETE FROM global_blacklist WHERE user_id=?", (self.uid,))
                title = "🌐 Global Unblacklisted"
            else:
                cursor.execute("DELETE FROM blacklists WHERE guild_id=? AND user_id=?", (i.guild.id, self.uid))
                title = "✅ Unblacklisted"
            removed = cursor.rowcount > 0
            color = COLOR_SUCCESS if removed else COLOR_ERROR
            msg = f"✅ **{tag}** removed." if removed else "ℹ️ Not blacklisted."

        conn.commit()
        await self.finish(i, f"{msg}\n**Reason:** {self.reason}")
        await self._send_log(i, user, title, color)

    @button(label="Cancel", style=ButtonStyle.secondary, emoji="❌")
    async def cancel(self, i: Interaction, _) -> None:
        user = await resolve_user(i.client, self.uid)
        tag = str(user) if user else f"`{self.uid}`"
        await self.finish(i, f"❌ Cancelled for **{tag}**.")
