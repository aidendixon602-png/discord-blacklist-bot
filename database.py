import sqlite3
from discord import Guild, TextChannel
from typing import Optional
from logging_config import logger

conn: sqlite3.Connection = sqlite3.connect('blacklists.db')
c: sqlite3.Cursor = conn.cursor()

c.executescript('''
CREATE TABLE IF NOT EXISTS blacklists (guild_id INTEGER, user_id INTEGER, reason TEXT, PRIMARY KEY(guild_id, user_id));
CREATE TABLE IF NOT EXISTS global_blacklist (user_id INTEGER PRIMARY KEY, reason TEXT);
CREATE TABLE IF NOT EXISTS guild_settings (guild_id INTEGER PRIMARY KEY, log_channel_id INTEGER, global_enabled INTEGER DEFAULT 0);
''')
conn.commit()

logger.info("DB loaded")

def log_channel(guild: Guild) -> Optional[TextChannel]:
    row = c.execute('SELECT log_channel_id FROM guild_settings WHERE guild_id=?', (guild.id,)).fetchone()
    return guild.get_channel(row[0]) if row and row[0] else None

def global_enabled(guild: Guild) -> bool:
    row = c.execute('SELECT global_enabled FROM guild_settings WHERE guild_id=?', (guild.id,)).fetchone()
    return bool(row and row[0]) if row else False

def commit() -> None:
    conn.commit()
