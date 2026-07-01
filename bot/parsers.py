"""Разбор текстовых команд бота.

Логика вынесена в чистые функции без зависимостей от Telegram и БД —
её удобно покрывать юнит-тестами.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import time


class ParseError(ValueError):
    """Команда введена в неправильном формате."""


@dataclass(frozen=True)
class AddCommand:
    amount: float
    category: str


@dataclass(frozen=True)
class RemindCommand:
    at: time
    text: str


def _strip_command(text: str, name: str) -> str:
    """Убирает ведущий `/name` (или `name`, `/name@botusername`), возвращает остаток."""
    stripped = text.strip()
    parts = stripped.split(maxsplit=1)
    if not parts:
        return ""
    head = parts[0]
    cmd = head.lstrip("/").split("@", 1)[0].lower()
    if cmd == name:
        return parts[1].strip() if len(parts) > 1 else ""
    return stripped


def parse_amount(raw: str) -> float:
    """'500' / '500,50' / '500.5' -> положительный float, округлённый до копеек."""
    normalized = raw.strip().replace(",", ".")
    try:
        value = float(normalized)
    except ValueError as exc:
        raise ParseError(f"Не удалось разобрать сумму: {raw!r}") from exc
    if value != value or value in (float("inf"), float("-inf")):
        raise ParseError(f"Некорректная сумма: {raw!r}")
    if value <= 0:
        raise ParseError("Сумма должна быть больше нуля.")
    return round(value, 2)


def parse_add(text: str) -> AddCommand:
    """Разбирает `/add 500 еда` -> AddCommand(amount=500.0, category='еда')."""
    remainder = _strip_command(text, "add")
    tokens = remainder.split(maxsplit=1)
    if len(tokens) < 2:
        raise ParseError("Формат: /add <сумма> <категория>. Пример: /add 500 еда")
    amount = parse_amount(tokens[0])
    category = tokens[1].strip().lower()
    if not category:
        raise ParseError("Не указана категория. Пример: /add 500 еда")
    return AddCommand(amount=amount, category=category)


def parse_time(raw: str) -> time:
    """'18:00' -> datetime.time(18, 0). Часы 0-23, минуты 0-59."""
    value = raw.strip()
    if ":" not in value:
        raise ParseError(f"Время в формате ЧЧ:ММ, получено {raw!r}")
    hh, mm = value.split(":", 1)
    try:
        hour, minute = int(hh), int(mm)
    except ValueError as exc:
        raise ParseError(f"Время в формате ЧЧ:ММ, получено {raw!r}") from exc
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ParseError("Часы должны быть 0-23, минуты 0-59.")
    return time(hour=hour, minute=minute)


def parse_remind(text: str) -> RemindCommand:
    """Разбирает `/remind 18:00 купить хлеб` -> RemindCommand."""
    remainder = _strip_command(text, "remind")
    tokens = remainder.split(maxsplit=1)
    if len(tokens) < 2:
        raise ParseError("Формат: /remind ЧЧ:ММ <текст>. Пример: /remind 18:00 отчёт")
    at = parse_time(tokens[0])
    message = tokens[1].strip()
    if not message:
        raise ParseError("Не указан текст напоминания.")
    return RemindCommand(at=at, text=message)
