# Product and engineering roadmap

## Milestone 0 — Chat MVP
- [x] React chat interface and authentication
- [x] Flask session auth, CSRF and conversation ownership
- [x] Anthropic and OpenAI-compatible model streaming adapters
- [x] Conversation/message persistence and starter CI

## Milestone 1 — Specialised AI teacher and development partner (current)
- [x] Three assistant modes: Teach, Build and Review
- [x] Curated shared knowledge articles seeded into the database
- [x] Learner profile: experience, language, teaching style and goals
- [x] Private project workspaces with stack, description and goals
- [x] Allow-listed text/code files stored without execution
- [x] CPU-only retrieval across shared guides and selected project files
- [x] Context source markers and persisted source labels
- [x] Conversation workspace stores mode and optional selected project
- [x] Ownership, validation, retrieval, and personalisation tests

## Milestone 2 — Quality, trust and safety
- [ ] Human-reviewed Nepali/English evaluation set across Python, AI/ML, web/mobile and SQL
- [ ] Answer feedback, issue reporting and admin quality dashboard
- [ ] Provider-reported token usage and accurate cost accounting
- [ ] Per-plan usage quotas, spend caps and low-cost model routing
- [ ] Redis-backed rate limits
- [ ] Email verification, password recovery, account deletion and data export
- [ ] Secret scanning/redaction guidance for project file ingestion
- [ ] Database migrations and managed production database

## Milestone 3 — Better project intelligence
- [ ] GitHub connection with explicit repository/branch permissions
- [ ] File tree synchronisation and incremental re-indexing
- [ ] Multilingual embeddings and vector retrieval with benchmarked quality
- [ ] Structured code review reports and diff proposals
- [ ] Safe code execution in isolated ephemeral containers
- [ ] PDF/DOCX uploads and source extraction with malware scanning

## Milestone 4 — More assistant capabilities
- [ ] Optional web search with citations
- [ ] Image/diagram understanding and voice input/output
- [ ] Tool orchestration with approval gates
- [ ] Team workspaces and collaboration

## Milestone 5 — Own model capabilities
- [ ] Benchmark open-weight models on actual target hardware
- [ ] Fine-tune narrow tasks only with permitted, high-quality, reviewed data
- [ ] Consider self-hosting when usage and unit economics justify it
- [ ] Explore original foundation-model research only with a separate data, compute, safety and staffing budget

No general-purpose foundation-model pretraining is part of the current milestone.
