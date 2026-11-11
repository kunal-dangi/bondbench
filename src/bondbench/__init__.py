"""bondbench: evaluate LLMs on fixed-income and fund-operations questions."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from .checks import json_check, keyword_check, numeric_check, refusal_check
from .goldset import GoldItem, GoldSetError, builtin_goldsets, load_goldset
from .providers import Completion, register_provider
from .runner import grade, run, score, summarize, to_markdown

try:
    __version__ = _version("bondbench")
except PackageNotFoundError:  # running from a source checkout without installing
    __version__ = "0.0.0"

__all__ = [
    "Completion",
    "GoldItem",
    "GoldSetError",
    "builtin_goldsets",
    "grade",
    "json_check",
    "keyword_check",
    "load_goldset",
    "numeric_check",
    "refusal_check",
    "register_provider",
    "run",
    "score",
    "summarize",
    "to_markdown",
]
