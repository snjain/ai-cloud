"""Tests for guardrail graph architecture."""

import pytest


def test_guardrail_imports():
    """Verify guardrail graph module imports."""
    from graphs.guardrail_graph import create_workflow

    assert callable(create_workflow)


def test_guardrail_state_model():
    """Verify guardrail state model exists."""
    from graphs.guardrail_graph import GuardrailState

    assert GuardrailState is not None
