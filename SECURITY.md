# Security Policy

## Supported development status

SkillForge AI is an early-stage application. It is not yet approved for handling sensitive personal, financial, medical, or confidential business information.

## Reporting a vulnerability

Please do not publish exploitable vulnerability details in a public issue. Once the project has a dedicated security contact, reports should be sent privately to that contact. Until then, use GitHub's private vulnerability reporting feature if it is enabled for the repository.

Include the affected component, impact, reproduction steps, and any suggested mitigation. Do not access, modify, or retain another person's data while investigating.

## Before production

- Keep provider API keys and application secrets on the server; never commit `.env` files.
- Enforce HTTPS and secure cookie settings.
- Configure trusted origins and CSRF protection.
- Apply rate limits and request-size limits at the application and edge layers.
- Review authentication, session expiry, password reset, and account deletion flows.
- Configure encrypted backups, retention, and deletion procedures.
- Review model-provider data retention and privacy terms before sending user content.
- Run dependency and application security scans, then conduct an independent review.
