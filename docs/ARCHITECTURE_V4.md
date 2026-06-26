# Prisma AI v4 — Production Foundation

## Golden rule: two independent systems

### 1. Analytics Engine (core)

Deterministic, no LLM. Responsible for ingestion, profiling, insights, forecast, AutoML, SHAP, charts, dashboard, reports (structured fields), root cause, compare, recommendations.

Output shape (evolving):

```json
{
  "profile": {},
  "health": {},
  "insights": {},
  "dashboard": {},
  "forecast": {},
  "xai": {},
  "recommendations": {},
  "report": {}
}
```

Frontend renders from backend JSON only. No fake metrics.

### 2. AI Narration Engine (optional)

Never calculates. Converts structured analytics into natural language via `backend/app/services/llm/`.

Default provider: **NoOp** (template/heuristic fallbacks). No localhost, no API keys required.

## Implementation phases

| Phase | Scope | Status |
|-------|--------|--------|
| **1** | Reports API, dashboard panels, SHAP UI, forecast UX, analytics polish, LLM NoOp default | In progress |
| **2** | Dataset intelligence (domain detection), projects/workspaces, connector interfaces | Planned |
| **3** | Deploy: Vercel + Render + Supabase + Redis + Sentry + PostHog | Planned |
| **4** | LLM providers (Ollama, OpenAI, Gemini, etc.) behind single config | Planned |

## LLM configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `none` | `none` \| `ollama` (more providers later) |
| `OLLAMA_BASE_URL` | — | Only when `LLM_PROVIDER=ollama` |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `OLLAMA_TIMEOUT` | `30` | Generate timeout (seconds) |
| `OLLAMA_CONNECT_TIMEOUT` | `5` | Connection timeout (seconds) |

## Deployment target

```
Frontend → Vercel
Backend  → Render
Database → Supabase Postgres (Phase 3)
Storage  → Supabase Storage (Phase 3)
Cache    → Redis (Phase 3)
```

Phase 1 ships without database/Redis; in-memory sessions remain for demo deploy.

## Non-negotiables

- Never break existing tests
- Preserve API contracts unless strictly necessary
- Analytics deterministic; AI optional
- Document architectural changes here and in README
