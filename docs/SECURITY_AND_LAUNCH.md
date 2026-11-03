# Security, privacy, and launch checklist

## Current safeguards
- Password hashes and HTTP-only session cookies
- CSRF protection and configured CORS allow-list
- Per-user conversation and project ownership checks
- Project file path validation, source/text extension allow-list, file-count and character limits
- Project files stored as text and never executed by the application
- Retrieved project and knowledge content is treated as untrusted prompt data
- Model provider credentials remain server-side
- Chat message and request limits

## Important current limitations
- Project context ingestion is not a malware scanner or secret scanner.
- Users must not upload credentials, API tokens, environment secrets, private keys, customer data, or confidential material.
- The retrieval engine is lexical and may miss related information; it does not prove that all project files were reviewed.
- Provider API calls may send prompts and retrieved project snippets to the configured third-party model service.
- Basic usage tokens are character-based estimates, not billing data.
- In-memory rate limits are not suitable for multi-instance production.
- The repository still uses create_all for startup; use migrations for future production schema changes.

## Required before public launch
- Replace the development secret with a cryptographically random secret.
- Use HTTPS and secure cookies; verify origins and SameSite settings.
- Add Redis-backed limits, per-plan quotas, provider token accounting and spend limits.
- Add email verification, password reset, account deletion, and data export.
- Add project file secret detection/redaction, retention/deletion controls and user consent.
- Add prompt-injection testing for project source files and retrieved content.
- Add moderation, user reporting, and acceptable-use enforcement.
- Use managed database migrations, encrypted backups, restore drills, and monitoring.
- Publish clear privacy and provider-disclosure notices.
- Conduct independent application/API security review.
- Review Nepal legal, privacy, consumer, payment, and tax requirements with qualified local advisers.

This is an early-stage development product, not a security certification or production launch approval.
