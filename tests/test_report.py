from decimal import Decimal
from pathlib import Path

from bandeja.models import Action, ExpenseSummary, Result
from bandeja.report import render_report


def test_reporte_sin_archivos() -> None:
    text = render_report(Result(Path("/bandeja"), Path("/archivo"), simulated=True))
    assert "simulación (no se movió ningún archivo)" in text
    assert "Nada que archivar." in text
    assert "Ningún CSV con columnas de fecha y monto." in text
    assert "Ninguna." in text


def test_escapa_la_barra_vertical() -> None:
    inbox = Path("/bandeja")
    destination = Path("/archivo")
    result = Result(inbox, destination, simulated=True)
    result.actions.append(
        Action(
            source=inbox / "a|b.txt",
            destination=destination / "documentos" / "2026" / "03" / "a|b.txt",
            category="documentos",
            reason="extension",
            sha256="abc",
        )
    )
    assert "a\\|b.txt" in render_report(result)


def test_el_total_junta_la_misma_categoria_aunque_cambie_el_acento() -> None:
    result = Result(Path("/bandeja"), Path("/archivo"), simulated=False)
    result.expenses.append(
        ExpenseSummary("a.csv", 1, 0, Decimal("10.00"), {"Café": Decimal("10.00")})
    )
    result.expenses.append(
        ExpenseSummary("b.csv", 1, 0, Decimal("5.00"), {"cafe": Decimal("5.00")})
    )
    total = render_report(result).split("### Total", 1)[1]
    assert "| Café | 15,00 |" in total
    assert "| cafe |" not in total
    assert "Total: 15,00" in total
