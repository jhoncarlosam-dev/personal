"""Resume un CSV de gastos si trae columnas de fecha y monto."""

import csv
import io
import unicodedata
from decimal import Decimal
from pathlib import Path

from bandeja.models import ExpenseSummary
from bandeja.money import parse_amount, parse_date

_DATE = ("fecha", "date", "dia")
_AMOUNT = ("monto", "valor", "importe", "amount", "total")
_CATEGORY = ("categoria", "category", "rubro")
_CONCEPT = ("concepto", "descripcion", "description", "detalle")


def summarize_expenses(path: Path) -> ExpenseSummary | None:
    """Devuelve None cuando el CSV no es un listado de gastos."""
    text = _read_text(path)
    if not text.strip():
        return None
    reader = csv.DictReader(io.StringIO(text), delimiter=_delimiter(text))
    if not reader.fieldnames:
        return None
    columns = {_fold(name): name for name in reader.fieldnames if name}
    date_column = _pick(columns, _DATE)
    amount_column = _pick(columns, _AMOUNT)
    if date_column is None or amount_column is None:
        return None
    category_column = _pick(columns, _CATEGORY)
    concept_column = _pick(columns, _CONCEPT)

    grouped: dict[str, tuple[str, Decimal]] = {}
    valid = 0
    skipped = 0
    for row in reader:
        if not any(
            (value or "").strip() for value in row.values() if isinstance(value, str)
        ):
            continue
        try:
            amount = parse_amount(row.get(amount_column) or "")
            date_text = (row.get(date_column) or "").strip()
            if not date_text:
                raise ValueError("fecha vacía")
            parse_date(date_text)
        except (ValueError, KeyError):
            skipped += 1
            continue
        label = _label(row, category_column, concept_column)
        key = _fold(label)
        current = grouped.get(key)
        grouped[key] = (
            (label, amount) if current is None else (current[0], current[1] + amount)
        )
        valid += 1

    by_category = {label: total for label, total in grouped.values()}
    grand = sum(by_category.values(), Decimal("0.00"))
    return ExpenseSummary(path.name, valid, skipped, grand, by_category)


def _read_text(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def _delimiter(text: str) -> str:
    """Elige el separador mirando solo el encabezado.

    Un monto como ``1.200.000,50`` lleva coma. Si se inspeccionara el archivo
    completo, esa coma parecería separar columnas.
    """
    header = next((line for line in text.splitlines() if line.strip()), "")
    counts = {separator: header.count(separator) for separator in (";", ",", "\t")}
    best = max(counts, key=lambda separator: counts[separator])
    return best if counts[best] else ","


def _pick(columns: dict[str, str], options: tuple[str, ...]) -> str | None:
    for option in options:
        found = columns.get(option)
        if found is not None:
            return found
    return None


def _label(
    row: dict[str, str | None], category: str | None, concept: str | None
) -> str:
    for column in (category, concept):
        if column is None:
            continue
        text = (row.get(column) or "").strip()
        if text:
            return text
    return "sin categoría"


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.strip().casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))
