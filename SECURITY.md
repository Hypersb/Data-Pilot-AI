# Security Policy

## Supported versions

| Version   | Supported          |
| --------- | ------------------ |
| 3.0.x-rc  | :white_check_mark: |
| < 3.0     | :x:                |

## Reporting a vulnerability

**Please do not report security vulnerabilities in public GitHub issues.**

Instead, use one of these channels:

1. [GitHub Security Advisories](https://github.com/Hypersb/Data-Pilot-AI/security/advisories/new) (preferred)
2. Open a private report via repository maintainer contact if advisories are unavailable

Include:

- Description of the issue and potential impact
- Steps to reproduce
- Affected versions or commits
- Suggested fix (if any)

We aim to acknowledge reports within 7 days.

## Scope notes

Prisma AI v3.0.0-rc.1 is a **demo / portfolio release**:

- No user authentication
- In-memory session storage (data expires; not persisted securely)
- File uploads are processed in memory on the server
- Optional Ollama integration calls a local LLM endpoint — do not expose Ollama to the public internet without authentication

Do not deploy this release as-is for production multi-tenant workloads without addressing authentication, persistence, and upload hardening.

## Safe disclosure

We appreciate responsible disclosure and will credit reporters in release notes when fixes are published (unless you prefer to remain anonymous).
