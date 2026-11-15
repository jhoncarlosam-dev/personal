import pytest

from bandeja.errors import BandejaError
from bandeja.rules import default_rules, load_rules, rules_to_toml


def test_la_primera_regla_interna_es_comprobantes() -> None:
    rules = default_rules()
    assert rules[0].category == "comprobantes"
    assert "factura" in rules[0].patterns


def test_roundtrip_toml(tmp_path) -> None:
    original = default_rules()
    path = tmp_path / "reglas.toml"
    path.write_text(rules_to_toml(original), encoding="utf-8")
    assert load_rules(path) == original


def test_rechaza_extension_repetida(tmp_path) -> None:
    path = tmp_path / "reglas.toml"
    path.write_text(
        """\
[[regla]]
categoria = "a"
extensiones = ["pdf"]

[[regla]]
categoria = "b"
extensiones = ["PDF"]
""",
        encoding="utf-8",
    )
    with pytest.raises(BandejaError, match="pdf"):
        load_rules(path)


def test_rechaza_categoria_reservada(tmp_path) -> None:
    path = tmp_path / "reglas.toml"
    path.write_text(
        '[[regla]]\ncategoria = "_duplicados"\nextensiones = ["bin"]\n',
        encoding="utf-8",
    )
    with pytest.raises(BandejaError, match="inválida"):
        load_rules(path)


def test_rechaza_tabla_simple(tmp_path) -> None:
    path = tmp_path / "reglas.toml"
    path.write_text(
        '[regla]\ncategoria = "a"\nextensiones = ["pdf"]\n', encoding="utf-8"
    )
    with pytest.raises(BandejaError, match=r"no \[regla\]"):
        load_rules(path)


def test_rechaza_toml_invalido_y_archivo_ausente(tmp_path) -> None:
    path = tmp_path / "reglas.toml"
    path.write_text("[[regla]\n", encoding="utf-8")
    with pytest.raises(BandejaError, match="TOML"):
        load_rules(path)
    with pytest.raises(BandejaError, match="no se pudo leer"):
        load_rules(tmp_path / "no.toml")
