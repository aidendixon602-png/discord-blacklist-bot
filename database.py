"""Database setup and management."""

import sqlite3
from logging_config import logger

conn = sqlite3.connect("blacklists.db")
c = conn.cursor()

c.executescript('''
CREATE TABLE IF NOT EXISTS blacklists (
    guild_id INTEGER,
    user_id INTEGER,
    reason TEXT,
    PRIMARY KEY(guild_id, user_id)
);
CREATE TABLE IF NOT EXISTS global_blacklist (
    user_id INTEGER PRIMARY KEY,
    reason TEXT
);
CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id INTEGER PRIMARY KEY,
    log_channel_id INTEGER,
    global_enabled INTEGER DEFAULT 0,
    raid_enabled INTEGER DEFAULT 1,
    auto_kick_enabled INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS user_permissions (
    guild_id INTEGER,
    user_id INTEGER,
    permission_level INTEGER,
    PRIMARY KEY(guild_id, user_id)
);
CREATE TABLE IF NOT EXISTS permission_levels (
    level INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);
INSERT OR IGNORE INTO permission_levels (level, name) VALUES
(0, 'Helper'), (1, 'Moderator'), (2, 'Admin'), (3, 'Owner');
''')
conn.commit()
logger.info("Database ready")
