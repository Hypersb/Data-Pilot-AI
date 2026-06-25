# Changelog

All notable changes to Prisma AI are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0-rc.1] - 2026-06-24

### Added

- Next.js 16 web application as the primary product UI (landing, upload, analysis hub, chat, report)
- V3 analysis bundle endpoint (`GET /api/sessions/{id}/analysis`)
- Sample dataset catalog and one-click load (`/api/samples`)
- Model Arena API and frontend page for tabular model comparison
- Experiment Lab and experiment tracking endpoints
- Multi-agent team analysis, root cause, storytelling, and data health scoring
- PDF and PowerPoint executive report export (`/api/sessions/{id}/report/v2`)
- Natural-language data cleaning with audit trail
- SQL generation (educational, non-executing)
- GitHub Actions CI for backend pytest and frontend build
- Repository governance: CONTRIBUTING, SECURITY, CODE_OF_CONDUCT
- Cross-platform dev scripts (`scripts/start-dev.ps1`, `scripts/start-dev.sh`)

### Changed

- Rebranded product to **Prisma AI** (open-source release candidate)
- Documentation updated: Next.js is the primary UI; Streamlit is optional
- Docker image bundles `sample-data/` and brand assets for demo datasets in containers

### Notes

- API health endpoint reports version `3.0.0` (internal API version)
- GitHub release tag: `v3.0.0-rc.1`
- Sessions are in-memory with TTL; no authentication in this release
- Ollama is optional; heuristic tool routing works without a local LLM

[3.0.0-rc.1]: https://github.com/Hypersb/Data-Pilot-AI/releases/tag/v3.0.0-rc.1
