# AI Cloud

A **cloud-native AI agent platform** that progresses from no-code prototyping to production-ready multi-agent systems.

**Stack**: n8n → Pydantic AI → LangGraph, all powered by cloud LLMs and services.

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   n8n (Docker)  │────►│  Pydantic AI    │────►│   LangGraph     │
│   localhost:5678│     │  Agent (FastAPI)│     │  Multi-Agent    │
│                 │     │  localhost:8001 │     │  localhost:8001 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │   Cloud Services    │
                    │  • OpenAI / OpenRouter│
                    │  • Cloud Supabase   │
                    │  • Brave Search API │
                    │  • Mem0 (memory)    │
                    │  • Langfuse (opt)   │
                    └─────────────────────┘
```

---

## Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **Docker / Docker Desktop**
- **uv** (`pip install uv`)
- **rav** (`pip install rav`)

### Cloud Service Accounts

1. **OpenAI API** — [platform.openai.com](https://platform.openai.com)
2. **Supabase** — [supabase.com](https://supabase.com) (create a project)
3. **Brave Search API** — [brave.com/search/api](https://brave.com/search/api)

### 1. Clone & Setup

```bash
cd ai-cloud

# Create virtual environment
uv venv
source .venv/bin/activate

# Install root dependencies
uv pip install -e ".[all]"

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### 2. Database Setup

```bash
rav run db-setup
```

This runs all SQL files in `sql/` against your cloud Supabase project via the connection pooler.

### 3. Start Services

```bash
# Terminal 1: Start n8n (Docker)
rav run n8n

# Terminal 2: Start agent backend (native Python)
rav run agent-api

# Terminal 3: Start RAG pipeline (file watcher)
rav run rag-pipeline

# Terminal 4: Start frontend (native Node)
cd apps/agent-frontend
npm install
rav run frontend
```

### 4. Access

| Service | URL | Notes |
|---------|-----|-------|
| n8n | http://localhost:5678 | Workflow automation |
| Agent API | http://localhost:8001 | FastAPI + Pydantic AI |
| API Docs | http://localhost:8001/docs | Auto-generated Swagger |
| Frontend | http://localhost:8082 | React chat UI |
| Streamlit UI | http://localhost:8501 | `rav run agent-streamlit` |

---

## Project Structure

```
ai-cloud/
├── apps/
│   ├── agent-backend/          # Pydantic AI + LangGraph + FastAPI
│   │   ├── agent.py            # Main agent definition
│   │   ├── api.py              # FastAPI endpoints
│   │   ├── cli.py              # Interactive CLI
│   │   ├── streamlit_ui.py     # Streamlit chat UI
│   │   ├── config.py           # Centralized config
│   │   ├── tools/              # Agent tools (RAG, web search, code, SQL)
│   │   ├── memory/             # Mem0 long-term memory
│   │   ├── graphs/             # LangGraph architectures
│   │   └── tests/              # Backend unit tests
│   ├── agent-frontend/         # React + Tailwind + shadcn/ui chat
│   │   ├── src/pages/Admin.tsx # Admin dashboard
│   │   ├── src/pages/Chat.tsx  # Chat interface
│   │   └── tests/              # Vitest unit tests
│   └── rag-pipeline/           # Document ingestion pipeline
│       ├── main.py             # File watcher
│       ├── db_handler.py       # Supabase operations
│       └── text_processor.py   # Chunking + embeddings
├── infra/
│   ├── docker-compose.yml      # Full stack (optional)
│   ├── docker-compose.n8n.yml  # Standalone n8n
│   ├── n8n/backup/workflows/   # Pre-loaded cloud workflow
│   └── Caddyfile               # Reverse proxy
├── sql/                        # Supabase schema scripts
├── scripts/                    # Utility scripts (run_sql.py)
├── shared/                     # Document drop folder for RAG
├── docs/                       # Implementation plans
├── tests/                      # Smoke/integration tests
├── .env.example                # Environment template
├── pyproject.toml              # uv project config
└── rav.yaml                    # Command shortcuts
```

---

## Commands (via `rav`)

