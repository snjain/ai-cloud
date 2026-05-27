"""Smoke tests for the AI Cloud platform."""

import pytest


def test_imports():
    """Verify core dependencies are importable."""
    import fastapi
    import pydantic_ai
    import langgraph
    import openai
    import supabase

    assert fastapi.__version__


def test_env_file_exists():
    """Verify .env file is present."""
    from pathlib import Path

    env_path = Path(__file__).resolve().parent.parent / ".env"
    assert env_path.exists(), ".env file not found at project root"


@pytest.mark.smoke
def test_project_structure():
    """Verify key project directories exist."""
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    assert (root / "apps" / "agent-backend").exists()
    assert (root / "apps" / "agent-frontend").exists()
    assert (root / "apps" / "rag-pipeline").exists()
    assert (root / "infra").exists()
