"""Tests for routing graph architecture."""

import pytest


def test_routing_imports():
    """Verify routing graph module imports."""
    from graphs.routing_graph import create_workflow

    assert callable(create_workflow)


def test_router_state_model():
    """Verify router state model exists."""
    from graphs.routing_graph import RouterState

    assert RouterState is not None
