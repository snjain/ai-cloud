"""CLI interface for testing the agent."""
import asyncio
from httpx import AsyncClient
import os

from agent import agent
from deps import AgentDeps
from clients import get_embedding_client, get_supabase_client, get_mem0_client


async def main():
    print("🤖 AI Cloud Agent CLI")
    print("Type 'exit' to quit\n")

    embedding_client = get_embedding_client()
    supabase = get_supabase_client()
    memory = get_mem0_client()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        relevant_memories = memory.search(query=user_input, filters={"user_id": "cli_user"}, limit=3)
        memories_str = "\n".join(
            f"- {entry['memory']}" for entry in relevant_memories.get("results", [])
        )

        async with AsyncClient() as http_client:
            deps = AgentDeps(
                supabase=supabase,
                embedding_client=embedding_client,
                http_client=http_client,
                brave_api_key=os.getenv("BRAVE_API_KEY"),
                memories=memories_str,
            )
            result = await agent.run(user_input, deps=deps)

        print(f"\nAgent: {result.output}\n")
        memory.add(
            [{"role": "user", "content": user_input}],
            user_id="cli_user",
        )


if __name__ == "__main__":
    asyncio.run(main())
