"""Clasifica un nombre de archivo. La primera regla que coincide gana."""

import unicodedata
from pathlib import Path

from bandeja.models import Classification, Rule

REASON_PATTERN = "patron"
REASON_EXTENSION = "extension"
REASON_OTHER = "otros"
REASON_DUPLICATE = "duplicado"


def classify(filename: str, rules: list[Rule] | tuple[Rule, ...]) -> Classification:
    stem = _fold_name(Path(filename).stem)
    extension = Path(filename).suffix.casefold().lstrip(".")
    for rule in rules:
        if not rule.patterns:
            continue
        if rule.extensions and extension not in rule.extensions:
            continue
        if any(_fold_name(pattern) in stem for pattern in rule.patterns):
            return Classification(rule.category, REASON_PATTERN)
    for rule in rules:
        if rule.patterns or not extension:
            continue
        if extension in rule.extensions:
            return Classification(rule.category, REASON_EXTENSION)
    return Classification("otros", REASON_OTHER)


def _fold_name(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.strip().casefold())
    without_marks = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return without_marks.replace("_", "-").replace(" ", "-")
