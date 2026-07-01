"""Фоновый планировщик напоминаний.

Раз в минуту проверяет напоминания, чьё время совпало с текущим, и
отправляет сообщение в чат. Каждое напоминание срабатывает раз в сутки.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from aiogram import Bot

from .db import Database

logger = logging.getLogger(__name__)


async def reminder_loop(bot: Bot, db: Database, poll_seconds: int = 30) -> None:
    """Бесконечный цикл проверки напоминаний. Запускается как фоновая задача."""
    while True:
        try:
            now = datetime.now()
            today = now.date().isoformat()
            due = await db.due_reminders(now.hour, now.minute, today)
            for row in due:
                try:
                    await bot.send_message(row["chat_id"], f"⏰ Напоминание: {row['text']}")
                    await db.mark_fired(row["id"], today)
                except Exception:  # pragma: no cover - сетевые сбои
                    logger.exception("Не удалось отправить напоминание id=%s", row["id"])
        except asyncio.CancelledError:  # pragma: no cover
            raise
        except Exception:  # pragma: no cover
            logger.exception("Ошибка в цикле напоминаний")
        await asyncio.sleep(poll_seconds)
