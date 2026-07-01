"""Точка входа: инициализация бота, БД и планировщика напоминаний."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import Config, ConfigError
from .db import Database
from .handlers import build_router
from .reminders import reminder_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("expense-tracker-bot")


async def run() -> None:
    config = Config.from_env()

    db = Database(config.db_path)
    await db.connect()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(build_router(db))

    reminders_task = asyncio.create_task(reminder_loop(bot, db))
    logger.info("Бот запущен. Ожидание сообщений…")
    try:
        await dp.start_polling(bot)
    finally:
        reminders_task.cancel()
        await db.close()
        await bot.session.close()


def main() -> None:
    try:
        asyncio.run(run())
    except ConfigError as exc:
        raise SystemExit(str(exc))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановлено.")


if __name__ == "__main__":
    main()
