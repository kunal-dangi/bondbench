"""Model providers.

A model is named either explicitly as ``provider:model`` (``openai:gpt-4o``,
``anthropic:claude-haiku-4-5-20251001``, ``fake:demo``) or by its bare name,
in which case the provider is inferred from the prefix (``gpt-`` and the
``o`` reasoning series go to OpenAI, ``claude-`` goes to Anthropic).

SDKs are imported lazily, so you only need the extras for the providers you
actually call.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Completion:
    text: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int


class Provider(Protocol):
    def complete(
        self, model: str, system: str, prompt: str, *, temperature: float, max_tokens: int
    ) -> Completion: ...


def _missing_sdk(package: str) -> ImportError:
    return ImportError(
        f"The '{package}' package is not installed. Install it with: "
        f"pip install 'bondbench[{package}]'"
    )


class OpenAIProvider:
    """OpenAI chat completions. Reads ``OPENAI_API_KEY`` and ``OPENAI_BASE_URL``."""

    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise _missing_sdk("openai") from exc
            self._client = OpenAI()
        return self._client

    def complete(self, model, system, prompt, *, temperature, max_tokens):
        client = self._get_client()
        t0 = time.perf_counter()
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            seed=42,
            max_tokens=max_tokens,
        )
        return Completion(
            text=resp.choices[0].message.content or "",
            prompt_tokens=resp.usage.prompt_tokens,
            completion_tokens=resp.usage.completion_tokens,
            latency_ms=int((time.perf_counter() - t0) * 1000),
        )


class AnthropicProvider:
    """Anthropic Messages API. Reads ``ANTHROPIC_API_KEY``."""

    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic
            except ImportError as exc:
                raise _missing_sdk("anthropic") from exc
            self._client = Anthropic()
        return self._client

    def complete(self, model, system, prompt, *, temperature, max_tokens):
        client = self._get_client()
        t0 = time.perf_counter()
        resp = client.messages.create(
            model=model,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = "".join(getattr(block, "text", "") for block in resp.content)
        return Completion(
            text=text,
            prompt_tokens=resp.usage.input_tokens,
            completion_tokens=resp.usage.output_tokens,
            latency_ms=int((time.perf_counter() - t0) * 1000),
        )


class FakeProvider:
    """Offline provider for dry runs and tests. Costs nothing, needs no key.

    It echoes the question, so it exercises the whole pipeline but its scores
    mean nothing.
    """

    def complete(self, model, system, prompt, *, temperature, max_tokens):
        text = f"[fake:{model}] {prompt}"
        return Completion(
            text=text,
            prompt_tokens=len(system.split()) + len(prompt.split()),
            completion_tokens=len(text.split()),
            latency_ms=0,
        )


_FACTORIES: dict[str, Callable[[], Provider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "fake": FakeProvider,
}
_INSTANCES: dict[str, Provider] = {}

_OPENAI_PREFIXES = ("gpt-", "chatgpt-", "o1", "o3", "o4")
_ANTHROPIC_PREFIXES = ("claude-",)


def register_provider(name: str, factory: Callable[[], Provider]) -> None:
    """Register a provider so models can be named ``name:model``."""
    _FACTORIES[name] = factory
    _INSTANCES.pop(name, None)


def available_providers() -> list[str]:
    return sorted(_FACTORIES)


def parse_model_spec(spec: str) -> tuple[str, str]:
    """Split ``provider:model`` or infer the provider from a bare model name."""
    if ":" in spec:
        provider, model = spec.split(":", 1)
        if provider not in _FACTORIES:
            raise ValueError(
                f"Unknown provider '{provider}' in '{spec}'. Known: {available_providers()}"
            )
        if not model:
            raise ValueError(f"No model name in '{spec}'")
        return provider, model
    if spec.startswith(_OPENAI_PREFIXES):
        return "openai", spec
    if spec.startswith(_ANTHROPIC_PREFIXES):
        return "anthropic", spec
    raise ValueError(
        f"Can't tell which provider serves '{spec}'. Name it explicitly, "
        f"for example 'openai:{spec}'. Known providers: {available_providers()}"
    )


def get_provider(name: str) -> Provider:
    if name not in _INSTANCES:
        _INSTANCES[name] = _FACTORIES[name]()
    return _INSTANCES[name]
