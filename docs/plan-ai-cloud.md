# Plan: AI Cloud — Cloud-Native AI Agent Platform

## Vision
Build a **cloud-native AI agent platform** that mirrors the progressive maturity model of `ai-local` (n8n → Pydantic AI → LangGraph) but powered entirely by **cloud services** instead of local infrastructure. The project draws architecture, tooling patterns, and deployment strategies from `ai-agent-mastery`, while adopting the modular project structure and developer experience from `ai-local`.

---

## What We Are NOT Building (Local AI Stack)
| Local Service | Why Excluded | Cloud Replacement |
|---------------|-------------|-------------------|
| Ollama | Local LLM inference | OpenAI / OpenRouter / Anthropic APIs |
| Open WebUI | Local chat interface | Custom React frontend |
| Flowise | Local no-code agent builder | n8n + custom Pydantic AI agents |
| SearXNG | Local metasearch engine | Brave Search API |
| Self-hosted Supabase | Local DB/auth | Cloud Supabase project |
| Self-hosted Langfuse | Local observability | Cloud Langfuse or omit |

## What We ARE Building
| Component | Source Inspiration | Cloud Version |
|-----------|-------------------|---------------|
| **n8n** (Docker) | `ai-local` infra + `ai-agent-mastery` cloud workflow | n8n container with cloud LLM credentials, pre-loaded cloud workflow |
| **Pydantic AI Agent** | `ai-agent-mastery` Module 4 | Cloud LLMs, cloud Supabase, Brave Search |
| **React Frontend** | `ai-agent-mastery` Module 5-6 | Vite + React + Tailwind + Shadcn |
| **LangGraph Multi-Agent** | `ai-agent-mastery` Module 7 | Cloud LLM routing, supervisor, human-in-the-loop |
| **RAG Pipeline** | `ai-agent-mastery` RAG | Cloud embedding, cloud vector store |
| **Observability** | `ai-agent-mastery` Langfuse | Cloud Langfuse integration |

---

## Project Structure

```
ai-cloud/
├── apps/
│   ├── agent-backend/           # Pydantic AI + LangGraph agent (FastAPI)
│   │   ├── agent.py
│   │   ├── api.py               # FastAPI endpoints
│   │   ├── clients.py           # LLM/db client config
│   │   ├── config.py            # pydantic-settings config
│   │   ├── deps.py              # AgentDeps
│   │   ├── prompt.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   ├── tools/               # Agent tools (cloud versions)
│   │   │   ├── web_search.py    # Brave Search API
│   │   │   ├── rag_search.py    # Supabase pgvector
│   │   │   ├── image_analysis.py
│   │   │   ├── code_execution.py
│   │   │   └── sql_query.py
│   │   ├── memory/
│   │   │   └── mem0_client.py   # Long-term memory (cloud Postgres)
│   │   ├── graphs/              # LangGraph architectures
│   │   │   ├── state.py
│   │   │   ├── guardrail_graph.py
│   │   │   ├── routing_graph.py
│   │   │   ├── parallel_graph.py
│   │   │   ├── supervisor_graph.py
│   │   │   └── patterns.py
│   │   └── tests/
│   ├── agent-frontend/          # React frontend (from Module 5-6)
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   └── hooks/
│   │   └── Dockerfile
│   └── rag-pipeline/            # Document ingestion pipeline
│       ├── main.py
│       ├── text_processor.py
│       ├── db_handler.py
│       ├── requirements.txt
│       └── Dockerfile
├── infra/
│   ├── docker-compose.yml       # n8n + optional Qdrant/Neo4j/Langfuse
│   ├── docker-compose.n8n.yml   # Minimal n8n only
│   ├── n8n/
│   │   └── backup/
│   │       └── workflows/
│   │           └── AI_Agent_Cloud.json   # Pre-loaded cloud workflow
│   └── Caddyfile                # Optional reverse proxy
├── docs/
│   ├── plan-ai-cloud.md         # This file
│   ├── plan-n8n-cloud.md
│   ├── plan-pydantic-ai-cloud.md
│   └── plan-langgraph-cloud.md
├── sql/
│   ├── documents.sql
│   ├── document_metadata.sql
│   ├── document_rows.sql
│   ├── conversations_messages.sql
│   └── execute_sql_rpc.sql
├── .env.example
├── pyproject.toml               # uv project config
├── rav.yaml                     # Command shortcuts
└── README.md
```

---

## Technology Stack

### Core
- **Python 3.12+** with `uv` for package management
- **Node.js 20+** with `npm` for frontend
- **rav** for command shortcuts

