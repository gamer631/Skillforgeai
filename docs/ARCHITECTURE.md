# Architecture and data model

## High-level architecture

```text
Browser (React + Vite)
       |
       | same-origin /api requests + session cookie + CSRF token
       v
Flask REST API
  |-- Auth blueprint (registration, login, logout, current user)
  |-- Chat blueprint (conversation CRUD, streaming messages)
  |-- SQLAlchemy models (User, Conversation, Message)
  |-- Rate limiter
  |-- OpenAI-compatible provider adapter
       |
       +--> Hosted provider (OpenAI / Groq / compatible endpoint)
       +--> Local inference endpoint (e.g. Ollama)
       |
       v
SQLite (development) / managed PostgreSQL or MySQL (production)
```

## Provider adapter

`OpenAICompatibleProvider` sends a streaming request to `<LLM_BASE_URL>/chat/completions`.
The provider is selected entirely through environment variables. API keys are never sent to the browser.
The implementation supports common OpenAI-compatible SSE response chunks. Provider-specific features
(file search, native web search, vision, tools, structured output) need explicit adapters and tests.

## Database entities

### users

- `id` — primary key
- `email` — unique, indexed
- `display_name`
- `password_hash` — Werkzeug password hash; never store plaintext passwords
- `preferred_language`
- `is_active`
- `created_at`

### conversations

- `id` — primary key
- `user_id` — owner foreign key
- `title`
- `created_at`
- `updated_at` — indexed for recent-history ordering

### messages

- `id` — primary key
- `conversation_id` — foreign key
- `role` — `user` or `assistant`
- `content`
- `model`
- `input_characters`, `output_characters` — provisional usage metrics; not token billing
- `created_at`

### usage_events

- `id`, `user_id`, optional `conversation_id`
- `model`, request status, latency
- input/output character counts
- nullable input/output token counts for future provider-reported metering
- `created_at`

## API contract

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health and provider-configured status |
| GET | `/api/csrf` | CSRF token bootstrap |
| POST | `/api/auth/register` | Register an account |
| POST | `/api/auth/login` | Start session |
| POST | `/api/auth/logout` | End session |
| GET | `/api/auth/me` | Current user |
| GET | `/api/conversations` | List user's conversations |
| POST | `/api/conversations` | Create conversation |
| GET | `/api/conversations/{id}` | Read owned conversation |
| DELETE | `/api/conversations/{id}` | Delete owned conversation |
| POST | `/api/conversations/{id}/messages` | Stream a model response (SSE) |

## Streaming event format

Each SSE `data:` line contains JSON:

- `{"type":"delta","content":"..."}` — incremental assistant text
- `{"type":"done","conversation_id":123}` — response persisted
- `{"type":"error","error":"..."}` — provider/stream failure

## Production data migration note

`db.create_all()` is used only to make the starter easy to run. Before production, introduce Alembic/Flask-Migrate
migrations, a managed database, backups, restore drills, and a documented retention/deletion policy.
