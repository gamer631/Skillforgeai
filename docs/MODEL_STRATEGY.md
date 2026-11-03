# Model strategy: building a ChatGPT-class product responsibly

## Do not begin by pretraining a foundation model

A model that is only 10–30 million parameters is useful for experiments (tokenisation, language modelling,
small classifiers, or domain-specific components), but it will not provide the broad reasoning, coding,
multilingual quality, and reliability expected from a ChatGPT/Claude-style general assistant.

With no dedicated NVIDIA GPU and a low initial budget, pretraining a competitive foundation model is not a
practical first milestone. It would also consume time and money before product-market fit is established.

## Recommended sequence

### Stage 1 — Own the product layer (current MVP)

- Build the user experience, accounts, chat history, streaming, safety controls, privacy, usage metering,
  feedback, and evaluation framework.
- Use an interchangeable hosted model provider through either the native Anthropic Messages API adapter or the OpenAI-compatible chat-completions adapter.
- Keep provider keys on the backend; never expose them to the browser.

### Stage 2 — Cost and quality routing

- Compare candidate models on a fixed Nepali/English benchmark.
- Route easy tasks to low-cost fast models and complex tasks to stronger models.
- Measure input/output tokens, latency, answer quality, and cost per successful task.
- Add provider fallback only after testing timeout, failure, and privacy behaviour.

### Stage 3 — Product-specific intelligence

- Add retrieval-augmented generation for SkillForge-owned help content or user documents.
- Add web search with cited sources only after a search provider is integrated.
- Add tool use in isolated, permissioned services; never execute arbitrary model-generated code on the API server.
- Add file extraction, malware scanning, and per-user access checks before file uploads.

### Stage 4 — Open-weight/self-hosted models

- Benchmark small quantised models on actual target hardware before paying for hosting.
- Run local Ollama models for development and offline experiments where hardware allows.
- Consider a managed GPU endpoint only when recurring inference cost and sustained demand justify it.
- Consider fine-tuning an existing open-weight model only when high-quality task examples and evaluation data exist.

### Stage 5 — Original model research (long-term, optional)

- Build a clean dataset with permission and provenance controls.
- Establish a reproducible evaluation suite before training.
- Start with small task-specific experiments, not a claim of a general-purpose frontier model.
- Estimate compute, data, staffing, safety, and deployment budgets before any pretraining commitment.

## Candidate provider configuration patterns

| Provider style | Environment | Example base URL | Notes |
|---|---|---|---|
| OpenAI API | `LLM_PROVIDER=openai-compatible` | `https://api.openai.com/v1` | Set a currently available model from the account |
| Groq API | `LLM_PROVIDER=openai-compatible` | `https://api.groq.com/openai/v1` | OpenAI-compatible chat completions endpoint |
| Local Ollama | `LLM_PROVIDER=openai-compatible` | `http://127.0.0.1:11434/v1` | Local inference; speed and quality depend on hardware |
| Anthropic Claude API | `LLM_PROVIDER=anthropic` | `https://api.anthropic.com/v1` | Native Messages API; API billing is separate from consumer Claude plans |

Provider model names and prices change. Verify availability, geographic access, terms, privacy, and pricing on the provider's official documentation before enabling a model for customers.

## Commercial API billing reminder

A personal ChatGPT or Claude consumer subscription is not the same thing as API access for a product. Model API calls are billed separately by the provider according to API usage and model pricing. Budget the provider bill independently from SkillForge user subscriptions, and enforce usage caps before opening a public beta. Anthropic documents the separation between Claude.ai plans and API Console usage in its help centre: https://support.anthropic.com/en/articles/9876003-i-subscribe-to-a-paid-claude-ai-plan-why-do-i-have-to-pay-separately-for-api-usage-on-console
