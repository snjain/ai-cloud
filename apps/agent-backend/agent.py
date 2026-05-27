"""Main Pydantic AI agent definition."""
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, RunContext
from typing import List

from config import settings
from prompt import AGENT_SYSTEM_PROMPT
from deps import AgentDeps
from tools import (
    web_search_tool,
    retrieve_relevant_documents_tool,
    list_documents_tool,
    get_document_content_tool,
    execute_sql_query_tool,
    image_analysis_tool,
    execute_safe_code_tool,
)


_agent = None


def get_model():
    return OpenAIModel(
        settings.llm_choice,
        provider=OpenAIProvider(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key or "dummy-key-for-import",
        ),
    )


def get_agent():
    global _agent
    if _agent is None:
        _agent = Agent(
            get_model(),
            system_prompt=AGENT_SYSTEM_PROMPT,
            deps_type=AgentDeps,
            retries=2,
        )

        @_agent.system_prompt
        def add_memories(ctx: RunContext[AgentDeps]) -> str:
            return f"\nUser Memories:\n{ctx.deps.memories}"

        @_agent.tool
        async def web_search(ctx: RunContext[AgentDeps], query: str) -> str:
            """Search the web with a specific query and get a summary of top results."""
            print("Calling web_search tool")
            return await web_search_tool(query, ctx.deps.http_client, ctx.deps.brave_api_key)

        @_agent.tool
        async def retrieve_relevant_documents(ctx: RunContext[AgentDeps], user_query: str) -> str:
            """Retrieve relevant document chunks based on the query with RAG."""
            print("Calling retrieve_relevant_documents tool")
            return await retrieve_relevant_documents_tool(
                ctx.deps.supabase, ctx.deps.embedding_client, user_query
            )

        @_agent.tool
        async def list_documents(ctx: RunContext[AgentDeps]) -> List[str]:
            """Retrieve a list of all available documents."""
            print("Calling list_documents tool")
            return await list_documents_tool(ctx.deps.supabase)

        @_agent.tool
        async def get_document_content(ctx: RunContext[AgentDeps], document_id: str) -> str:
            """Retrieve the full content of a specific document by combining all its chunks."""
            print("Calling get_document_content tool")
            return await get_document_content_tool(ctx.deps.supabase, document_id)

        @_agent.tool
        async def execute_sql_query(ctx: RunContext[AgentDeps], sql_query: str) -> str:
            """Run a read-only SQL query against the document_rows table."""
            print(f"Calling execute_sql_query tool with SQL: {sql_query}")
            return await execute_sql_query_tool(ctx.deps.supabase, sql_query)

        @_agent.tool
        async def image_analysis(ctx: RunContext[AgentDeps], document_id: str, query: str) -> str:
            """Analyze an image based on the document ID using a vision LLM."""
            print("Calling image_analysis tool")
            return await image_analysis_tool(ctx.deps.supabase, document_id, query)

        @_agent.tool
        async def execute_code(ctx: RunContext[AgentDeps], code: str) -> str:
            """Execute Python code in a restricted sandbox. Use print for output."""
            print(f"Executing code: {code}")
            return execute_safe_code_tool(code)

    return _agent


# Module-level alias for backward compatibility
agent = get_agent()
