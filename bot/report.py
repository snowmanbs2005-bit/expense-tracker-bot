"""Расчёт отчёта по расходам и построение графика.

Расчётная часть — чистые функции (тестируемые). Графика рисуется
matplotlib на бэкенде Agg и возвращается как PNG в байтах.
"""
from __future__ import annotations

import io
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional

VALID_PERIODS = ("week", "month", "all")


@dataclass(frozen=True)
class Expense:
    category: str
    amount: float
    created_at: datetime


def period_start(period: str, now: Optional[datetime] = None) -> Optional[datetime]:
    """Начало периода. Для 'all' возвращает None (без нижней границы)."""
    now = now or datetime.now()
    if period == "week":
        return now - timedelta(days=7)
    if period == "month":
        return now - timedelta(days=30)
    if period == "all":
        return None
    raise ValueError(f"Неизвестный период: {period!r}. Допустимо: {VALID_PERIODS}")


def filter_period(
    expenses: Iterable[Expense], period: str, now: Optional[datetime] = None
) -> List[Expense]:
    """Оставляет траты, попадающие в заданный период."""
    start = period_start(period, now)
    if start is None:
        return list(expenses)
    return [e for e in expenses if e.created_at >= start]


def summarize(expenses: Iterable[Expense]) -> Dict[str, float]:
    """Суммы по категориям, отсортированные по убыванию."""
    totals: Dict[str, float] = defaultdict(float)
    for e in expenses:
        totals[e.category] += e.amount
    rounded = {k: round(v, 2) for k, v in totals.items()}
    return dict(sorted(rounded.items(), key=lambda kv: kv[1], reverse=True))


def total(expenses: Iterable[Expense]) -> float:
    """Общая сумма трат."""
    return round(sum(e.amount for e in expenses), 2)


@dataclass(frozen=True)
class Report:
    period: str
    by_category: Dict[str, float]
    total: float

    @property
    def is_empty(self) -> bool:
        return not self.by_category


def build_report(
    expenses: Iterable[Expense], period: str, now: Optional[datetime] = None
) -> Report:
    """Собирает отчёт за период: суммы по категориям + итог."""
    if period not in VALID_PERIODS:
        raise ValueError(f"Неизвестный период: {period!r}")
    selected = filter_period(expenses, period, now)
    by_category = summarize(selected)
    return Report(period=period, by_category=by_category, total=total(selected))


_PERIOD_LABEL = {"week": "неделю", "month": "месяц", "all": "всё время"}


def format_report(report: Report) -> str:
    """Текстовое представление отчёта для отправки в чат."""
    label = _PERIOD_LABEL.get(report.period, report.period)
    if report.is_empty:
        return f"За {label} трат не найдено."
    lines = [f"📊 Отчёт за {label}:", ""]
    for category, amount in report.by_category.items():
        lines.append(f"• {category}: {amount:.2f}")
    lines.append("")
    lines.append(f"Итого: {report.total:.2f}")
    return "\n".join(lines)


def render_chart(report: Report) -> bytes:
    """Строит горизонтальную столбчатую диаграмму расходов по категориям (PNG)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    categories = list(report.by_category.keys())
    values = list(report.by_category.values())

    fig, ax = plt.subplots(figsize=(7, max(2.5, 0.6 * len(categories) + 1)))
    bars = ax.barh(categories, values, color="#4c78a8")
    ax.invert_yaxis()  # самая большая категория — сверху
    ax.set_xlabel("Сумма")
    ax.set_title(f"Расходы за {_PERIOD_LABEL.get(report.period, report.period)}")
    ax.bar_label(bars, fmt="%.0f", padding=3)
    ax.margins(x=0.15)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    return buf.getvalue()