### AI / LLM
- **Pydantic AI** — type-safe agent framework
- **LangGraph** — multi-agent orchestration
- **OpenAI API** — primary LLM provider (gpt-4o-mini, gpt-4o)
- **OpenRouter** — fallback/alternative provider

### Database & Storage
- **Supabase (Cloud)** — Postgres + pgvector + Auth
- **Mem0** — long-term memory over Postgres

### Search
- **Brave Search API** — web search

### Infrastructure
- **n8n (Docker)** — no-code workflow automation
- **Docker Compose** — local orchestration
- **Caddy** — reverse proxy (optional)

### Frontend
- **React 18** + **Vite**
- **Tailwind CSS** + **Shadcn UI**
- **Supabase JS client** — auth + realtime

### Observability (Optional)
- **Langfuse (Cloud)** — agent tracing & evaluation

---

## Implementation Phases

### Phase 0: Project Bootstrap
1. Initialize `pyproject.toml` with `uv`
2. Create `rav.yaml` with common commands
3. Create `.env.example` with all cloud service placeholders
4. Set up directory structure (`apps/`, `infra/`, `docs/`, `sql/`)
5. Create root `README.md`

### Phase 1: Cloud n8n Setup
1. Create `infra/docker-compose.n8n.yml` — minimal n8n with SQLite (no local Supabase)
2. Port `AI_Agent_Mastery_Prototype_Cloud.json` into `infra/n8n/backup/workflows/`
3. Add `.env` vars: `N8N_ENCRYPTION_KEY`, `N8N_USER_MANAGEMENT_JWT_SECRET`
4. Add `rav` commands: `n8n`, `n8n-stop`
5. **Test**: n8n starts at `http://localhost:5678`, cloud workflow is importable

### Phase 2: Cloud Pydantic AI Agent (Backend)
1. Create `apps/agent-backend/` with core files:
   - `config.py` — `pydantic-settings` for all cloud env vars
   - `clients.py` — OpenAI/Supabase/HTTP clients
   - `deps.py` — `AgentDeps` dataclass
   - `prompt.py` — system prompt
   - `agent.py` — Pydantic AI agent with tools
2. Port tools to cloud versions:
   - `web_search.py` — Brave Search API only
   - `rag_search.py` — Supabase pgvector similarity search
   - `image_analysis.py` — OpenAI vision
   - `code_execution.py` — RestrictedPython sandbox
   - `sql_query.py` — Supabase RPC
3. Add `memory/mem0_client.py` — Mem0 over cloud Postgres
4. Add `api.py` — FastAPI with `/api/pydantic-agent` endpoint
5. Add `streamlit_ui.py` — quick chat UI for dev
6. Add `requirements.txt` + `Dockerfile`
7. Add SQL scripts in `sql/`
8. **Test**: `python api.py` → health check passes, agent responds via curl

### Phase 3: RAG Pipeline
1. Create `apps/rag-pipeline/`:
   - `text_processor.py` — chunking + OpenAI embeddings
   - `db_handler.py` — Supabase vector operations
   - `main.py` — file watcher / Google Drive watcher
2. Add `Dockerfile`
3. **Test**: Ingest test documents, verify vector search returns results

### Phase 4: React Frontend
1. Scaffold `apps/agent-frontend/` with Vite + React + Tailwind + Shadcn
2. Port chat UI from `ai-agent-mastery` Module 5-6:
   - Auth (Supabase)
   - Chat interface with streaming
   - Conversation history
   - Settings panel
3. Add `.env.example` for frontend vars
4. Add `Dockerfile`
5. **Test**: `npm run dev` → can log in and chat with backend

### Phase 5: LangGraph Multi-Agent Architectures
1. Create `apps/agent-backend/graphs/`:
   - `state.py` — shared state definitions
   - `guardrail_graph.py` — RAG with citation validation
   - `routing_graph.py` — LLM routing to specialized agents
   - `parallel_graph.py` — parallel research agents
   - `supervisor_graph.py` — dynamic delegation
2. Add FastAPI endpoints for each graph:
   - `/api/agent/guardrail`
   - `/api/agent/route`
   - `/api/agent/parallel`
   - `/api/agent/supervisor`
3. **Test**: Each graph endpoint responds correctly

### Phase 6: Docker Compose Integration
1. Create `infra/docker-compose.yml` with:
   - `n8n` service
   - `agent-api` service (builds `apps/agent-backend/`)
   - `rag-pipeline` service (builds `apps/rag-pipeline/`)
   - `frontend` service (builds `apps/agent-frontend/`)
   - Optional: `qdrant`, `neo4j`, `langfuse-web/worker`
