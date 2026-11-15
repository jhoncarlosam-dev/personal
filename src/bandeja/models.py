"""Datos que comparten la clasificación, el archivo y el reporte."""

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Rule:
    category: str
    extensions: frozenset[str]
    patterns: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Classification:
    category: str
    reason: str


@dataclass(frozen=True, slots=True)
class ExpenseSummary:
    source: str
    rows: int
    skipped: int
    total: Decimal
    by_category: dict[str, Decimal]


@dataclass(frozen=True, slots=True)
class Action:
    source: Path
    destination: Path
    category: str
    reason: str
    sha256: str
    duplicate_of: Path | None = None


@dataclass(slots=True)
class Result:
    inbox: Path
    destination: Path
    simulated: bool
    actions: list[Action] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    expenses: list[ExpenseSummary] = field(default_factory=list)
    hidden: int = 0

    @property
    def archived(self) -> list[Action]:
        return [action for action in self.actions if action.reason != "duplicado"]

    @property
    def duplicates(self) -> list[Action]:
        return [action for action in self.actions if action.reason == "duplicado"]
