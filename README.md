# SkillForge AI

**Think. Create. Code. Understand.**  
An affordable AI assistant built in Nepal, designed for Nepali and English users.

This repository contains an early MVP foundation: a React chat interface, Flask API, account registration/login, user-owned conversation history, streaming AI responses through native Anthropic and OpenAI-compatible provider adapters, basic rate limits, usage-event records, and automated backend/frontend tests.

> **Important product truth:** SkillForge AI is the assistant product and application layer. The first version uses an existing model through an API or a compatible local inference server. It does not claim to have trained a ChatGPT/Claude-scale foundation model. Training a competitive general-purpose model from scratch is not a realistic low-budget first step, especially without dedicated GPU infrastructure.

## What's implemented

- Responsive dark chat interface with signup/sign-in
- User-owned conversations, message history, and delete conversation
- Streaming server-sent-event (SSE) responses
- Nepali/English-aware system instructions
- Provider adapters for the native Anthropic Messages API and OpenAI-compatible chat endpoints
- Can point at OpenAI, Groq, a compatible router, local Ollama, or Anthropic Claude API
- Server-side API key storage
- Password hashing, HTTP-only session cookies, CSRF protection
- Conversation ownership checks
- Message-size, hourly rate, and daily beta limits
- Basic usage and latency event records
- SQLite development database and Docker setup
- Pytest API tests and Vitest frontend utility tests

## Repository layout

```text
Skillforgeai/
├── backend/
│   ├── app/
│   │   ├── auth/              # register, login, logout, current user
│   │   ├── chat/              # conversations and streamed messages
│   │   ├── services/          # model-provider adapter
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py          # User, Conversation, Message, UsageEvent
│   │   └── __init__.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── wsgi.py
├── frontend/
│   ├── src/App.jsx
│   ├── src/api.js
│   ├── src/styles.css
│   ├── src/utils.js
│   └── package.json
├── docs/
│   ├── PRODUCT_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── MODEL_STRATEGY.md
│   ├── NEPAL_PRICING.md
│   └── SECURITY_AND_LAUNCH.md
├── .env.example
├── docker-compose.yml
└── Makefile
```

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- An API key for a hosted model provider **or** a running compatible local model server

## Run locally — Windows PowerShell

### 1. Configure backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item ..\.env.example .env
```

Edit `backend/.env` and set:

```env
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-provider-api-key
LLM_MODEL=your-currently-available-chat-model
```

For Claude API access, use the native Messages adapter:

```env
LLM_PROVIDER=anthropic
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_API_KEY=your-anthropic-api-key
LLM_MODEL=your-currently-available-claude-model
ANTHROPIC_VERSION=2026-10-21
```

Never commit `.env` or place an API key in frontend variables.

### 2. Start the backend

```powershell
flask --app wsgi.py run --debug --port 5000
```

Backend: `http://127.0.0.1:5000`  
Health: `http://127.0.0.1:5000/api/health`

### 3. Start the frontend

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

### macOS/Linux equivalent

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with provider endpoint, key, and model.
flask --app wsgi.py run --debug --port 5000
```

In another terminal, run `cd frontend && npm install && npm run dev`.

## Local model with Ollama

Install Ollama and pull a model that fits your computer's RAM. Start the local service, then set the backend environment to:

```env
LLM_BASE_URL=http://127.0.0.1:11434/v1
LLM_API_KEY=
LLM_MODEL=your-local-model-name
```

The model name must match a model available in your Ollama installation. Local model speed and quality depend heavily on system RAM, CPU, model size, and quantisation. A small local model may be useful for development, but it will not automatically match frontier hosted assistants. If the API is running in Docker while Ollama runs on your host machine, use `http://host.docker.internal:11434/v1` (where supported) instead of `127.0.0.1`.

## Tests and production build

Backend tests:

```bash
cd backend
pytest
```

Frontend tests and production build:

```bash
cd frontend
npm install
npm test
npm run build
```

## Docker

Copy `.env.example` to `.env` at repository root, configure `LLM_MODEL` and provider credentials, then run:

```bash
docker compose up --build
```

The API is exposed on port `5000`. The frontend is currently run separately with Vite; production should serve the built frontend and `/api` behind one HTTPS domain/reverse proxy.

## Current API

- `GET /api/health`
- `GET /api/csrf`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/conversations`
- `POST /api/conversations`
- `GET /api/conversations/<id>`
- `DELETE /api/conversations/<id>`
- `POST /api/conversations/<id>/messages` (SSE stream)

## Known limitations — do not skip before launch

This is an early MVP foundation, not a production-ready public AI service. It does not yet have email verification, password reset, account deletion, mature moderation, user feedback, file upload/RAG, web search, citations, voice/image support, tool execution, subscription billing, token-based accounting, model routing, or robust distributed rate limiting. The in-memory limiter is for development; use Redis in production. Add migrations before production database use. Review model-provider terms and privacy handling. Complete a security review and cost-budget tests before accepting payments or opening the service to the public.

See `docs/SECURITY_AND_LAUNCH.md` for the release checklist.

## License

MIT for this starter software. Product branding and any third-party model, dataset, media, or provider assets remain subject to their own terms.
