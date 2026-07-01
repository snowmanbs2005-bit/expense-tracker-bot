"""Хранение данных в SQLite через aiosqlite."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import aiosqlite

from .report import Expense

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    amount     REAL    NOT NULL,
    category   TEXT    NOT NULL,
    created_at TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_expenses_user ON expenses(user_id, created_at);

CREATE TABLE IF NOT EXISTS reminders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    chat_id     INTEGER NOT NULL,
    at_hour     INTEGER NOT NULL,
    at_minute   INTEGER NOT NULL,
    text        TEXT    NOT NULL,
    last_fired  TEXT
);
"""


class Database:
    """Тонкая обёртка над aiosqlite с методами предметной области."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("База данных не инициализирована. Вызовите connect().")
        return self._conn

    # ---- расходы ---------------------------------------------------------
    async def add_expense(
        self, user_id: int, amount: float, category: str,
        created_at: Optional[datetime] = None,
    ) -> None:
        created_at = created_at or datetime.now()
        await self.conn.execute(
            "INSERT INTO expenses (user_id, amount, category, created_at) "
            "VALUES (?, ?, ?, ?)",
            (user_id, amount, category, created_at.isoformat()),
        )
        await self.conn.commit()

    async def list_expenses(self, user_id: int) -> List[Expense]:
        cursor = await self.conn.execute(
            "SELECT amount, category, created_at FROM expenses WHERE user_id = ?",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [
            Expense(
                category=row["category"],
                amount=row["amount"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    # ---- напоминания -----------------------------------------------------
    async def add_reminder(
        self, user_id: int, chat_id: int, hour: int, minute: int, text: str
    ) -> None:
        await self.conn.execute(
            "INSERT INTO reminders (user_id, chat_id, at_hour, at_minute, text) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, chat_id, hour, minute, text),
        )
        await self.conn.commit()

    async def due_reminders(self, hour: int, minute: int, today: str) -> List[aiosqlite.Row]:
        """Напоминания на текущее время, ещё не сработавшие сегодня."""
        cursor = await self.conn.execute(
            "SELECT * FROM reminders "
            "WHERE at_hour = ? AND at_minute = ? "
            "AND (last_fired IS NULL OR last_fired != ?)",
            (hour, minute, today),
        )
        return list(await cursor.fetchall())

    async def mark_fired(self, reminder_id: int, today: str) -> None:
        await self.conn.execute(
            "UPDATE reminders SET last_fired = ? WHERE id = ?", (today, reminder_id)
        )
        await self.conn.commit()
