# SkillForge AI

**Think. Create. Code. Understand.**  
A Nepal-built AI teacher and software development partner for Nepali and English users.

SkillForge AI is not pretraining a general-purpose foundation model. It uses an interchangeable hosted or local model and adds specialised behaviour through curated technical knowledge, private project context, learner preferences, and Teach/Build/Review modes.

## What it does

- **Teach:** explain Python, AI/ML, deep learning, web/mobile development, databases, and software engineering step by step.
- **Build:** plan features, propose implementation code, explain file changes, and suggest focused tests.
- **Review:** inspect supplied code excerpts for correctness, security, performance, and maintainability.
- **Shared expertise:** a curated, seeded knowledge library covering Python debugging, full-stack architecture, SQL, machine learning, deep learning, and secure-code review.
- **Personal project context:** private projects with descriptions, goals, technology stacks, and selected code/text files.
- **Retrieval:** CPU-only lexical retrieval sends the top relevant shared and project snippets with [K1] and [P1] source markers.
- **Learner profile:** experience level, language preference, teaching style, and learning goals.
- **Streaming chat:** existing Anthropic and OpenAI-compatible provider adapters remain configurable.
- **User isolation:** all projects and conversations are checked against the authenticated owner.

## Project knowledge

1. Create a project in the left sidebar.
2. Add its name, description, goals, and stack.
3. Select the project above the chat.
4. Add selected UTF-8 source/config/documentation files in supported text formats.
5. Ask SkillForge to teach, build, or review in the context of that project.
6. The assistant receives only top-ranked relevant excerpts and cites them as [P1], [P2], etc. Shared guides use [K1], [K2].

Project files are stored as text and are never executed by this service. Do not upload secrets, API keys, environment credentials, private keys, customer data, or confidential files. The initial retrieval engine is lexical and may miss relevant files.

## Requirements and local setup

- Python 3.11+, Node.js 20+, npm
- Hosted model API key or compatible local inference service

Windows PowerShell backend:

\`\`\`powershell
cd backend
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item ..\\.env.example .env
\`\`\`

Set the model provider in the backend environment:

\`\`\`env
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-provider-api-key
LLM_MODEL=your-currently-available-model
\`\`\`

For Claude API access use the native Anthropic adapter:

\`\`\`env
LLM_PROVIDER=anthropic
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_API_KEY=your-anthropic-api-key
LLM_MODEL=your-currently-available-claude-model
ANTHROPIC_VERSION=2026-10-21
\`\`\`

Start the backend:

\`\`\`powershell
flask --app wsgi.py run --debug --port 5000
\`\`\`

Start the frontend in another terminal:

\`\`\`powershell
cd frontend
npm install
npm run dev
\`\`\`

Open http://127.0.0.1:5173.

macOS/Linux: create a virtual environment in backend, install requirements, copy ../.env.example to .env, then run \`flask --app wsgi.py run --debug --port 5000\`. In another terminal run \`cd frontend && npm install && npm run dev\`.

## Seed shared knowledge

Starter articles are inserted at app startup if their slugs do not exist. To seed explicitly from the backend directory:

\`\`\`bash
python -m scripts.seed_knowledge
\`\`\`

The seed routine does not overwrite existing articles; updates should use a deliberate content change or migration process.

## API additions

- \`GET /api/knowledge\` — list published shared guides (requires login)
- \`GET /api/projects\`, \`POST /api/projects\`
- \`GET /api/projects/{id}\`, \`PATCH /api/projects/{id}\`, \`DELETE /api/projects/{id}\`
- \`POST /api/projects/{id}/files\` — add/update one text/code file
- \`DELETE /api/projects/{id}/files/{file_id}\`
- \`GET /api/profile\`, \`PUT /api/profile\`
- \`GET /api/usage\` — 30-day approximate usage
- \`POST /api/conversations/{id}/messages\` accepts \`mode\` (\`teach\`, \`build\`, \`review\`) and optional \`project_id\`

## Tests

\`\`\`bash
cd backend && pytest
\`\`\`

\`\`\`bash
cd frontend && npm install && npm test && npm run build
\`\`\`

GitHub Actions runs backend tests and frontend tests/build on pushes and pull requests to main/develop.

## Model and safety limits

The app does not train a ChatGPT/Claude-scale model. Shared knowledge plus retrieval improves task relevance; it does not guarantee factual accuracy. Project context is selected by lexical matching and only supplied snippets are seen by the model. Provider credentials stay on the server, but prompts and retrieved snippets are sent to the configured provider. Disclose this before public launch. This is a development milestone, not production certification.

See docs/SPECIALIZED_ASSISTANT.md, docs/ARCHITECTURE.md, docs/SECURITY_AND_LAUNCH.md, and docs/ROADMAP.md.

## License

MIT for this starter software. Third-party models, providers, datasets, and assets remain subject to their own terms.
