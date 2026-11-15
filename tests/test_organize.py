import os
import shutil
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from bandeja.errors import BandejaError, EjecucionError
from bandeja.models import Rule
from bandeja.organize import file_sha256, organize
from bandeja.rules import default_rules, rules_to_toml, validate_rules


def test_simular_no_crea_el_destino(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "nota.txt").write_text("hola", encoding="utf-8")
    destination = tmp_path / "out"
    result = organize(inbox, destination, simulate=True)
    assert result.simulated is True
    assert result.actions[0].category == "documentos"
    assert (inbox / "nota.txt").is_file()
    assert not destination.exists()


def test_bandeja_vacia_no_crea_el_destino(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    destination = tmp_path / "out"
    result = organize(inbox, destination)
    assert result.actions == []
    assert not destination.exists()


def test_duplicado_en_la_misma_corrida(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "factura-marzo.pdf").write_bytes(b"mismo")
    (inbox / "recibo-duplicado.pdf").write_bytes(b"mismo")
    result = organize(inbox, tmp_path / "out")
    assert [action.category for action in result.actions] == [
        "comprobantes",
        "_duplicados",
    ]
    assert result.actions[1].duplicate_of == result.actions[0].destination
    assert result.actions[0].sha256 == result.actions[1].sha256


def test_duplicado_contra_lo_ya_archivado(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    destination = tmp_path / "out"
    inbox.mkdir()
    (inbox / "factura-marzo.pdf").write_bytes(b"mismo-contenido")
    first = organize(inbox, destination)
    (inbox / "otra.pdf").write_bytes(b"mismo-contenido")
    second = organize(inbox, destination)
    assert second.actions[0].category == "_duplicados"
    assert second.actions[0].duplicate_of == first.actions[0].destination
    assert (destination / "_duplicados" / "otra.pdf").read_bytes() == b"mismo-contenido"


def test_sin_indice_no_mira_el_destino(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    destination = tmp_path / "out"
    inbox.mkdir()
    (inbox / "factura-marzo.pdf").write_bytes(b"mismo-contenido")
    organize(inbox, destination)
    (inbox / "otra.pdf").write_bytes(b"mismo-contenido")
    result = organize(inbox, destination, index_destination=False)
    assert result.duplicates == []
    assert result.actions[0].category == "documentos"
    assert not (destination / "_duplicados").exists()
    assert list(destination.rglob("factura-marzo.pdf"))
    assert list(destination.rglob("otra.pdf"))


def test_no_pisa_un_archivo_existente(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    destination = tmp_path / "out"
    inbox.mkdir()
    target = inbox / "notas.txt"
    target.write_text("uno", encoding="utf-8")
    moment = datetime(2026, 3, 18, 9, 0, 0).timestamp()
    os.utime(target, (moment, moment))
    organize(inbox, destination)
    target.write_text("dos", encoding="utf-8")
    os.utime(target, (moment, moment))
    result = organize(inbox, destination)
    folder = destination / "documentos" / "2026" / "03"
    assert (folder / "notas.txt").read_text(encoding="utf-8") == "uno"
    assert (folder / "notas-2.txt").read_text(encoding="utf-8") == "dos"
    assert result.actions[0].reason == "extension"


def test_colision_de_nombre_en_subcarpetas(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    (inbox / "a").mkdir(parents=True)
    (inbox / "b").mkdir()
    first = inbox / "a" / "nota.txt"
    second = inbox / "b" / "nota.txt"
    first.write_text("uno", encoding="utf-8")
    second.write_text("dos", encoding="utf-8")
    moment = datetime(2026, 3, 18, 9, 0, 0).timestamp()
    os.utime(first, (moment, moment))
    os.utime(second, (moment, moment))
    destination = tmp_path / "out"
    planned = organize(inbox, destination, recursive=True, simulate=True)
    assert not destination.exists()
    assert [action.destination.name for action in planned.actions] == [
        "nota.txt",
        "nota-2.txt",
    ]
    organize(inbox, destination, recursive=True)
    folder = destination / "documentos" / "2026" / "03"
    assert (folder / "nota.txt").read_text(encoding="utf-8") == "uno"
    assert (folder / "nota-2.txt").read_text(encoding="utf-8") == "dos"


def test_ignora_subcarpetas_si_no_es_recursivo(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    (inbox / "sub").mkdir(parents=True)
    (inbox / "sub" / "nota.txt").write_text("hola", encoding="utf-8")
    (inbox / "raiz.txt").write_text("raiz", encoding="utf-8")
    result = organize(inbox, tmp_path / "out")
    assert [action.source.name for action in result.actions] == ["raiz.txt"]
    assert (inbox / "sub" / "nota.txt").is_file()


def test_omite_ocultos(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / ".secreto.txt").write_text("x", encoding="utf-8")
    (inbox / "visible.txt").write_text("y", encoding="utf-8")
    result = organize(inbox, tmp_path / "out")
    assert result.hidden == 1
    assert [action.source.name for action in result.actions] == ["visible.txt"]
    assert (inbox / ".secreto.txt").is_file()


def test_omite_enlaces_simbolicos(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "nota.txt").write_text("hola", encoding="utf-8")
    (inbox / "enlace.txt").symlink_to("nota.txt")
    result = organize(inbox, tmp_path / "out")
    assert [action.source.name for action in result.actions] == ["nota.txt"]
    assert result.actions[0].category == "documentos"
    assert (inbox / "enlace.txt").is_symlink()
    assert any("enlace.txt" in warning for warning in result.warnings)


def test_no_mueve_el_archivo_de_reglas(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    rules = inbox / "reglas.toml"
    rules.write_text(rules_to_toml(default_rules()), encoding="utf-8")
    (inbox / "nota.txt").write_text("hola", encoding="utf-8")
    destination = tmp_path / "out"
    organize(inbox, destination, rules_path=rules)
    assert rules.is_file()
    assert list(destination.rglob("reglas.toml")) == []
    assert list(destination.rglob("nota.txt"))


def test_las_reglas_recibidas_reemplazan_a_las_internas(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "archivo.xyz").write_text("x", encoding="utf-8")
    rules = validate_rules([Rule("raros", frozenset({"xyz"}), ())])
    result = organize(inbox, tmp_path / "out", rules)
    assert result.actions[0].category == "raros"
    assert result.actions[0].reason == "extension"


def test_csv_duplicado_no_se_suma_dos_veces(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    content = "fecha,monto\n2026-03-01,10\n"
    (inbox / "gastos-a.csv").write_text(content, encoding="utf-8")
    (inbox / "gastos-b.csv").write_text(content, encoding="utf-8")
    result = organize(inbox, tmp_path / "out")
    assert len(result.expenses) == 1
    assert result.expenses[0].source == "gastos-a.csv"
    assert result.expenses[0].total == Decimal("10.00")
    assert result.duplicates[0].source.name == "gastos-b.csv"


def test_csv_que_no_es_de_gastos_solo_se_archiva(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "contactos.csv").write_text("nombre,edad\nAna,30\n", encoding="utf-8")
    result = organize(inbox, tmp_path / "out")
    assert result.expenses == []
    assert result.warnings == []
    assert result.actions[0].category == "hojas"


def test_csv_solo_con_encabezado_avisa(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "vacio.csv").write_text("fecha,monto\n", encoding="utf-8")
    result = organize(inbox, tmp_path / "out")
    assert result.expenses[0].rows == 0
    assert any("ninguna fila" in warning for warning in result.warnings)
    assert result.actions[0].category == "hojas"


@pytest.mark.parametrize("lugar", ["mismo", "dentro", "padre"])
def test_rutas_solapadas(tmp_path: Path, lugar: str) -> None:
    inbox = tmp_path / "bandeja"
    inbox.mkdir()
    if lugar == "mismo":
        destination = inbox
    elif lugar == "dentro":
        destination = inbox / "salida"
    else:
        destination = tmp_path
    with pytest.raises(BandejaError, match="destino"):
        organize(inbox, destination)


def test_bandeja_inexistente_o_que_no_es_carpeta(tmp_path: Path) -> None:
    with pytest.raises(BandejaError, match="no existe"):
        organize(tmp_path / "no", tmp_path / "out")
    archivo = tmp_path / "archivo"
    archivo.write_text("x", encoding="utf-8")
    with pytest.raises(BandejaError, match="no es una carpeta"):
        organize(archivo, tmp_path / "out")


def test_si_falla_a_mitad_se_puede_reanudar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inbox = tmp_path / "in"
    destination = tmp_path / "out"
    inbox.mkdir()
    (inbox / "a.txt").write_text("a", encoding="utf-8")
    (inbox / "b.txt").write_text("b", encoding="utf-8")
    real_move = shutil.move
    state = {"failed": False}

    def flaky(src: str, dst: str) -> str:
        if Path(src).name == "b.txt" and not state["failed"]:
            state["failed"] = True
            raise OSError(28, "No space left on device")
        return real_move(src, dst)

    monkeypatch.setattr("bandeja.organize.shutil.move", flaky)
    with pytest.raises(EjecucionError, match="b.txt") as caught:
        organize(inbox, destination)
    assert caught.value.result.actions[0].source.name == "a.txt"
    assert (inbox / "b.txt").is_file()
    assert not (inbox / "a.txt").exists()
    assert list(destination.rglob("a.txt"))

    again = organize(inbox, destination)
    assert [action.source.name for action in again.actions] == ["b.txt"]
    assert not (inbox / "b.txt").exists()
    assert list(destination.rglob("b.txt"))


def test_si_un_archivo_no_se_puede_leer_sigue_con_el_resto(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "a.txt").write_text("a", encoding="utf-8")
    (inbox / "b.txt").write_text("b", encoding="utf-8")
    real_hash = file_sha256

    def flaky(path: Path) -> str:
        if path.name == "a.txt":
            raise OSError(13, "Permission denied")
        return real_hash(path)

    monkeypatch.setattr("bandeja.organize.file_sha256", flaky)
    result = organize(inbox, tmp_path / "out")
    assert [action.source.name for action in result.actions] == ["b.txt"]
    assert (inbox / "a.txt").is_file()
    assert any("a.txt" in warning for warning in result.warnings)
