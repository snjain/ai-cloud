"""Tests for API agent architectures."""

import pytest
from fastapi.testclient import TestClient


class TestPydanticAgentAPI:
    """Tests for the base Pydantic AI agent endpoint."""

    @pytest.mark.asyncio
    async def test_chat_endpoint_exists(self):
        """Verify the chat endpoint module imports correctly."""
        from api import app

        assert app is not None
        assert app.title == "AI Cloud Agent API"
