# SkillForge AI — Specialised teacher and development partner

## Product identity

SkillForge AI is both:
- An expert technology teacher that explains concepts, builds mental models, provides examples, and checks understanding.
- A software development partner that helps plan features, diagnose bugs, generate code, review changes, and suggest tests.

This product does not pretrain a general foundation model. It uses a configurable hosted or local model and improves task relevance with curated knowledge, project-aware retrieval, mode-specific instructions, learner preferences, and ongoing evaluation.

## Assistant modes

### Teach
- Adapt to beginner, intermediate, or advanced experience.
- Explain intuition before syntax.
- Use step-by-step explanations, worked examples, common mistakes, and a practice task.
- Prefer Socratic questions or hands-on teaching when selected in the learner profile.
- Respond in the preferred language or follow the user's message.

### Build
- Understand the user's project goal and selected project context.
- Propose a short plan and small implementation steps.
- Include relevant file paths, code, and focused tests.
- State assumptions and trade-offs.
- Never claim to have opened or modified the user's repository or run code without a real connected tool.

### Review
- Prioritise correctness and security findings.
- Separate verified evidence from hypotheses.
- Explain impact, affected location, recommended fix, and tests.
- Do not invent vulnerabilities.

## Two knowledge layers

### Shared expert knowledge
The initial curated library is seeded from reviewed SkillForge-authored notes about:
- Python debugging
- Full-stack web architecture
- Relational database design
- Machine-learning workflow and evaluation
- Deep-learning foundations
- Secure-code review

These are starter notes, not a replacement for official language/framework documentation. Add reviewed articles through the seed content process. Each article has a stable slug, title, category, tags, language, summary, content, and publication flag.

### Personal project knowledge
Users can create private project workspaces with:
- Project name, description, goals, and technology stack
- Selected source/config/documentation files in supported text formats
- Per-project limits on file count and characters
- Lexical retrieval across those files when the project is selected in a conversation

Files are stored as UTF-8 text in the application database, not executed. Users should not upload environment secrets, API keys, customer data, private keys, or production credentials. The initial allow-list is source code and text formats only.

## Retrieval approach

The MVP uses CPU-only lexical matching:
1. Split curated articles and project files into overlapping text chunks.
2. Tokenise Unicode text and code identifiers.
3. Rank chunks by query-token overlap.
4. Include a small, bounded number of relevant chunks in the model context.
5. Add references such as [K1] for shared knowledge and [P1] for a user's project file.
6. Persist source labels with the assistant message and show them in the UI.

This is deterministic and cheap, but not semantic vector search. Synonyms and conceptual matches can be missed. A future milestone can add multilingual embeddings and a vector store after collecting evaluation examples.

## Privacy and trust boundaries

- Project records and files are scoped by owner ID in every route.
- A conversation can only attach a project owned by the logged-in user.
- Retrieved knowledge/project text is explicitly treated as untrusted data, never privileged instructions.
- Project source files are not run or installed.
- Model prompts include only selected project context and top-ranked snippets; do not assume all files were read.
- When using a hosted provider, the included excerpts and user prompt are transmitted to that provider. Disclose this before public launch.
- The current lexical engine is not a secret scanner. Do not upload secrets or confidential data.

## Model strategy

Keep provider adapters interchangeable. Start with an affordable model that performs adequately on a human-reviewed Nepali/English technology benchmark. Measure quality and cost. Fine-tuning may later improve response style or narrowly scoped tasks, but it is not required to launch this architecture. Do not claim a proprietary foundation model or frontier-level ability.
