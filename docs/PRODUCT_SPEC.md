# SkillForge AI — Product Requirements Document

**Product:** SkillForge AI  
**Company/brand:** SkillForge Nepal  
**Status:** MVP definition  
**Initial market:** Nepal, with international expansion later  
**Primary languages:** Nepali and English  

## 1. Product vision

Build an affordable, trustworthy ChatGPT/Claude-style AI assistant product that helps people learn, write, plan, code, analyse information, and solve everyday problems. The product experience belongs to SkillForge AI; foundation-model inference is initially supplied through interchangeable third-party or self-hosted model providers.

The product must not claim that SkillForge has trained a proprietary foundation model unless that becomes true and is independently substantiated.

## 2. Target users

- Students and independent learners
- Developers and freelancers
- Small businesses and professionals
- Nepali-speaking users who prefer Nepali explanations
- Later: teams, schools, colleges, and organisations

## 3. MVP jobs-to-be-done

1. Ask a question and receive a useful answer in Nepali or English.
2. Continue a multi-turn conversation with conversation history.
3. Explain, write, review, and debug code.
4. Draft and rewrite text such as emails, proposals, reports, and articles.
5. Explain technical topics at beginner, intermediate, or advanced levels.

## 4. MVP scope

### Included

- Responsive web application (desktop and mobile)
- Email/password registration and login
- Private conversations and message history
- Streaming assistant responses
- Configurable OpenAI-compatible model provider
- User-specific conversation ownership
- Basic usage limits and message-size limits
- Nepali/English instruction in the assistant system prompt
- Basic Markdown rendering for code, lists, tables, and links
- Environment-based model, endpoint, and API-key configuration

### Explicitly deferred

- Foundation-model pretraining from scratch
- File uploads and retrieval-augmented generation (RAG)
- Web search and source citations
- Image, voice, and video input/output
- Code execution or computer-use tools
- Team workspaces and collaboration
- Native iOS/Android apps
- Production subscriptions, wallet, and payment reconciliation
- Fine-tuning and custom model hosting

These are separate milestones requiring security, privacy, cost, and quality reviews.

## 5. Differentiation

- Nepal-first pricing and transparent NPR plans
- Good Nepali and English user experience
- Low-bandwidth-first interface
- Clear privacy and data-retention controls
- Practical usefulness for learning, coding, freelancing, and small business workflows
- Model-provider abstraction to avoid lock-in

A generic chat interface is not sufficient differentiation. We must validate a sharper wedge (for example Nepali-first coding and learning assistance) with real users before expanding features.

## 6. Product quality metrics

- First response latency and stream completion rate
- Cost per active user and cost per 1,000 messages
- Answer helpfulness rating and user-reported issue rate
- Conversation retention and weekly active users
- Nepali answer quality measured by a human-reviewed evaluation set
- Abuse rate, moderation incidents, and privacy/security incidents
- Free-to-paid conversion after paid tiers are tested

## 7. Trust and safety principles

- Clearly identify the system as an AI assistant.
- Do not represent model output as guaranteed fact.
- Do not claim web search, file inspection, code execution, or external actions unless such tools are actually connected and used.
- Keep provider keys server-side.
- Restrict conversations to their owning user.
- Apply rate limits and cost ceilings before public beta.
- Publish privacy, retention, refund, and acceptable-use policies before launch.
- Provide a mechanism to report harmful or incorrect responses.
