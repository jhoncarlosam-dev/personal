import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bandeja.cli import main
from bandeja.rules import default_rules, load_rules


def test_simular_por_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "factura-acme.pdf").write_bytes(b"%PDF")
    destination = tmp_path / "out"
    code = main(["ordenar", str(inbox), "--destino", str(destination), "--simular"])
    captured = capsys.readouterr()
    assert code == 0
    assert "simulación" in captured.out
    assert "comprobantes" in captured.out
    assert (inbox / "factura-acme.pdf").is_file()
    assert not destination.exists()


def test_reporte_y_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "notas.txt").write_text("hola", encoding="utf-8")
    destination = tmp_path / "out"
    report = tmp_path / "reporte.md"
    payload = tmp_path / "reporte.json"
    code = main(
        [
            "ordenar",
            str(inbox),
            "--destino",
            str(destination),
            "--reporte",
            str(report),
            "--json",
            str(payload),
        ]
    )
    assert code == 0
    assert not (inbox / "notas.txt").exists()
    assert list(destination.rglob("notas.txt"))
    text = report.read_text(encoding="utf-8")
    assert "extensión" in text
    data = json.loads(payload.read_text(encoding="utf-8"))
    assert data["simulado"] is False
    assert data["movimientos"][0]["categoria"] == "documentos"
    assert capsys.readouterr().out == text


def test_reporte_dentro_de_la_bandeja_avisa(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "nota.txt").write_text("hola", encoding="utf-8")
    report = inbox / "reporte.md"
    code = main(
        [
            "ordenar",
            str(inbox),
            "--destino",
            str(tmp_path / "out"),
            "--simular",
            "--reporte",
            str(report),
        ]
    )
    assert code == 0
    assert "puede archivarlo" in report.read_text(encoding="utf-8")
    assert (inbox / "nota.txt").is_file()


def test_error_si_la_bandeja_no_existe(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["ordenar", str(tmp_path / "no"), "--destino", str(tmp_path / "out")])
    assert code == 1
    assert "no existe" in capsys.readouterr().err


def test_reglas_se_pueden_volver_a_cargar(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["reglas"])
    assert code == 0
    path = tmp_path / "reglas.toml"
    path.write_text(capsys.readouterr().out, encoding="utf-8")
    assert load_rules(path) == default_rules()


def test_ejemplo_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    folder = tmp_path / "bandeja"
    assert main(["ejemplo", str(folder)]) == 0
    assert (folder / "factura-marzo.pdf").is_file()
    assert (folder / "enlace-factura.pdf").is_symlink()
    assert main(["ejemplo", str(folder)]) == 1
    assert "ya existe" in capsys.readouterr().err


def test_uso_incorrecto() -> None:
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_version() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_modulo(tmp_path: Path) -> None:
    inbox = tmp_path / "in"
    inbox.mkdir()
    (inbox / "hola.txt").write_text("hola", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bandeja",
            "ordenar",
            str(inbox),
            "--destino",
            str(tmp_path / "out"),
            "--simular",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr
    assert "simulación" in completed.stdout
    assert (inbox / "hola.txt").is_file()
