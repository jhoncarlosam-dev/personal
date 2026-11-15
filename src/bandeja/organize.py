"""Planifica y ejecuta el archivo de una bandeja."""

import csv
import hashlib
import os
import shutil
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from bandeja.classify import REASON_DUPLICATE, classify
from bandeja.errors import BandejaError, EjecucionError
from bandeja.expenses import summarize_expenses
from bandeja.models import Action, ExpenseSummary, Result, Rule
from bandeja.rules import default_rules, validate_rules


def organize(
    inbox: Path,
    destination: Path,
    rules: Sequence[Rule] | None = None,
    *,
    simulate: bool = False,
    recursive: bool = False,
    index_destination: bool = True,
    rules_path: Path | None = None,
) -> Result:
    """Archiva los archivos de ``inbox`` dentro de ``destination``.

    No borra duplicados: los aparta en ``_duplicados``. Con ``simulate`` no
    crea carpetas ni mueve nada, pero el resultado describe el plan y, si hay
    CSV de gastos, los totales. Un CSV idéntico a otro ya contado no se suma
    otra vez.
    """
    inbox, destination = _prepare(inbox, destination)
    active = validate_rules(default_rules() if rules is None else rules)
    result = Result(inbox=inbox, destination=destination, simulated=simulate)
    known = _index(destination, result) if index_destination else {}
    reserved: set[Path] = set()
    ignored_rules = rules_path.resolve() if rules_path is not None else None

    for path in _candidates(inbox, recursive):
        relative = _relative(path, inbox)
        if _hidden(path, inbox):
            result.hidden += 1
            continue
        if ignored_rules is not None and path.resolve() == ignored_rules:
            continue
        if path.is_symlink():
            result.warnings.append(f"Se omitió el enlace simbólico {relative}")
            continue
        if not path.is_file():
            continue
        try:
            digest = file_sha256(path)
        except OSError as exc:
            result.warnings.append(f"No se pudo leer {relative}: {exc.strerror or exc}")
            continue

        duplicate_of = known.get(digest)
        if duplicate_of is not None:
            category = "_duplicados"
            reason = REASON_DUPLICATE
            planned = destination / "_duplicados" / path.name
        else:
            classification = classify(path.name, active)
            category = classification.category
            reason = classification.reason
            modified = datetime.fromtimestamp(path.stat().st_mtime)
            planned = (
                destination / category / f"{modified:%Y}" / f"{modified:%m}" / path.name
            )

        planned = _free_path(planned, reserved)
        reserved.add(planned)
        if duplicate_of is None:
            known[digest] = planned

        file_warnings: list[str] = []
        summary = None
        if duplicate_of is None and path.suffix.casefold() == ".csv":
            summary = _expenses_for(path, file_warnings)

        if not simulate:
            try:
                _move(path, planned)
            except OSError as exc:
                raise EjecucionError(
                    f"no se pudo mover {relative}: {exc.strerror or exc}",
                    result,
                ) from exc

        result.actions.append(
            Action(
                source=path,
                destination=planned,
                category=category,
                reason=reason,
                sha256=digest,
                duplicate_of=duplicate_of,
            )
        )
        if summary is not None:
            result.expenses.append(summary)
        result.warnings.extend(file_warnings)
    return result


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _prepare(inbox: Path, destination: Path) -> tuple[Path, Path]:
    if not inbox.exists():
        raise BandejaError(f"no existe la bandeja: {inbox}")
    if not inbox.is_dir():
        raise BandejaError(f"la bandeja no es una carpeta: {inbox}")
    if destination.exists() and not destination.is_dir():
        raise BandejaError(f"el destino no es una carpeta: {destination}")
    inbox_resolved = inbox.resolve()
    destination_resolved = destination.resolve()
    overlaps = (
        inbox_resolved == destination_resolved
        or destination_resolved.is_relative_to(inbox_resolved)
        or inbox_resolved.is_relative_to(destination_resolved)
    )
    if overlaps:
        raise BandejaError(
            "el destino no puede ser la bandeja ni estar dentro de ella, ni al revés"
        )
    return inbox_resolved, destination_resolved


def _candidates(inbox: Path, recursive: bool) -> list[Path]:
    if recursive:
        found = [
            path for path in inbox.rglob("*") if path.is_file() or path.is_symlink()
        ]
    else:
        found = [
            path for path in inbox.iterdir() if path.is_file() or path.is_symlink()
        ]
    return sorted(found, key=lambda path: _relative(path, inbox).casefold())


def _hidden(path: Path, inbox: Path) -> bool:
    return any(part.startswith(".") for part in path.relative_to(inbox).parts)


def _index(destination: Path, result: Result) -> dict[str, Path]:
    found: dict[str, Path] = {}
    if not destination.exists():
        return found
    files = [
        path
        for path in destination.rglob("*")
        if path.is_file() and not path.is_symlink()
    ]
    for path in sorted(files, key=lambda item: item.as_posix().casefold()):
        try:
            digest = file_sha256(path)
        except OSError as exc:
            result.warnings.append(
                f"No se pudo leer {path.name} en el destino: {exc.strerror or exc}"
            )
            continue
        found.setdefault(digest, path)
    return found


def _free_path(path: Path, reserved: set[Path]) -> Path:
    candidate = path
    number = 2
    while candidate in reserved or candidate.is_symlink() or candidate.exists():
        candidate = path.with_name(f"{path.stem}-{number}{path.suffix}")
        number += 1
        if number > 10_000:
            raise BandejaError(f"hay demasiados archivos llamados {path.name}")
    return candidate


def _move(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(os.fspath(source), os.fspath(destination))


def _expenses_for(path: Path, warnings: list[str]) -> ExpenseSummary | None:
    try:
        summary = summarize_expenses(path)
    except (OSError, csv.Error) as exc:
        warnings.append(f"No se pudo leer {path.name} como CSV: {exc}")
        return None
    if summary is None:
        return None
    if summary.rows == 0 and summary.skipped == 0:
        warnings.append(f"{path.name}: tiene columnas de gastos, pero ninguna fila")
    elif summary.skipped or summary.rows == 0:
        warnings.append(
            f"{path.name}: {_count(summary.rows, 'fila válida', 'filas válidas')}, "
            f"{_count(summary.skipped, 'fila omitida', 'filas omitidas')}"
        )
    return summary


def _count(amount: int, singular: str, plural: str) -> str:
    if amount == 1:
        return f"1 {singular}"
    return f"{amount} {plural}"


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name
