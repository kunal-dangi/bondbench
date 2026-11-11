"""Load and validate gold sets.

A gold set is a CSV with one question per row. Required columns:

``id``, ``category``, ``question``

Optional columns:

``checks``             which checks to run, separated by ``;``
                       (``keyword``, ``refusal``, ``json``, ``numeric``)
``expected_keywords``  for ``keyword``: pass if any of these appear (``;`` separated)
``must_not_contain``   for ``keyword``: fail if any of these appear
``answer_key``         for ``numeric``: the JSON key holding the answer
``answer_value``       for ``numeric``: the correct number
``tolerance``          for ``numeric``: allowed absolute error (default 0.01)

If ``checks`` is missing or blank for a row, it is inferred: ``keyword`` when
keywords are given, ``refusal`` when the category is ``refusal``, and ``json``
when the question mentions JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import pandas as pd

KNOWN_CHECKS = ("keyword", "refusal", "json", "numeric")
REQUIRED_COLUMNS = ("id", "category", "question")
DEFAULT_TOLERANCE = 0.01
_DATA_PACKAGE = "bondbench.data"


class GoldSetError(ValueError):
    """Raised when a gold set file is malformed."""


@dataclass(frozen=True)
class GoldItem:
    id: str
    category: str
    question: str
    checks: tuple[str, ...]
    expected_keywords: tuple[str, ...] = ()
    must_not_contain: tuple[str, ...] = ()
    answer_key: str | None = None
    answer_value: float | None = None
    tolerance: float = DEFAULT_TOLERANCE


def builtin_goldsets() -> list[str]:
    """Names of the gold sets shipped with the package."""
    files = resources.files(_DATA_PACKAGE).iterdir()
    return sorted(f.name[:-4] for f in files if f.name.endswith(".csv"))


def _split(cell: str) -> tuple[str, ...]:
    return tuple(p.strip() for p in cell.split(";") if p.strip())


def _infer_checks(category: str, question: str, has_keywords: bool) -> tuple[str, ...]:
    checks = []
    if has_keywords:
        checks.append("keyword")
    if category.lower() == "refusal":
        checks.append("refusal")
    if "json" in question.lower():
        checks.append("json")
    return tuple(checks)


def _read(source: str | Path) -> tuple[pd.DataFrame, str]:
    if isinstance(source, str) and source in builtin_goldsets():
        ref = resources.files(_DATA_PACKAGE) / f"{source}.csv"
        with resources.as_file(ref) as path:
            return pd.read_csv(path, dtype=str, keep_default_na=False), source
    path = Path(source)
    if not path.exists():
        names = ", ".join(builtin_goldsets())
        raise GoldSetError(f"No gold set at '{source}'. Built-in gold sets: {names}")
    try:
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    except pd.errors.ParserError as exc:
        raise GoldSetError(
            f"{path}: could not parse the CSV ({exc}). A comma inside a question "
            "needs the whole field wrapped in double quotes."
        ) from exc
    return frame, str(path)


def load_goldset(source: str | Path) -> list[GoldItem]:
    """Load a built-in gold set by name, or a CSV file by path."""
    frame, label = _read(source)
    frame.columns = [c.strip() for c in frame.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise GoldSetError(
            f"{label}: missing column(s) {missing}. Found {list(frame.columns)}. "
            "Check that the header is on the first line of the file."
        )

    def cell(row: pd.Series, name: str) -> str:
        return str(row[name]).strip() if name in row.index else ""

    items: list[GoldItem] = []
    seen: set[str] = set()
    for line_no, (_, row) in enumerate(frame.iterrows(), start=2):
        qid = cell(row, "id")
        where = f"{label}, line {line_no} (id '{qid}')"
        if not qid:
            raise GoldSetError(f"{label}, line {line_no}: empty id")
        if qid in seen:
            raise GoldSetError(f"{where}: duplicate id")
        seen.add(qid)

        question = cell(row, "question")
        if not question:
            raise GoldSetError(f"{where}: empty question")
        category = cell(row, "category")
        expected = _split(cell(row, "expected_keywords"))
        forbidden = _split(cell(row, "must_not_contain"))

        checks = _split(cell(row, "checks").lower())
        if not checks:
            checks = _infer_checks(category, question, bool(expected))
        unknown = [c for c in checks if c not in KNOWN_CHECKS]
        if unknown:
            raise GoldSetError(f"{where}: unknown check(s) {unknown}. Known: {list(KNOWN_CHECKS)}")
        if not checks:
            raise GoldSetError(
                f"{where}: no checks to run. Add expected_keywords or a checks value."
            )

        answer_key = cell(row, "answer_key") or None
        answer_value: float | None = None
        tolerance = DEFAULT_TOLERANCE
        if "numeric" in checks:
            raw_value = cell(row, "answer_value")
            if not answer_key or not raw_value:
                raise GoldSetError(f"{where}: the numeric check needs answer_key and answer_value")
            try:
                answer_value = float(raw_value)
                raw_tol = cell(row, "tolerance")
                tolerance = float(raw_tol) if raw_tol else DEFAULT_TOLERANCE
            except ValueError as exc:
                raise GoldSetError(f"{where}: answer_value and tolerance must be numbers") from exc

        items.append(
            GoldItem(
                id=qid,
                category=category,
                question=question,
                checks=checks,
                expected_keywords=expected,
                must_not_contain=forbidden,
                answer_key=answer_key,
                answer_value=answer_value,
                tolerance=tolerance,
            )
        )

    if not items:
        raise GoldSetError(f"{label}: no questions found")
    return items
