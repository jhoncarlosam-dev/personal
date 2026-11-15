from decimal import Decimal
from pathlib import Path

from bandeja.demo import create_example
from bandeja.organize import organize
from bandeja.report import render_report


def test_el_ejemplo_simula_archiva_y_se_puede_correr_de_nuevo(tmp_path: Path) -> None:
    inbox = create_example(tmp_path / "bandeja")
    destination = tmp_path / "archivo"

    planned = organize(inbox, destination, simulate=True)
    assert planned.simulated is True
    assert not destination.exists()
    assert (inbox / "factura-marzo.pdf").is_file()
    assert len(planned.actions) == 8
    assert planned.hidden == 1
    assert len(planned.warnings) == 2
    assert planned.expenses[0].rows == 3
    assert planned.expenses[0].skipped == 1
    assert planned.expenses[0].total == Decimal("1228500.50")
    assert planned.expenses[0].by_category == {
        "Alimentación": Decimal("25000.00"),
        "Transporte": Decimal("3500.00"),
        "Hogar": Decimal("1200000.50"),
    }
    planned_text = render_report(planned)
    assert "simulación (no se movió ningún archivo)" in planned_text
    assert "1.228.500,50" in planned_text
    assert "25.000,00" in planned_text
    assert "1.200.000,50" in planned_text

    done = organize(inbox, destination)
    assert done.simulated is False
    text = render_report(done)
    assert "\n- Modo: archivado\n" in text
    assert "duplicado de comprobantes/2026/03/factura-marzo.pdf" in text
    assert "Se omitió el enlace simbólico enlace-factura.pdf" in text
    assert "gastos-marzo.csv: 3 filas válidas, 1 fila omitida" in text
    assert "Ocultos omitidos: 1" in text
    factura = next(
        action for action in done.actions if action.source.name == "factura-marzo.pdf"
    )
    copia = next(
        action
        for action in done.actions
        if action.source.name == "recibo-duplicado.pdf"
    )
    assert copia.sha256 == factura.sha256
    assert copia.duplicate_of == factura.destination
    assert sorted(
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file()
    ) == [
        "_duplicados/recibo-duplicado.pdf",
        "comprobantes/2026/03/factura-marzo.pdf",
        "comprobantes/2026/03/recibo_dian.xml",
        "documentos/2026/03/contrato.pdf",
        "documentos/2026/04/notas.txt",
        "hojas/2026/03/gastos-marzo.csv",
        "imagenes/2026/03/foto-viaje.png",
        "otros/2026/03/archivo-raro.xyz",
    ]
    assert sorted(path.name for path in inbox.iterdir()) == [
        ".borrador.txt",
        "enlace-factura.pdf",
    ]

    again = organize(inbox, destination)
    assert again.actions == []
    assert again.hidden == 1
    assert again.expenses == []
    assert any("enlace-factura.pdf" in warning for warning in again.warnings)

    (inbox / "otra-vez.pdf").write_bytes(
        (
            destination / "comprobantes" / "2026" / "03" / "factura-marzo.pdf"
        ).read_bytes()
    )
    third = organize(inbox, destination)
    assert [action.destination.name for action in third.actions] == ["otra-vez.pdf"]
    assert third.actions[0].category == "_duplicados"
    assert third.expenses == []