2. Add health checks and dependency ordering
3. Add `rav` commands: `up`, `down`, `logs`
4. **Test**: `rav run up` → all services start, frontend can chat with backend

### Phase 7: Deployment Configuration
1. Add `infra/Caddyfile` for reverse proxy
2. Add `infra/render.yaml` for Render deployment
3. Add cloud deployment guides in `docs/`
4. **Test**: Verify Caddy routes work locally

### Phase 8: Documentation & Polish
1. Write `README.md` with full setup instructions
2. Write per-module READMEs in `apps/*/README.md`
3. Add API docs (auto-generated from FastAPI)
4. Final integration testing

---

## Environment Variables (`.env.example`)

```env
# ========== N8N ==========
N8N_ENCRYPTION_KEY=your-secure-random-key
N8N_USER_MANAGEMENT_JWT_SECRET=your-secure-jwt-secret

# ========== LLM (OpenAI) ==========
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_CHOICE=gpt-4o-mini
VISION_LLM_CHOICE=gpt-4o-mini

# ========== Embedding (OpenAI) ==========
EMBEDDING_PROVIDER=openai
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=sk-...
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# ========== Database (Cloud Supabase) ==========
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres

# ========== Web Search ==========
BRAVE_API_KEY=your-brave-api-key

# ========== Frontend ==========
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_AGENT_ENDPOINT=http://localhost:8001/api/pydantic-agent
VITE_ENABLE_STREAMING=true

# ========== Observability (Optional) ==========
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com

# ========== RAG Pipeline ==========
RAG_PIPELINE_TYPE=local
RUN_MODE=continuous
RAG_WATCH_DIRECTORY=./shared

# ========== Deployment ==========
ENVIRONMENT=development
AGENT_API_HOSTNAME=agent.yourdomain.com
FRONTEND_HOSTNAME=chat.yourdomain.com
```

---

## Key Design Decisions

1. **No Local LLM Stack**: Unlike `ai-local`, we do NOT include Ollama, Open WebUI, Flowise, or SearXNG. Everything uses cloud APIs.
2. **Cloud Supabase**: We use a cloud Supabase project (not self-hosted). Users create their own project at supabase.com.
3. **Docker for n8n Only**: n8n runs in Docker for consistency. The Python backend and frontend run natively during development (via `uv` and `npm`) and are containerized for deployment.
4. **Single Python Environment**: Unlike `ai-agent-mastery` which uses separate venvs for agent and RAG, we use a single `uv` workspace or a shared `requirements.txt` to simplify dependency management.
5. **Progressive Disclosure**: Each phase is independently testable. A user can stop after Phase 1 (n8n only), Phase 2 (n8n + Pydantic agent), etc.

---

## rav.yaml Commands (Planned)

```yaml
scripts:
  # n8n
  n8n:      docker compose -f infra/docker-compose.n8n.yml up -d
  n8n-stop: docker compose -f infra/docker-compose.n8n.yml down --volumes
  n8n-logs: docker compose -f infra/docker-compose.n8n.yml logs -f n8n

  # Backend
  agent-api:      cd apps/agent-backend && uv run python -m uvicorn api:app --reload --port 8001
  agent-cli:      cd apps/agent-backend && uv run python cli.py
  agent-streamlit: cd apps/agent-backend && uv run streamlit run streamlit_ui.py
  agent-test:     cd apps/agent-backend && uv run pytest tests/ -v

  # Frontend
  frontend:       cd apps/agent-frontend && npm run dev
  frontend-build: cd apps/agent-frontend && npm run build

  # Full Stack
  up:   docker compose -f infra/docker-compose.yml up -d --build
  down: docker compose -f infra/docker-compose.yml down --volumes
  logs: docker compose -f infra/docker-compose.yml logs -f
  ps:   docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

  # Utilities
  clean: rav run down && docker system prune -f
```

---

## Acceptance Criteria

- [ ] `rav run n8n` starts n8n with pre-loaded cloud workflow
- [ ] `rav run agent-api` starts FastAPI backend, health check passes
- [ ] Agent can chat via Streamlit (`rav run agent-streamlit`)
- [ ] Agent can perform RAG against cloud Supabase
- [ ] Agent can search web via Brave API
- [ ] Agent has long-term memory via Mem0
- [ ] `rav run frontend` starts React app, can auth and chat
- [ ] LangGraph endpoints (`/api/agent/*`) work correctly
- [ ] `rav run up` starts full stack in Docker
- [ ] All SQL scripts execute cleanly on cloud Supabase
- [ ] README has clear setup instructions for cloud services
