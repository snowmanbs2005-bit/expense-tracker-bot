"""Тесты расчёта отчёта: фильтрация по периоду, суммы по категориям, итог."""
from datetime import datetime, timedelta

import pytest

from bot.report import (
    Expense,
    build_report,
    filter_period,
    format_report,
    summarize,
    total,
)

NOW = datetime(2026, 7, 1, 12, 0, 0)


def make_expenses():
    return [
        Expense("еда", 500.0, NOW - timedelta(days=1)),
        Expense("еда", 300.0, NOW - timedelta(days=2)),
        Expense("такси", 250.0, NOW - timedelta(days=3)),
        Expense("развлечения", 1000.0, NOW - timedelta(days=10)),  # вне недели
        Expense("аренда", 20000.0, NOW - timedelta(days=40)),      # вне месяца
    ]


class TestSummarize:
    def test_sums_by_category(self):
        assert summarize(make_expenses()) == {
            "аренда": 20000.0,
            "развлечения": 1000.0,
            "еда": 800.0,
            "такси": 250.0,
        }

    def test_sorted_desc(self):
        assert list(summarize(make_expenses()).values()) == sorted(
            summarize(make_expenses()).values(), reverse=True
        )

    def test_empty(self):
        assert summarize([]) == {}


class TestTotal:
    def test_total(self):
        assert total(make_expenses()) == 22050.0

    def test_rounding(self):
        exp = [Expense("x", 0.1, NOW), Expense("x", 0.2, NOW)]
        assert total(exp) == 0.3


class TestFilterPeriod:
    def test_week(self):
        selected = filter_period(make_expenses(), "week", now=NOW)
        assert {e.category for e in selected} == {"еда", "такси"}

    def test_month(self):
        selected = filter_period(make_expenses(), "month", now=NOW)
        assert "аренда" not in {e.category for e in selected}
        assert "развлечения" in {e.category for e in selected}

    def test_all(self):
        assert len(filter_period(make_expenses(), "all", now=NOW)) == 5

    def test_invalid_period(self):
        with pytest.raises(ValueError):
            filter_period(make_expenses(), "year", now=NOW)


class TestBuildReport:
    def test_week_report(self):
        report = build_report(make_expenses(), "week", now=NOW)
        assert report.by_category == {"еда": 800.0, "такси": 250.0}
        assert report.total == 1050.0
        assert not report.is_empty

    def test_empty_report(self):
        report = build_report([], "week", now=NOW)
        assert report.is_empty
        assert report.total == 0

    def test_format_contains_total(self):
        report = build_report(make_expenses(), "week", now=NOW)
        text = format_report(report)
        assert "1050.00" in text
        assert "еда" in text

    def test_format_empty(self):
        text = format_report(build_report([], "month", now=NOW))
        assert "не найдено" in text
