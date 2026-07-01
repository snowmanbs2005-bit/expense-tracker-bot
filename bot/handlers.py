"""Обработчики команд Telegram (aiogram 3)."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, Message

from .db import Database
from .parsers import ParseError, parse_add, parse_remind
from .report import build_report, format_report, render_chart

router = Router()

HELP_TEXT = (
    "💸 <b>expense-tracker-bot</b> — учёт расходов без ручных таблиц.\n\n"
    "<b>Команды:</b>\n"
    "/add &lt;сумма&gt; &lt;категория&gt; — добавить трату\n"
    "   пример: <code>/add 500 еда</code>\n"
    "/report [week|month|all] — отчёт с суммами по категориям и графиком\n"
    "   пример: <code>/report month</code>\n"
    "/remind ЧЧ:ММ &lt;текст&gt; — ежедневное напоминание\n"
    "   пример: <code>/remind 18:00 записать расходы</code>\n"
    "/help — эта справка"
)


def build_router(db: Database) -> Router:
    """Возвращает роутер с обработчиками, замкнутыми на конкретную БД."""

    @router.message(CommandStart())
    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        await message.answer(HELP_TEXT)

    @router.message(Command("add"))
    async def cmd_add(message: Message) -> None:
        try:
            cmd = parse_add(message.text or "")
        except ParseError as exc:
            await message.answer(f"⚠️ {exc}")
            return
        await db.add_expense(message.from_user.id, cmd.amount, cmd.category)
        await message.answer(
            f"✅ Записано: {cmd.amount:.2f} — {cmd.category}"
        )

    @router.message(Command("report"))
    async def cmd_report(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        period = parts[1].strip().lower() if len(parts) > 1 else "week"
        if period not in ("week", "month", "all"):
            await message.answer("⚠️ Период: week, month или all. Пример: /report month")
            return
        expenses = await db.list_expenses(message.from_user.id)
        report = build_report(expenses, period)
        await message.answer(format_report(report))
        if not report.is_empty:
            png = render_chart(report)
            await message.answer_photo(
                BufferedInputFile(png, filename="report.png")
            )

    @router.message(Command("remind"))
    async def cmd_remind(message: Message) -> None:
        try:
            cmd = parse_remind(message.text or "")
        except ParseError as exc:
            await message.answer(f"⚠️ {exc}")
            return
        await db.add_reminder(
            message.from_user.id,
            message.chat.id,
            cmd.at.hour,
            cmd.at.minute,
            cmd.text,
        )
        await message.answer(
            f"⏰ Напоминание на {cmd.at.strftime('%H:%M')} сохранено: {cmd.text}"
        )

    @router.message(F.text & ~F.text.startswith("/"))
    async def fallback(message: Message) -> None:
        await message.answer("Не понимаю. /help — список команд.")

    return router
