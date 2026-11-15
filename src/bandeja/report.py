"""Presenta el resultado en Markdown y en JSON."""

import json
import unicodedata
from decimal import Decimal
from pathlib import Path

from bandeja.models import Action, ExpenseSummary, Result
from bandeja.money import format_amount

_REASONS = {
    "patron": "patrón",
    "extension": "extensión",
    "otros": "sin regla",
    "duplicado": "duplicado",
}


def render_report(result: Result) -> str:
    mode = (
        "simulación (no se movió ningún archivo)" if result.simulated else "archivado"
    )
    lines = [
        "# Reporte de bandeja",
        "",
        f"- Modo: {mode}",
        f"- Bandeja: `{result.inbox}`",
        f"- Destino: `{result.destination}`",
        f"- Archivos tratados: {len(result.actions)}",
        f"- Archivados: {len(result.archived)}",
        f"- Duplicados: {len(result.duplicates)}",
        f"- Ocultos omitidos: {result.hidden}",
        f"- Advertencias: {len(result.warnings)}",
        "",
        "## Movimientos",
        "",
    ]
    if not result.actions:
        lines.append("Nada que archivar.")
        lines.append("")
    else:
        lines.extend(
            [
                "| Archivo | Categoría | Destino | Motivo |",
                "| --- | --- | --- | --- |",
            ]
        )
        for action in result.actions:
            cells = [
                _cell(_relative(action.source, result.inbox)),
                _cell(action.category),
                _cell(_relative(action.destination, result.destination)),
                _cell(_reason(action, result.destination)),
            ]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    lines.extend(_expenses(result))
    lines.extend(["## Advertencias", ""])
    if result.warnings:
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("Ninguna.")
    lines.append("")
    return "\n".join(lines)


def render_json(result: Result) -> str:
    payload = {
        "simulado": result.simulated,
        "bandeja": str(result.inbox),
        "destino": str(result.destination),
        "ocultos": result.hidden,
        "advertencias": list(result.warnings),
        "movimientos": [_action_json(action) for action in result.actions],
        "gastos": [_expense_json(summary) for summary in result.expenses],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _expenses(result: Result) -> list[str]:
    lines = ["## Gastos", ""]
    if not result.expenses:
        lines.extend(["Ningún CSV con columnas de fecha y monto.", ""])
        return lines

    combined: dict[str, tuple[str, Decimal]] = {}
    several = len(result.expenses) > 1
    for summary in result.expenses:
        lines.extend(
            [
                f"### {summary.source}",
                "",
                f"Filas válidas: {summary.rows}. Filas omitidas: {summary.skipped}.",
                "",
            ]
        )
        lines.extend(_amount_table(summary.by_category))
        label = "Subtotal" if several else "Total"
        lines.extend([f"{label}: {format_amount(summary.total)}", ""])
        for category, amount in summary.by_category.items():
            _accumulate(combined, category, amount)
    if several:
        totals = {label: amount for label, amount in combined.values()}
        grand = sum(totals.values(), Decimal("0.00"))
        lines.extend(["### Total", ""])
        lines.extend(_amount_table(totals))
        lines.extend([f"Total: {format_amount(grand)}", ""])
    return lines


def _amount_table(amounts: dict[str, Decimal]) -> list[str]:
    if not amounts:
        return ["Sin filas válidas.", ""]
    lines = ["| Categoría | Total |", "| --- | --- |"]
    for category, amount in amounts.items():
        lines.append(f"| {_cell(category)} | {format_amount(amount)} |")
    lines.append("")
    return lines


def _accumulate(
    grouped: dict[str, tuple[str, Decimal]], label: str, amount: Decimal
) -> None:
    key = _fold(label)
    current = grouped.get(key)
    if current is None:
        grouped[key] = (label, amount)
        return
    grouped[key] = (current[0], current[1] + amount)


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.strip().casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _reason(action: Action, destination: Path) -> str:
    if action.duplicate_of is not None:
        return f"duplicado de {_relative(action.duplicate_of, destination)}"
    return _REASONS.get(action.reason, action.reason)


def _action_json(action: Action) -> dict[str, object]:
    return {
        "origen": str(action.source),
        "destino": str(action.destination),
        "categoria": action.category,
        "motivo": action.reason,
        "sha256": action.sha256,
        "duplicado_de": None
        if action.duplicate_of is None
        else str(action.duplicate_of),
    }


def _expense_json(summary: ExpenseSummary) -> dict[str, object]:
    return {
        "origen": summary.source,
        "filas": summary.rows,
        "omitidas": summary.skipped,
        "total": f"{summary.total:.2f}",
        "por_categoria": {
            category: f"{amount:.2f}"
            for category, amount in summary.by_category.items()
        },
    }


def _cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
