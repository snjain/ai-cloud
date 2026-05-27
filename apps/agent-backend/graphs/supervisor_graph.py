"""Supervisor Agent Architecture with LangGraph (Module 7.7)."""
import os
from typing import Optional, List
from dataclasses import dataclass

from langgraph.graph import StateGraph, START, END
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from openai import AsyncOpenAI
from httpx import AsyncClient
from supabase import Client

from graphs.state import SupervisorState
from graphs.utils import get_model, stream_agent_response
from tools.web_search import web_search_tool
from tools.rag_search import retrieve_relevant_documents_tool
from tools.code_execution import execute_safe_code_tool
from tools.sql_query import execute_sql_query_tool


@dataclass
class SupervisorDeps:
    shared_context: str
    iteration: int


@dataclass
class SubAgentDeps:
    supabase: Client
    embedding_client: AsyncOpenAI
    http_client: AsyncClient
    brave_api_key: Optional[str]


def _create_sub_deps():
    from clients import get_embedding_client, get_supabase_client
    return SubAgentDeps(
        supabase=get_supabase_client(),
        embedding_client=get_embedding_client(),
        http_client=AsyncClient(),
        brave_api_key=os.getenv("BRAVE_API_KEY") or None,
    )


SUPERVISOR_PROMPT = """You are a supervisor agent that orchestrates specialized sub-agents.

Your task: analyze the user's request and accumulated context, then decide the next action.

Options:
- "web_research": Delegate to web research agent
- "rag_search": Delegate to document research agent
- "code_execution": Delegate to code execution agent
- "sql_query": Delegate to SQL query agent
- "final_response": Provide the final answer directly

When delegating, be specific about what the sub-agent should do.
When responding directly, give a comprehensive answer based on all context.

Max iterations: 5. After that you MUST provide a final_response."""

supervisor_agent = Agent(get_model(), system_prompt=SUPERVISOR_PROMPT)

WEB_PROMPT = "Web research specialist. Search the web and summarize findings concisely."
RAG_PROMPT = "Document research specialist. Search knowledge base and cite sources."
CODE_PROMPT = "Code execution specialist. Run Python and explain results."
SQL_PROMPT = "SQL query specialist. Execute SELECT queries and present results."

web_agent = Agent(get_model(), system_prompt=WEB_PROMPT, deps_type=SubAgentDeps)
rag_agent = Agent(get_model(), system_prompt=RAG_PROMPT, deps_type=SubAgentDeps)
code_agent = Agent(get_model(), system_prompt=CODE_PROMPT, deps_type=SubAgentDeps)
sql_agent = Agent(get_model(), system_prompt=SQL_PROMPT, deps_type=SubAgentDeps)


@web_agent.tool
async def search_web(ctx: RunContext[SubAgentDeps], query: str) -> str:
    return await web_search_tool(query, ctx.deps.http_client, ctx.deps.brave_api_key)


@rag_agent.tool
async def search_docs(ctx: RunContext[SubAgentDeps], query: str) -> str:
    return await retrieve_relevant_documents_tool(ctx.deps.supabase, ctx.deps.embedding_client, query)


@code_agent.tool
async def run_code(ctx: RunContext[SubAgentDeps], code: str) -> str:
    return execute_safe_code_tool(code)


@sql_agent.tool
async def run_sql(ctx: RunContext[SubAgentDeps], query: str) -> str:
    return await execute_sql_query_tool(ctx.deps.supabase, query)


MAX_ITERATIONS = 5


async def supervisor_node(state: SupervisorState, writer) -> dict:
    iteration = state.get("iteration_count", 0) + 1
    shared = "\n\n".join(state.get("shared_state", [])) or "No previous context."

    prompt = f"""User Query: {state['query']}

Iteration: {iteration}/{MAX_ITERATIONS}

Accumulated Context:
{shared}

Decide the next action. Output one of: web_research, rag_search, code_execution, sql_query, final_response
If delegating, specify the task. If final_response, provide the complete answer."""

    message_history = state.get("pydantic_message_history", [])
    result = await supervisor_agent.run(prompt, message_history=message_history)
    output = result.output.strip()

    decision = "final_response"
    task = output
    for d in ["web_research", "rag_search", "code_execution", "sql_query", "final_response"]:
        if output.lower().startswith(d):
            decision = d
            task = output[len(d):].strip(":-\n ")
            break

    if decision == "final_response" or iteration >= MAX_ITERATIONS:
        print("[supervisor] final response ready")
        return {"final_response": task, "iteration_count": iteration, "delegate_to": None}

    print(f"[supervisor] delegating to {decision}")
    return {"iteration_count": iteration, "delegate_to": decision, "reasoning": task}


async def sub_agent_node(state: SupervisorState, writer) -> dict:
    delegate = state.get("delegate_to")
    task = state.get("reasoning", state["query"])
    deps = _create_sub_deps()
    message_history = state.get("pydantic_message_history", [])

    agent_map = {
        "web_research": web_agent,
        "rag_search": rag_agent,
        "code_execution": code_agent,
        "sql_query": sql_agent,
    }

    selected_agent = agent_map.get(delegate)
    if not selected_agent:
        print(f"[supervisor] unknown agent: {delegate}")
        return {"shared_state": state.get("shared_state", []) + [f"Error: unknown agent {delegate}"]}

    full_response, _ = await stream_agent_response(selected_agent, task, deps, writer, message_history)
    summary = f"{delegate.upper()} RESULT:\n{full_response[:500]}"
    return {"shared_state": state.get("shared_state", []) + [summary]}


def route_after_supervisor(state: SupervisorState) -> str:
    if state.get("final_response"):
        return "end"
    if state.get("delegate_to"):
        return "sub_agent_node"
    return "end"


def route_after_sub_agent(state: SupervisorState) -> str:
    return "supervisor_node"


def create_workflow():
    builder = StateGraph(SupervisorState)
    builder.add_node("supervisor_node", supervisor_node)
    builder.add_node("sub_agent_node", sub_agent_node)

    builder.add_edge(START, "supervisor_node")
    builder.add_conditional_edges(
        "supervisor_node",
        route_after_supervisor,
        {"sub_agent_node": "sub_agent_node", "end": END},
    )
    builder.add_conditional_edges(
        "sub_agent_node",
        route_after_sub_agent,
        {"supervisor_node": "supervisor_node"},
    )

    return builder.compile()


workflow = create_workflow()


def create_initial_state(
    query: str,
    session_id: str,
    request_id: str,
    pydantic_message_history: Optional[List[ModelMessage]] = None,
) -> SupervisorState:
    return {
        "query": query,
        "session_id": session_id,
        "request_id": request_id,
        "shared_state": [],
        "iteration_count": 0,
        "delegate_to": None,
        "reasoning": "",
        "final_response": "",
        "streaming_success": True,
        "message_history": [],
        "pydantic_message_history": pydantic_message_history or [],
    }
