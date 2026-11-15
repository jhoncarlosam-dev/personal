"""Crea una bandeja pequeña para recorrer la aplicación de punta a punta."""

import os
from datetime import datetime
from pathlib import Path

from bandeja.errors import BandejaError

# Las 9:00 evitan que un cambio de zona horaria mueva el archivo de mes.
_APRIL = datetime(2026, 4, 2, 9, 0, 0)
_INVOICE = b"%PDF-1.4\nfactura de marzo\n"
_EXPENSES = """fecha;concepto;categoria;monto
15/03/2026;Almuerzo;Alimentación;25.000
16/03/2026;Bus;Transporte;3.500
02/04/2026;Arriendo;Hogar;1.200.000,50
sin-fecha;Taxi;Transporte;no-es-un-monto
"""


def create_example(directory: Path) -> Path:
    """Crea ``directory`` con facturas, un duplicado, un CSV y un archivo oculto."""
    if directory.exists():
        raise BandejaError(f"ya existe: {directory}")
    try:
        directory.mkdir(parents=True)
    except OSError as exc:
        raise BandejaError(
            f"no se pudo crear {directory}: {exc.strerror or exc}"
        ) from exc

    _write(directory / "factura-marzo.pdf", _INVOICE, datetime(2026, 3, 18, 9, 0, 0))
    _write(directory / "recibo-duplicado.pdf", _INVOICE, datetime(2026, 3, 18, 9, 0, 0))
    _write(
        directory / "contrato.pdf",
        b"%PDF-1.4\ncontrato\n",
        datetime(2026, 3, 4, 9, 0, 0),
    )
    _write(
        directory / "recibo_dian.xml", b"<recibo/>\n", datetime(2026, 3, 11, 9, 0, 0)
    )
    _write(
        directory / "foto-viaje.png",
        b"\x89PNG\r\nfoto\n",
        datetime(2026, 3, 20, 9, 0, 0),
    )
    _write(directory / "notas.txt", b"notas de la reunion\n", _APRIL)
    _write(
        directory / "gastos-marzo.csv",
        _EXPENSES.encode(),
        datetime(2026, 3, 18, 9, 0, 0),
    )
    _write(directory / "archivo-raro.xyz", b"??\n", datetime(2026, 3, 7, 9, 0, 0))
    _write(directory / ".borrador.txt", b"oculto\n", datetime(2026, 3, 1, 9, 0, 0))
    (directory / "enlace-factura.pdf").symlink_to("factura-marzo.pdf")
    return directory


def _write(path: Path, content: bytes, moment: datetime) -> None:
    path.write_bytes(content)
    timestamp = moment.timestamp()
    os.utime(path, (timestamp, timestamp))
