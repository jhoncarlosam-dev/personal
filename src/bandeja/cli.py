"""Comandos de consola de bandeja."""

import argparse
import sys
from pathlib import Path

from bandeja import __version__
from bandeja.demo import create_example
from bandeja.errors import BandejaError, EjecucionError
from bandeja.models import Result
from bandeja.organize import organize
from bandeja.report import render_json, render_report
from bandeja.rules import default_rules, load_rules, rules_to_toml

_EXAMPLES = """ejemplos:
  bandeja ejemplo ejemplos/bandeja
  bandeja ordenar ejemplos/bandeja --destino ejemplos/archivo --simular
  bandeja ordenar ejemplos/bandeja --destino ejemplos/archivo --reporte ejemplos/reporte.md
  bandeja reglas > mis-reglas.toml
"""


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.comando == "reglas":
            sys.stdout.write(rules_to_toml(default_rules()))
            return 0
        if args.comando == "ejemplo":
            return _example(args.carpeta)
        if args.comando == "ordenar":
            return _sort(args)
    except EjecucionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        if exc.result.actions:
            sys.stderr.write(render_report(exc.result))
        return 1
    except BandejaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 2


def cli() -> None:
    sys.exit(main())


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bandeja",
        description="Archiva una carpeta por categoría y mes, y resume los CSV de gastos.",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    commands = parser.add_subparsers(dest="comando", required=True)

    example = commands.add_parser("ejemplo", help="crea una bandeja de demostración")
    example.add_argument("carpeta", type=_path, help="carpeta nueva que se va a crear")

    sort = commands.add_parser("ordenar", help="clasifica y archiva la bandeja")
    sort.add_argument("bandeja", type=_path, help="carpeta de entrada")
    sort.add_argument(
        "--destino", type=_path, required=True, help="carpeta donde se archiva"
    )
    sort.add_argument(
        "--reglas",
        type=_path,
        help="archivo TOML; si se omite, usa las reglas internas",
    )
    sort.add_argument(
        "--simular",
        action="store_true",
        help="muestra el plan y los totales sin mover archivos ni crear carpetas",
    )
    sort.add_argument(
        "--recursivo", action="store_true", help="incluye las subcarpetas"
    )
    sort.add_argument(
        "--sin-indice",
        action="store_true",
        help="no compara el contenido con lo ya archivado",
    )
    sort.add_argument(
        "--reporte", type=_path, help="escribe el reporte Markdown en esta ruta"
    )
    sort.add_argument(
        "--json", type=_path, dest="json_path", help="escribe el resultado en JSON"
    )

    commands.add_parser("reglas", help="imprime las reglas internas en TOML")
    return parser


def _example(folder: Path) -> int:
    created = create_example(folder)
    suggested = created.parent / "archivo"
    print(f"Bandeja de ejemplo lista en {created}")
    print("Siguiente paso:")
    print(f"  bandeja ordenar {created} --destino {suggested} --simular")
    return 0


def _sort(args: argparse.Namespace) -> int:
    rules = load_rules(args.reglas) if args.reglas else default_rules()
    result = organize(
        args.bandeja,
        args.destino,
        rules,
        simulate=args.simular,
        recursive=args.recursivo,
        index_destination=not args.sin_indice,
        rules_path=args.reglas,
    )
    _flag_if_inside(result, args.reporte, "reporte")
    _flag_if_inside(result, args.json_path, "JSON")
    report = render_report(result)
    sys.stdout.write(report)
    if args.reporte is not None:
        _write(args.reporte, report)
    if args.json_path is not None:
        _write(args.json_path, render_json(result))
    return 0


def _flag_if_inside(result: Result, path: Path | None, label: str) -> None:
    if path is None:
        return
    resolved = path.resolve()
    if resolved == result.inbox or resolved.is_relative_to(result.inbox):
        result.warnings.append(
            f"El {label} está dentro de la bandeja; la próxima ejecución puede archivarlo"
        )


def _write(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise BandejaError(
            f"no se pudo escribir {path}: {exc.strerror or exc}"
        ) from exc


def _path(value: str) -> Path:
    return Path(value).expanduser()
