# Security, privacy, and launch checklist

## Current implementation safeguards

- Password hashes, not plaintext passwords
- Session cookies are HTTP-only
- CSRF protection on mutating API calls
- CORS allow-list from environment configuration
- Per-user conversation ownership checks
- Input length limits
- Registration/login/chat rate limits
- Model API keys remain server-side
- Generic error messages for unexpected failures

## Required before any public launch

- Replace the development secret with a cryptographically random secret.
- Set HTTPS and `SESSION_COOKIE_SECURE=true`; review SameSite and CORS for the final domain.
- Move rate-limit storage from in-memory to Redis or another shared backend.
- Use a managed relational database, migrations, encryption at rest, backups, and restore tests.
- Add email verification, password reset, account deletion, and session revocation.
- Add abuse detection, safety review, and a user report flow.
- Implement per-plan token quotas, spend budgets, and provider usage accounting.
- Review prompt-injection risks before enabling document retrieval or tools.
- Add data-retention/deletion policy and disclose model-provider data handling.
- Conduct dependency, application, and API security reviews.
- Add monitoring, structured logs with PII minimisation, and incident response runbooks.
- Review Nepal legal, privacy, consumer, payment, and tax requirements with qualified local advisers.
- Confirm all provider terms permit the intended product use and that user data handling is disclosed.

## Important limitations

This repository is a functional MVP foundation, not a production security certification. It does not yet include a mature moderation pipeline, file scanning, web search, payment processing, token accounting, plan enforcement, email verification, or account recovery. Do not accept customer payments or promise high availability until these controls are implemented and reviewed.
