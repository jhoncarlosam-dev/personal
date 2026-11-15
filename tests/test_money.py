from datetime import date
from decimal import Decimal

import pytest

from bandeja.money import format_amount, parse_amount, parse_date


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("25.000", "25000.00"),
        ("3.500", "3500.00"),
        ("1,50", "1.50"),
        ("1.50", "1.50"),
        ("1.00", "1.00"),
        ("1.000", "1000.00"),
        ("1.200.000,50", "1200000.50"),
        ("1,234.56", "1234.56"),
        ("15,000.50", "15000.50"),
        ("(2.500)", "-2500.00"),
        ("(2.500,50)", "-2500.50"),
        ("$ 1.234.567", "1234567.00"),
        ("COP 20.000", "20000.00"),
        ("-$1.200", "-1200.00"),
        ("2.50", "2.50"),
        ("0", "0.00"),
        ("12.3456", "12.35"),
    ],
)
def test_montos(raw: str, expected: str) -> None:
    assert parse_amount(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", ["", "   ", "abc", "12.34.56", "1..2", ".", "COP"])
def test_monto_invalido(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_amount(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-03-15", date(2026, 3, 15)),
        ("2026/3/5", date(2026, 3, 5)),
        ("15/03/2026", date(2026, 3, 15)),
        ("15-03-2026", date(2026, 3, 15)),
        ("03/15/2026", date(2026, 3, 15)),
        ("02/03/2026", date(2026, 3, 2)),
        ("", None),
        ("  ", None),
    ],
)
def test_fechas(raw: str, expected: date | None) -> None:
    assert parse_date(raw) == expected


@pytest.mark.parametrize("raw", ["13/13/2026", "2026-02-31", "marzo 15", "2026-13-01"])
def test_fecha_invalida(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_date(raw)


def test_formato_colombiano() -> None:
    assert format_amount(Decimal("1228500.50")) == "1.228.500,50"
    assert format_amount(Decimal(25000)) == "25.000,00"
    assert format_amount(Decimal(-3500)) == "-3.500,00"
    assert format_amount(Decimal(0)) == "0,00"
    assert format_amount(Decimal("1.005")) == "1,01"
