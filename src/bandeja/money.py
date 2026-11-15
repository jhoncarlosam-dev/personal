"""Montos y fechas en el formato que usa un CSV exportado desde Colombia."""

import re
import unicodedata
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

_CURRENCY = re.compile(r"(?i)(?:cop|usd|eur|[$€£])")


def parse_amount(raw: str) -> Decimal:
    """Convierte un monto a pesos con dos decimales.

    ``25.000`` y ``1.200.000,50`` se leen como en Colombia. Si aparecen punto
    y coma, el último separador es el decimal. Un grupo de exactamente tres
    dígitos es de miles (``1.000`` vale mil); uno o dos dígitos son decimales
    (``1.50`` vale uno con cincuenta).
    """
    text = unicodedata.normalize("NFKC", raw).strip()
    text = text.replace("\u00a0", "").replace(" ", "")
    text = _CURRENCY.sub("", text)
    if not text:
        raise ValueError(f"monto vacío: {raw!r}")

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]
    if text.startswith("+"):
        text = text[1:]
    elif text.startswith("-"):
        negative = True
        text = text[1:]
    if not re.fullmatch(r"\d+(?:[.,]\d+)*", text):
        raise ValueError(f"monto inválido: {raw!r}")

    try:
        amount = Decimal(_plain_number(text))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"monto inválido: {raw!r}") from exc
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return -amount if negative else amount


def parse_date(raw: str) -> date | None:
    """Lee una fecha ISO o día/mes/año.

    Si los dos primeros números caben en un día y en un mes, gana el orden
    colombiano: día, luego mes. ``03/15/2026`` sí se reconoce como 15 de marzo
    porque 15 no puede ser un mes.
    """
    text = raw.strip()
    if not text:
        return None
    iso = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if iso:
        year, month, day = (int(part) for part in iso.groups())
        return date(year, month, day)
    local = re.fullmatch(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", text)
    if local is None:
        raise ValueError(f"fecha inválida: {raw!r}")
    first, second, year = (int(part) for part in local.groups())
    if first > 12:
        day, month = first, second
    elif second > 12:
        month, day = first, second
    else:
        day, month = first, second
    return date(year, month, day)


def format_amount(value: Decimal) -> str:
    """Formatea ``1228500.50`` como ``1.228.500,50``."""
    quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if quantized < 0 else ""
    whole, fraction = f"{abs(quantized):.2f}".split(".")
    groups: list[str] = []
    while whole:
        groups.append(whole[-3:])
        whole = whole[:-3]
    return f"{sign}{'.'.join(reversed(groups))},{fraction}"


def _plain_number(text: str) -> str:
    if "." in text and "," in text:
        if text.rfind(",") > text.rfind("."):
            return text.replace(".", "").replace(",", ".")
        return text.replace(",", "")
    separator = "," if "," in text else "."
    if separator not in text:
        return text
    parts = text.split(separator)
    if _is_thousands(parts):
        return "".join(parts)
    if text.count(separator) == 1:
        return f"{parts[0]}.{parts[1]}"
    raise ValueError(text)


def _is_thousands(parts: list[str]) -> bool:
    return (
        len(parts) >= 2
        and parts[0].isdigit()
        and 1 <= len(parts[0]) <= 3
        and all(len(part) == 3 and part.isdigit() for part in parts[1:])
    )
