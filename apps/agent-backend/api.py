"""FastAPI application for the AI agent."""
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from project root before any imports
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from httpx import AsyncClient
import os
import uuid

from agent import agent
from deps import AgentDeps
from clients import get_embedding_client, get_supabase_client
from memory import get_mem0_client

app = FastAPI(title="AI Cloud Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
async def health():
    return {"status": "ok"}


# ═══════════════════════════════════════════════════════════════════════════════
# Base Pydantic AI Agent
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/pydantic-agent", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        embedding_client = get_embedding_client()
        supabase = get_supabase_client()
        memory = get_mem0_client()

        relevant_memories = memory.search(
            query=request.message, filters={"user_id": "api_user"}, limit=3
        )
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
            result = await agent.run(request.message, deps=deps)

        memory.add(
            [{"role": "user", "content": request.message}],
            user_id="api_user",
        )

        return ChatResponse(response=result.output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# LangGraph Multi-Agent Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/agent/guardrail")
async def guardrail_agent(request: ChatRequest):
    """Guardrail agent with validation loop."""
    try:
        from graphs.guardrail_graph import workflow, create_initial_state

        state = create_initial_state(
            query=request.message,
            session_id=request.conversation_id or str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
        )
        # Non-streaming execution for simplicity
        result = await workflow.ainvoke(state)
        return {"response": result.get("final_response", ""), "agent_type": "guardrail"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/route")
async def routing_agent(request: ChatRequest):
    """LLM routing agent."""
    try:
        from graphs.routing_graph import workflow, create_initial_state

        state = create_initial_state(
            query=request.message,
            session_id=request.conversation_id or str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
        )
        result = await workflow.ainvoke(state)
        return {"response": result.get("final_response", ""), "agent_type": result.get("agent_type", "unknown")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/parallel")
async def parallel_agent(request: ChatRequest):
    """Parallel agents with synthesis."""
    try:
        from graphs.parallel_graph import workflow, create_initial_state

        state = create_initial_state(
            query=request.message,
            session_id=request.conversation_id or str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
        )
        result = await workflow.ainvoke(state)
        return {"response": result.get("final_response", ""), "agent_type": "parallel"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/supervisor")
async def supervisor_agent(request: ChatRequest):
    """Supervisor agent with dynamic delegation."""
    try:
        from graphs.supervisor_graph import workflow, create_initial_state

        state = create_initial_state(
            query=request.message,
            session_id=request.conversation_id or str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
        )
        result = await workflow.ainvoke(state)
        return {"response": result.get("final_response", ""), "agent_type": "supervisor"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