### Infrastructure
| Command | Description |
|---------|-------------|
| `rav run n8n` | Start n8n in Docker |
| `rav run n8n-stop` | Stop n8n |
| `rav run n8n-logs` | Tail n8n logs |
| `rav run n8n-recreate` | Recreate n8n container |
| `rav run up` | Start full stack in Docker |
| `rav run down` | Stop full stack |
| `rav run ps` | List all Docker containers |
| `rav run ps-ai-cloud` | List ai-cloud containers |
| `rav run logs` | View stack logs |
| `rav run db-setup` | Run SQL setup scripts |

### Backend
| Command | Description |
|---------|-------------|
| `rav run agent-api` | Start agent API on port 8001 |
| `rav run agent-api-stop` | Stop agent API |
| `rav run agent-cli` | Run interactive CLI |
| `rav run agent-streamlit` | Start Streamlit chat UI |
| `rav run agent-streamlit-stop` | Stop Streamlit |
| `rav run agent-test` | Run backend tests |
| `rav run rag-pipeline` | Start RAG file watcher |
| `rav run rag-pipeline-stop` | Stop RAG pipeline |

### Frontend
| Command | Description |
|---------|-------------|
| `rav run frontend` | Start React frontend (dev mode) |
| `rav run frontend-build` | Build for production |
| `rav run frontend-install` | Install npm dependencies |
| `rav run frontend-test` | Run frontend unit tests (Vitest) |
| `rav run frontend-test-coverage` | Run frontend tests with coverage |

### Testing & Utilities
| Command | Description |
|---------|-------------|
| `rav run smoke-test` | Run pytest smoke test suite |
| `rav run coverage` | Run backend tests with coverage report |
| `rav run stop-all` | Stop all native + Docker services |
| `rav run clean` | Destroy all containers and volumes |
| `rav run generate-secrets` | Generate random N8N secrets |

---

## RAG Pipeline

Documents dropped into `shared/` are automatically:
1. Chunked by the RAG pipeline
2. Embedded using your configured embedding model
3. Stored in Supabase `documents` table with pgvector

The chat endpoints automatically retrieve relevant documents and prepend them to the agent's context.

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `POST /api/pydantic-agent` | Base Pydantic AI agent with RAG + memory |
| `POST /api/agent/guardrail` | Guardrail agent with validation |
| `POST /api/agent/route` | LLM routing agent |
| `POST /api/agent/parallel` | Parallel agents with synthesis |
| `POST /api/agent/supervisor` | Supervisor with dynamic delegation |

---

## Testing

### Backend Tests

```bash
# Run all backend tests
rav run agent-test

# Run smoke tests only
rav run smoke-test

# Run with coverage
rav run coverage
```

Backend coverage generates terminal + HTML reports (`htmlcov/index.html`).

### Frontend Tests

```bash
# Run frontend unit tests
rav run frontend-test

# Run with coverage
rav run frontend-test-coverage
```

Frontend coverage report is written to `apps/agent-frontend/htmlcov/`.

---

## Development Phases

1. **Phase 1**: n8n prototyping with cloud workflow ✅
2. **Phase 2**: Pydantic AI agent backend ✅
3. **Phase 3**: RAG document pipeline ✅
4. **Phase 4**: React frontend ✅
5. **Phase 5**: LangGraph multi-agent architectures ✅
6. **Phase 6**: Testing & coverage ✅
7. **Phase 7**: Full Docker Compose stack ✅
8. **Phase 8**: Deployment configuration ✅

See `docs/plan-ai-cloud.md` for the full implementation plan.

---

## Deployment

### Docker Compose (Full Stack)

```bash
# Ensure .env is populated, then:
rav run up
```

### Render

Use `infra/render.yaml` for [Render Blueprints](https://render.com/blueprints) deployment.

### Custom Domain (Caddy)

1. Set `AGENT_API_HOSTNAME` and `FRONTEND_HOSTNAME` in `.env`
2. Uncomment the Caddy service in `infra/docker-compose.yml`
3. `rav run up`

---

## License

Proprietary — see reference projects for component licenses.
