"""Tests for the Nous-Private-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"Private"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``Private-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "Private" tag namespace.

``is_nous_Private_non_agentic`` should only match the actual Nous Research
Private-3 / Private-4 chat family.
"""

from __future__ import annotations

import pytest

from Private_cli.model_switch import (
    _Private_MODEL_WARNING,
    _check_Private_model_warning,
    is_nous_Private_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "NousResearch/Private-3-Llama-3.1-70B",
        "NousResearch/Private-3-Llama-3.1-405B",
        "Private-3",
        "Private-3",
        "Private-4",
        "Private-4-405b",
        "Private_4_70b",
        "openrouter/Private3:70b",
        "openrouter/nousresearch/Private-4-405b",
        "NousResearch/Private3",
        "Private-3.1",
    ],
)
def test_matches_real_nous_Private_chat_models(model_name: str) -> None:
    assert is_nous_Private_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Nous Private 3/4"
    )
    assert _check_Private_model_warning(model_name) == _Private_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "Private-brain:qwen3-14b-ctx16k",
        "Private-brain:qwen3-14b-ctx32k",
        "Private-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat Private models we don't warn about
        "Private-llm-2",
        "Private2-pro",
        "nous-Private-2-mistral",
        # Edge cases
        "",
        "Private",  # bare "Private" isn't the 3/4 family
        "Private-brain",
        "brain-Private-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_Private_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Nous Private 3/4"
    )
    assert _check_Private_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_Private_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_Private_model_warning("") == ""
