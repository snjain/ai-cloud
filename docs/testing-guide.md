# AI Cloud — Testing Guide

## Before You Start

You need these API keys configured in your `.env` file:

```bash
cd /Users/snjain/github/ai-cloud
cp .env.example .env
```

Edit `.env` and set at minimum:
- `LLM_API_KEY` — OpenAI API key
- `SUPABASE_URL` — Cloud Supabase project URL
- `SUPABASE_SERVICE_KEY` — Supabase service role key
- `DATABASE_URL` — Postgres connection string
- `BRAVE_API_KEY` — Brave Search API key

Also copy and fill in `apps/agent-backend/.env` and `apps/agent-frontend/.env`.

Run the SQL scripts to set up your Supabase database:

```bash
cd /Users/snjain/github/ai-cloud
rav run db-setup
```

This runs all SQL files in `sql/` automatically. Alternatively, you can paste them manually into the Supabase SQL Editor.

---

## Test 1: n8n (No API Keys Needed)

```bash
cd /Users/snjain/github/ai-cloud
rav run n8n
```

**Verify:**
- Open http://localhost:5678
- Complete the initial owner setup (first time only)
- Go to Workflows — you should see "AI Agent Cloud" workflow imported

**Stop:**
```bash
rav run n8n-stop
```

---

## Test 2: Agent Backend — CLI Mode

```bash
cd /Users/snjain/github/ai-cloud/apps/agent-backend
source ../../.venv/bin/activate
python cli.py
```

**Expected interaction:**
```
🤖 AI Cloud Agent CLI
Type 'exit' to quit

You: What is the capital of France?
Agent: The capital of France is Paris...

You: exit
```

**What it tests:**
- ✅ OpenAI API connection
- ✅ Agent initialization
- ✅ Tool registration
- ✅ Mem0 memory

---

## Test 3: Agent Backend — API Mode

Terminal 1:
```bash
cd /Users/snjain/github/ai-cloud/apps/agent-backend
source ../../.venv/bin/activate
rav run agent-api
```

Terminal 2:
```bash
# Health check
curl http://localhost:8001/health

# Base agent chat
curl -X POST http://localhost:8001/api/pydantic-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?"}'

# Guardrail agent
curl -X POST http://localhost:8001/api/agent/guardrail \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain quantum computing"}'

# Routing agent
curl -X POST http://localhost:8001/api/agent/route \
  -H "Content-Type: application/json" \
  -d '{"message": "Search the web for latest AI news"}'

# Parallel agent
curl -X POST http://localhost:8001/api/agent/parallel \
  -H "Content-Type: application/json" \
  -d '{"message": "Compare Python vs JavaScript"}'

# Supervisor agent
curl -X POST http://localhost:8001/api/agent/supervisor \
  -H "Content-Type: application/json" \
  -d '{"message": "Research climate change and summarize"}'
```

**Expected:** JSON response with `"response": "..."`

---

## Test 4: Agent Backend — Streamlit UI

```bash
cd /Users/snjain/github/ai-cloud/apps/agent-backend
source ../../.venv/bin/activate
rav run agent-streamlit
```

**Verify:**
- Open http://localhost:8501
- Type a message and send
- Watch the agent respond with streaming text

---

## Test 5: Frontend

```bash
cd /Users/snjain/github/ai-cloud/apps/agent-frontend
npm install  # if not done
rav run frontend
```

**Verify:**
- Open http://localhost:8082
- Sign up / Log in (uses Supabase auth)
- Chat with the agent
- Messages render with Markdown support

---

## Test 6: RAG Pipeline

```bash
# Create a test document
mkdir -p /Users/snjain/github/ai-cloud/shared
echo "AI Cloud is a cloud-native agent platform built with n8n, Pydantic AI, and LangGraph. It uses OpenAI for LLMs, Supabase for storage, and Brave Search for web search." > /Users/snjain/github/ai-cloud/shared/test_doc.txt

# Run the pipeline
cd /Users/snjain/github/ai-cloud/apps/rag-pipeline
source ../../.venv/bin/activate
python main.py --watch ../../shared --interval 5
```

**Expected:**
```
Processing: /Users/snjain/github/ai-cloud/shared/test_doc.txt
  ✓ Indexed: test_doc.txt
```

**Verify in Supabase:**
```bash
rav run db-setup
```
Or manually in Supabase SQL Editor, run: `SELECT * FROM documents;`
- You should see the document chunks

Then test RAG via the agent:
```bash
curl -X POST http://localhost:8001/api/pydantic-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AI Cloud?"}'
```

The agent should retrieve the document and answer based on it.

---

## Test 7: Full Stack (Docker Compose)

```bash
cd /Users/snjain/github/ai-cloud
rav run up
```

**Verify all services:**
```bash
rav run ps
```

Expected output:
```
NAMES                    STATUS          PORTS
ai-cloud-agent-api       Up ...          0.0.0.0:8001->8001/tcp
ai-cloud-frontend        Up ...          0.0.0.0:8082->80/tcp
ai-cloud-rag-pipeline    Up ...
n8n                      Up ...          0.0.0.0:5678->5678/tcp
```

**Test:**
- http://localhost:5678 — n8n
- http://localhost:8001/health — Agent API
- http://localhost:8082 — Frontend

**Stop:**
```bash
rav run down
```

---

## Quick Smoke Test Script

Run the automated smoke test suite:

```bash
cd /Users/snjain/github/ai-cloud
rav run smoke-test
```

Or run this manually to verify the core backend works:

```bash
cd /Users/snjain/github/ai-cloud/apps/agent-backend
source ../../.venv/bin/activate

python3 << 'EOF'
import asyncio
from httpx import AsyncClient
from agent import get_agent
from deps import AgentDeps
from clients import get_embedding_client, get_supabase_client

async def test():
    embedding_client = get_embedding_client()
    supabase = get_supabase_client()
    
    async with AsyncClient() as http_client:
        deps = AgentDeps(
            supabase=supabase,
            embedding_client=embedding_client,
            http_client=http_client,
            brave_api_key=None,
            memories="",
        )
        agent = get_agent()
        result = await agent.run("Say 'AI Cloud is working' and nothing else.", deps=deps)
        print("Response:", result.data)

asyncio.run(test())
EOF
```

**Expected:** `Response: AI Cloud is working`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Need n8n secrets | Run `rav run generate-secrets` |
| `Missing credentials` / `OpenAIError` | Set `LLM_API_KEY` in `.env` |
| `supabase_url is required` | Set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` |
| `No module named 'langgraph'` | Run `uv pip install langgraph>=0.3.0` |
| `Port 5678 already in use` | `docker stop n8n` or change port |
| Frontend blank page | Check browser console for CORS errors; ensure `VITE_AGENT_ENDPOINT` is correct |
| n8n workflow not imported | Check `infra/n8n/backup/workflows/` has the JSON file |
