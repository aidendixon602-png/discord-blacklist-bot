from discord import app_commands, Interaction, File
from discord.app_commands import checks, Choice
from discord import Guild
from typing import List, Dict, Any
from database import c, global_enabled
from utils import resolve_user
from logging_config import logger
from datetime import datetime
import csv
import json
from io import StringIO, BytesIO

@app_commands.command(name="blacklist-export")
@checks.has_permissions(ban_members=True)
@app_commands.choices(format=[
    Choice(name="CSV", value="csv"),
    Choice(name="JSON", value="json")
])
async def blacklist_export(
    i: Interaction,
    include_global: bool = False,
    format: str = "csv"
) -> None:
    if include_global and not i.user.guild_permissions.administrator:
        return await i.response.send_message("Admin required for global.", ephemeral=True)
    if include_global and not global_enabled(i.guild):
        return await i.response.send_message("Global not enabled.", ephemeral=True)

    await i.response.defer()

    entries: List[Dict[str, Any]] = []

    for uid, reason in c.execute('SELECT user_id, reason FROM blacklists WHERE guild_id=?', (i.guild.id,)):
        user = await resolve_user(i.client, uid)
        entries.append({
            "user_id": str(uid),
            "username": str(user) if user else None,
            "reason": reason or None,
            "scope": "local"
        })

    if include_global:
        local_ids: set[str] = {e["user_id"] for e in entries}
        for uid, reason in c.execute('SELECT user_id, reason FROM global_blacklist'):
            if str(uid) not in local_ids:
                user = await resolve_user(i.client, uid)
                entries.append({
                    "user_id": str(uid),
                    "username": str(user) if user else None,
                    "reason": reason or None,
                    "scope": "global"
                })

    if not entries:
        return await i.followup.send("Blacklist empty.")

    ts: str = datetime.now().strftime('%Y-%m-%d_%H-%M')
    name: str = i.guild.name.replace(' ', '_')

    if format == "json":
        data: bytes = json.dumps(entries, indent=2, ensure_ascii=False).encode('utf-8')
        file: File = File(BytesIO(data), f"blacklist_{name}_{ts}{'_global' if include_global else ''}.json")
    else:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["user_id", "username", "reason", "scope"])
        for e in entries:
            writer.writerow([e["user_id"], e["username"] or "Unknown", e["reason"] or "", e["scope"]])
        file = File(BytesIO(output.getvalue().encode('utf-8')), f"blacklist_{name}_{ts}{'_global' if include_global else ''}.csv")

    logger.info(f"Export {format.upper()} | {len(entries)} entries | By {i.user}")
    await i.followup.send(f"Exported {len(entries)} entries ({format.upper()})", file=file)
