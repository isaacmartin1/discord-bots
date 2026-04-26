import sqlite3
import re
from datetime import datetime, timezone
import discord

class message_db:
    def __init__(self):
        self.conn = sqlite3.connect("messages.db")

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                content TEXT,
                timestamp DATETIME
            )
        """)

        self.conn.commit()

    def save_message(self, message_id: int, user_id: int, content: str, timestamp: datetime):
        self.conn.execute(
            "INSERT OR IGNORE INTO messages (message_id, user_id, content, timestamp) VALUES (?, ?, ?, ?)",
            (message_id, user_id, content, timestamp)
        )
        self.conn.commit()

    def get_last_message_date(self, user_id: int) -> datetime:
        row = self.conn.execute(
            "SELECT timestamp FROM messages WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)
        ).fetchone()

        if row:
            return row[0]
        else:
            return None

    async def batch_retrieve_messages(self, user_id: int, channel: discord.TextChannel, message_limit: int = 10000) -> None:
        last_date = self.get_last_message_date(user_id)
        after_date = None
        if last_date:
            after_date = datetime.fromisoformat(last_date).replace(tzinfo=timezone.utc)

        async for message in channel.history(limit=message_limit, after=after_date):
            if message.author.id != user_id or message.author.bot or not message.content:
                continue
            content = re.sub(r'http\S+', '', message.content).strip()
            if not content:
                continue
            self.save_message(message.id, message.author.id, content, message.created_at)

    def get_messages(self, user_id: int) -> list[str]:
        rows = self.conn.execute(
            "SELECT content from messages where user_id = ?", (user_id,)
        ).fetchall()

        return [row[0] for row in rows]

