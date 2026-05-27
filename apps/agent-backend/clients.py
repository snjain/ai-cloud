"""Client setup for LLMs, databases, and memory."""
from mem0 import Memory
from openai import AsyncOpenAI
from supabase import Client
import os

from config import settings


def get_embedding_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=settings.embedding_base_url,
        api_key=settings.embedding_api_key or settings.llm_api_key,
    )


def get_supabase_client() -> Client:
    return Client(settings.supabase_url, settings.supabase_service_key)


def get_mem0_config():
    """Build Mem0 configuration for cloud providers."""
    config = {}

    # LLM config
    if settings.llm_provider in ("openai", "openrouter"):
        config["llm"] = {
            "provider": "openai",
            "config": {
                "model": settings.llm_choice,
                "temperature": 0.2,
                "max_tokens": 2000,
            },
        }
        if settings.llm_provider == "openai" and settings.llm_api_key:
            os.environ["OPENAI_API_KEY"] = settings.llm_api_key
        if settings.llm_provider == "openrouter" and settings.llm_api_key:
            os.environ["OPENROUTER_API_KEY"] = settings.llm_api_key

    # Embedder config
    if settings.embedding_provider == "openai":
        config["embedder"] = {
            "provider": "openai",
            "config": {
                "model": settings.embedding_model_choice or "text-embedding-3-small",
                "embedding_dims": 1536,
            },
        }
        if settings.embedding_api_key:
            os.environ["OPENAI_API_KEY"] = settings.embedding_api_key

    # Vector store config (Supabase)
    config["vector_store"] = {
        "provider": "supabase",
        "config": {
            "connection_string": settings.resolved_database_url,
            "collection_name": "mem0_memories",
            "embedding_model_dims": 1536,
        },
    }

    return config


def get_mem0_client() -> Memory:
    return Memory.from_config(get_mem0_config())
