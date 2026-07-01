# expense-tracker-bot

Telegram-бот на Python для учёта личных и командных расходов с напоминаниями.
Добавляйте траты одной командой, получайте отчёт с разбивкой по категориям и
графиком — **без ручных таблиц в Excel**.

[![tests](https://github.com/snowmanbs2005-bit/expense-tracker-bot/actions/workflows/tests.yml/badge.svg)](https://github.com/snowmanbs2005-bit/expense-tracker-bot/actions/workflows/tests.yml)

## Что решает

Учёт расходов обычно ведут в заметках или таблицах — это долго и легко забросить.
Здесь достаточно написать боту `/add 500 еда`, а раз в неделю посмотреть `/report`:
бот сам посчитает суммы по категориям и построит график. Плюс напоминания
(`/remind 18:00 записать расходы`), чтобы не забывать вносить траты.

## Возможности

- **`/add <сумма> <категория>`** — добавить трату. Примеры: `/add 500 еда`, `/add 99,90 такси`, `/add 1200 продукты и вода`.
- **`/report [week|month|all]`** — отчёт за неделю (по умолчанию), месяц или всё время: суммы по категориям, итог и график (PNG).
- **`/remind ЧЧ:ММ <текст>`** — ежедевное напоминание в заданное время. Пример: `/remind 18:00 записать расходы`.
- **`/help`** — справка по командам.
- Хранение в **SQLite**, асинхронность на **aiogram 3**, график на **matplotlib**.

## Стек

| Назначение        | Технология         |
|-------------------|--------------------|
| Telegram API      | aiogram 3          |
| Хранилище         | SQLite (aiosqlite) |
| Графики           | matplotlib         |
| Конфигурация      | python-dotenv      |
| Тесты             | pytest             |

## Как получить токен бота

1. Откройте в Telegram [@BotFather](https://t.me/BotFather).
2. Отправьте `/newbot`, задайте отображаемое имя и username (должен заканчиваться на `bot`).
3. BotFather пришлёт **токен** вида `123456789:AAE...`. Это и есть ваш `BOT_TOKEN`.

## Запуск

```bash
# 1. Клонировать и перейти в папку
git clone https://github.com/snowmanbs2005-bit/expense-tracker-bot.git
cd expense-tracker-bot

# 2. Виртуальное окружение
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Зависимости
pip install -r requirements.txt

# 4. Токен: скопировать шаблон и вставить свой BOT_TOKEN
cp .env.example .env
#   затем откройте .env и подставьте токен от @BotFather

# 5. Запуск
python -m bot.main
```

Токен читается из переменной окружения `BOT_TOKEN` (или из файла `.env`).
Можно и без `.env`:

```bash
export BOT_TOKEN="123456789:AAE..."   # Windows PowerShell: $env:BOT_TOKEN="..."
python -m bot.main
```

## Тесты

Покрыта логика разбора команд и расчёта отчёта:

```bash
pip install pytest
pytest -q
```

## Структура проекта

```
expense-tracker-bot/
├── bot/
│   ├── main.py        # точка входа: бот, БД, планировщик
│   ├── config.py      # чтение BOT_TOKEN из окружения / .env
│   ├── parsers.py     # разбор /add и /remind (чистые функции)
│   ├── report.py      # расчёт отчёта + график matplotlib
│   ├── db.py          # хранилище SQLite (aiosqlite)
│   ├── handlers.py    # обработчики команд aiogram
│   └── reminders.py   # фоновый цикл напоминаний
├── tests/
│   ├── test_parsers.py
│   └── test_report.py
├── .env.example
├── requirements.txt
└── README.md
```

## Лицензия

[MIT](LICENSE)
