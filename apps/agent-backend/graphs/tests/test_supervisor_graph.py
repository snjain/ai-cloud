"""Tests for supervisor graph architecture."""

import pytest


def test_supervisor_imports():
    """Verify supervisor graph module imports."""
    from graphs.supervisor_graph import create_workflow

    assert callable(create_workflow)


def test_supervisor_state_model():
    """Verify supervisor state model exists."""
    from graphs.supervisor_graph import SupervisorState

    assert SupervisorState is not None
