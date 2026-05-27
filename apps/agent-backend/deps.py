"""Agent dependencies dataclass."""
from dataclasses import dataclass
from openai import AsyncOpenAI
from httpx import AsyncClient
from supabase import Client


@dataclass
class AgentDeps:
    supabase: Client
    embedding_client: AsyncOpenAI
    http_client: AsyncClient
    brave_api_key: str | None
    memories: str
