"""Token pricing, in USD per 1 million tokens.

Prices change. The defaults below are the list prices the original harness
used in late 2025; pass ``--pricing your_prices.json`` to override or extend
them. The JSON shape is::

    {"model-name": {"input": 0.15, "output": 0.60}}

A model with no price gets an empty cost instead of an error.
"""

from __future__ import annotations

import json
from pathlib import Path

PRICING_AS_OF = "late 2025"

DEFAULT_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"input": 0.150, "output": 0.600},
    "gpt-4o": {"input": 2.500, "output": 10.000},
    "claude-haiku-4-5-20251001": {"input": 1.000, "output": 5.000},
}


def load_pricing(path: str | Path | None = None) -> dict[str, dict[str, float]]:
    """Return the default prices, overridden by the JSON file at ``path``."""
    pricing = {model: dict(rates) for model, rates in DEFAULT_PRICING.items()}
    if path is None:
        return pricing
    data = json.loads(Path(path).read_text())
    for model, rates in data.items():
        if not {"input", "output"} <= set(rates):
            raise ValueError(f"Pricing for '{model}' needs 'input' and 'output' rates")
        pricing[model] = {"input": float(rates["input"]), "output": float(rates["output"])}
    return pricing


def cost_usd(
    model: str, prompt_tokens: int, completion_tokens: int, pricing: dict[str, dict[str, float]]
) -> float | None:
    """Cost of one request, or ``None`` if the model has no price."""
    rates = pricing.get(model)
    if rates is None:
        return None
    return (prompt_tokens * rates["input"] + completion_tokens * rates["output"]) / 1_000_000
