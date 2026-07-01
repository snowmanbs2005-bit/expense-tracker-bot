"""Конфигурация приложения: читается из переменных окружения / .env."""
from __future__ import annotations

import os
from dataclasses import dataclass

try:
    # Необязательная зависимость: подхватываем .env, если он есть.
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:  # pragma: no cover - dotenv может быть не установлен
    pass


class ConfigError(RuntimeError):
    """Ошибка конфигурации (например, не задан токен)."""


@dataclass(frozen=True)
class Config:
    bot_token: str
    db_path: str = "expenses.db"

    @classmethod
    def from_env(cls) -> "Config":
        token = os.environ.get("BOT_TOKEN", "").strip()
        if not token:
            raise ConfigError(
                "Не задана переменная окружения BOT_TOKEN.\n"
                "Получите токен у @BotFather и добавьте его в .env "
                "(см. .env.example)."
            )
        db_path = os.environ.get("DB_PATH", "expenses.db").strip() or "expenses.db"
        return cls(bot_token=token, db_path=db_path)
