"""Тесты разбора команд /add и /remind."""
from datetime import time

import pytest

from bot.parsers import (
    AddCommand,
    ParseError,
    RemindCommand,
    parse_add,
    parse_amount,
    parse_remind,
    parse_time,
)


class TestParseAmount:
    @pytest.mark.parametrize(
        "raw, expected",
        [("500", 500.0), ("500.50", 500.5), ("500,50", 500.5), ("0.01", 0.01), ("10.999", 11.0)],
    )
    def test_valid(self, raw, expected):
        assert parse_amount(raw) == expected

    @pytest.mark.parametrize("raw", ["abc", "", "0", "-5", "-0.01", "  "])
    def test_invalid(self, raw):
        with pytest.raises(ParseError):
            parse_amount(raw)


class TestParseAdd:
    def test_basic(self):
        assert parse_add("/add 500 еда") == AddCommand(amount=500.0, category="еда")

    def test_without_slash(self):
        assert parse_add("add 500 еда") == AddCommand(amount=500.0, category="еда")

    def test_multiword_category(self):
        assert parse_add("/add 1200 продукты и вода") == AddCommand(
            amount=1200.0, category="продукты и вода"
        )

    def test_category_lowercased(self):
        assert parse_add("/add 300 Кофе").category == "кофе"

    def test_comma_decimal(self):
        assert parse_add("/add 99,90 такси").amount == 99.9

    def test_bot_mention_stripped(self):
        assert parse_add("/add@my_bot 500 еда") == AddCommand(500.0, "еда")

    @pytest.mark.parametrize("text", ["/add", "/add 500", "/add еда", "/add abc еда"])
    def test_invalid(self, text):
        with pytest.raises(ParseError):
            parse_add(text)


class TestParseTime:
    @pytest.mark.parametrize(
        "raw, expected",
        [("18:00", time(18, 0)), ("00:00", time(0, 0)), ("23:59", time(23, 59)), ("9:05", time(9, 5))],
    )
    def test_valid(self, raw, expected):
        assert parse_time(raw) == expected

    @pytest.mark.parametrize("raw", ["1800", "24:00", "18:60", "aa:bb", "-1:00", ""])
    def test_invalid(self, raw):
        with pytest.raises(ParseError):
            parse_time(raw)


class TestParseRemind:
    def test_basic(self):
        assert parse_remind("/remind 18:00 отчёт") == RemindCommand(
            at=time(18, 0), text="отчёт"
        )

    def test_multiword_text(self):
        result = parse_remind("/remind 09:30 записать расходы за день")
        assert result.at == time(9, 30)
        assert result.text == "записать расходы за день"

    def test_without_slash(self):
        assert parse_remind("remind 18:00 привет").text == "привет"

    @pytest.mark.parametrize("text", ["/remind", "/remind 18:00", "/remind текст", "/remind 25:00 x"])
    def test_invalid(self, text):
        with pytest.raises(ParseError):
            parse_remind(text)
