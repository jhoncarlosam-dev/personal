"""Carga y valida las reglas de clasificación en TOML."""

import tomllib
from collections.abc import Sequence
from pathlib import Path

from bandeja.errors import BandejaError
from bandeja.models import Rule

_FIELDS = {"categoria", "extensiones", "patrones"}


def default_rules() -> list[Rule]:
    """Reglas de una bandeja personal: comprobantes, medios y documentos."""
    rules = [
        Rule(
            "comprobantes",
            frozenset({"pdf", "xml", "jpg", "jpeg", "png", "zip"}),
            ("factura", "recibo", "invoice", "comprobante", "nota-credito"),
        ),
        Rule("imagenes", frozenset({"jpg", "jpeg", "png", "gif", "webp", "heic"}), ()),
        Rule(
            "documentos",
            frozenset({"pdf", "doc", "docx", "txt", "md", "odt", "rtf"}),
            (),
        ),
        Rule("hojas", frozenset({"csv", "tsv", "xls", "xlsx", "ods"}), ()),
        Rule("audio", frozenset({"mp3", "wav", "flac", "m4a", "aac"}), ()),
        Rule("video", frozenset({"mp4", "mov", "mkv", "avi", "webm"}), ()),
        Rule("comprimidos", frozenset({"zip", "gz", "tgz", "bz2", "7z", "rar"}), ()),
        Rule(
            "codigo",
            frozenset(
                {
                    "py",
                    "js",
                    "ts",
                    "tsx",
                    "jsx",
                    "json",
                    "html",
                    "css",
                    "toml",
                    "yml",
                    "yaml",
                    "sh",
                }
            ),
            (),
        ),
    ]
    return validate_rules(rules)


def load_rules(path: Path) -> list[Rule]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise BandejaError(f"no se pudo leer {path}: {exc.strerror or exc}") from exc
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise BandejaError(f"TOML inválido en {path}: {exc}") from exc

    entries = data.get("regla")
    if isinstance(entries, dict):
        raise BandejaError("usa [[regla]] para cada regla, no [regla]")
    if not isinstance(entries, list) or not entries:
        raise BandejaError("el archivo debe incluir al menos una tabla [[regla]]")

    rules: list[Rule] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise BandejaError("cada [[regla]] debe ser una tabla")
        unknown = sorted(set(entry) - _FIELDS)
        if unknown:
            raise BandejaError(
                f"campos desconocidos en una regla: {', '.join(unknown)}"
            )
        category = entry.get("categoria")
        if not isinstance(category, str):
            raise BandejaError('cada regla necesita categoria = "..."')
        rules.append(
            Rule(
                category,
                frozenset(_strings(entry.get("extensiones"), "extensiones")),
                tuple(_strings(entry.get("patrones"), "patrones")),
            )
        )
    return validate_rules(rules)


def validate_rules(rules: Sequence[Rule]) -> list[Rule]:
    if not rules:
        raise BandejaError("no hay reglas")
    checked: list[Rule] = []
    seen: dict[str, str] = {}
    for rule in rules:
        category = _category(rule.category)
        extensions = frozenset(_extension(item) for item in rule.extensions)
        patterns = tuple(_pattern(item) for item in rule.patterns)
        if not extensions and not patterns:
            raise BandejaError(
                f"la regla {category!r} no tiene extensiones ni patrones"
            )
        if not patterns:
            for extension in sorted(extensions):
                previous = seen.get(extension)
                if previous is not None:
                    raise BandejaError(
                        f"la extensión .{extension} está en {previous!r} y en {category!r}"
                    )
                seen[extension] = category
        checked.append(Rule(category, extensions, patterns))
    return checked


def rules_to_toml(rules: Sequence[Rule]) -> str:
    blocks: list[str] = []
    for rule in rules:
        lines = ["[[regla]]", f"categoria = {_quote(rule.category)}"]
        if rule.extensions:
            lines.append(f"extensiones = [{_quoted_list(sorted(rule.extensions))}]")
        if rule.patterns:
            lines.append(f"patrones = [{_quoted_list(rule.patterns)}]")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _strings(value: object, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise BandejaError(f"{field} debe ser una lista de textos")
    return [item.strip() for item in value]


def _category(value: str) -> str:
    text = value.strip()
    invalid = (
        not text
        or text in {".", ".."}
        or text.startswith((".", "_"))
        or any(char in text for char in "/\\\0\n\r\t")
    )
    if invalid:
        raise BandejaError(f"categoría inválida: {value!r}")
    return text


def _extension(value: str) -> str:
    text = value.strip().casefold().lstrip(".")
    if not text or any(char in text for char in "./\\"):
        raise BandejaError(f"extensión inválida: {value!r}")
    return text


def _pattern(value: str) -> str:
    text = value.strip()
    if not text:
        raise BandejaError("hay un patrón vacío")
    return text


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _quoted_list(values: Sequence[str]) -> str:
    return ", ".join(_quote(value) for value in values)
