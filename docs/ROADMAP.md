# Product and engineering roadmap

## Milestone 0 — Local MVP foundation (this repository)

- [x] React chat interface and auth screen
- [x] Flask session auth, CSRF, conversation ownership
- [x] Streaming provider adapter
- [x] Conversation/message persistence
- [x] Starter usage event schema, hourly and daily beta limits
- [x] Backend tests and frontend utility tests authored
- [ ] Run dependency-backed test/build checks in an environment with package access

## Milestone 1 — Private alpha

- [ ] Choose provider and model using a cost/quality benchmark
- [ ] Deploy to a private staging URL with HTTPS
- [ ] Add Redis-backed rate limits, request IDs, and structured observability
- [ ] Add admin usage dashboard, provider cost accounting, and spend alerts
- [ ] Add user feedback (thumbs up/down + reason)
- [ ] Add Nepali/English evaluation suite and human review
- [ ] Invite 20–50 testers and review weekly feedback

## Milestone 2 — Trust and paid beta

- [ ] Email verification, password reset, account deletion
- [ ] Mature moderation and abuse reporting
- [ ] Token usage ingestion, per-plan quotas, and transparent usage meter
- [ ] Model routing and safe fallback strategy
- [ ] Privacy/retention policy and model-provider disclosure
- [ ] Payment integration only after merchant and legal requirements are checked
- [ ] Limited NPR-priced subscription pilot; no unlimited plans

## Milestone 3 — Useful tools

- [ ] File uploads with size/type validation and malware scanning
- [ ] Document extraction and per-user RAG with source references
- [ ] Web search provider with citations and freshness timestamps
- [ ] Prompt-injection-resistant tool orchestration
- [ ] Safe code execution in isolated ephemeral containers (never in the API process)

## Milestone 4 — Multimodal and teams

- [ ] Image understanding
- [ ] Voice input/output
- [ ] Team workspaces and shared billing
- [ ] Mobile PWA improvements and optional native apps

## Milestone 5 — Own model capabilities

- [ ] Benchmark open-weight models on target hardware and Nepali evaluations
- [ ] Self-host an open-weight model only when demand and economics justify GPU hosting
- [ ] Fine-tune for a narrow task only with licensed, reviewed, high-quality data
- [ ] Explore original pretraining research only with an explicit compute, data, safety, and staffing budget
