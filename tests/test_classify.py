import pytest

from bandeja.classify import classify
from bandeja.rules import default_rules


@pytest.mark.parametrize(
    ("name", "category", "reason"),
    [
        ("factura-marzo.pdf", "comprobantes", "patron"),
        ("Factura de marzo.PDF", "comprobantes", "patron"),
        ("nota_credito.xml", "comprobantes", "patron"),
        ("factura.zip", "comprobantes", "patron"),
        ("contrato.pdf", "documentos", "extension"),
        ("foto.png", "imagenes", "extension"),
        ("archivo.JPG", "imagenes", "extension"),
        ("gastos.csv", "hojas", "extension"),
        ("datos.zip", "comprimidos", "extension"),
        ("raro.xyz", "otros", "otros"),
        ("Makefile", "otros", "otros"),
    ],
)
def test_clasificacion(name: str, category: str, reason: str) -> None:
    result = classify(name, default_rules())
    assert result.category == category
    assert result.reason == reason
