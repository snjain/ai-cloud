"""Tests for parallel graph architecture."""

import pytest


def test_parallel_imports():
    """Verify parallel graph module imports."""
    from graphs.parallel_graph import create_workflow

    assert callable(create_workflow)
