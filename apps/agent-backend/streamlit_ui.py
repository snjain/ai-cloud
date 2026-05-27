"""Streamlit chat UI for the agent."""
from pydantic_ai.messages import ModelRequest, ModelResponse, PartDeltaEvent, PartStartEvent, TextPartDelta
from httpx import AsyncClient
import streamlit as st
import asyncio
import os

from agent import agent
from deps import AgentDeps
from clients import get_embedding_client, get_supabase_client, get_mem0_client


@st.cache_resource
def get_agent_deps():
    return get_embedding_client(), get_supabase_client()


@st.cache_resource(show_spinner=False)
def initialize_mem0():
    return get_mem0_client()


def display_message_part(part):
    if part.part_kind == "user-prompt" and part.content:
        with st.chat_message("user"):
            st.markdown(part.content)
    elif part.part_kind == "text" and part.content:
        with st.chat_message("assistant"):
            st.markdown(part.content)


async def run_agent_with_streaming(user_input):
    memory = initialize_mem0()
    relevant_memories = memory.search(query=user_input, filters={"user_id": "streamlit_user"}, limit=3)
    memories_str = "\n".join(
        f"- {entry['memory']}" for entry in relevant_memories.get("results", [])
    )

    embedding_client, supabase = get_agent_deps()

    async with AsyncClient() as http_client:
        agent_deps = AgentDeps(
            embedding_client=embedding_client,
            supabase=supabase,
            http_client=http_client,
            brave_api_key=os.getenv("BRAVE_API_KEY", ""),
            memories=memories_str,
        )

        async with agent.iter(user_input, deps=agent_deps, message_history=st.session_state.messages) as run:
            async for node in run:
                if agent.is_model_request_node(node):
                    async with node.stream(run.ctx) as request_stream:
                        async for event in request_stream:
                            if isinstance(event, PartStartEvent) and event.part.part_kind == "text":
                                yield event.part.content
                            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                                yield event.delta.content_delta

    st.session_state.messages.extend(run.result.new_messages())
    memory.add(
        [{"role": "user", "content": user_input}],
        user_id="streamlit_user",
    )


async def main():
    st.title("AI Cloud Agent")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        if isinstance(msg, ModelRequest) or isinstance(msg, ModelResponse):
            for part in msg.parts:
                display_message_part(part)

    user_input = st.chat_input("What do you want to do today?")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            async for message in run_agent_with_streaming(user_input):
                full_response += message
                placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)


if __name__ == "__main__":
    asyncio.run(main())
