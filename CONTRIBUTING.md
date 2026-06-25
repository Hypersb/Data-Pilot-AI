# Contributing to Prisma AI

Thank you for your interest in contributing. Prisma AI is an open-source data analysis platform built with FastAPI and Next.js.

## Getting started

1. Fork the repository and clone your fork.
2. Install backend dependencies:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   ```

4. Start development servers:

   - **Windows:** `.\scripts\start-dev.ps1` from the repo root
   - **macOS / Linux:** `./scripts/start-dev.sh` from the repo root

   Or manually:

   ```bash
   # Terminal 1 — backend on :8080
   cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

   # Terminal 2 — frontend on :3000
   cd frontend && npm run dev
   ```

## Running tests

```bash
cd backend
python -m pytest tests/ -v
```

```bash
cd frontend
npm run build
npm run lint
```

## Pull request guidelines

- Open an issue first for large changes or new features.
- Keep PRs focused — one logical change per pull request.
- Ensure backend tests pass and the frontend builds.
- Follow existing code style and naming conventions.
- Do not commit secrets, `.env` files, or build artifacts.
- Update documentation when behavior or setup steps change.

## Commit messages

Use clear, conventional prefixes when helpful:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation only
- `chore:` maintenance, tooling
- `test:` tests only
- `refactor:` code change without behavior change

## Code of conduct

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before participating.

## Security

Report vulnerabilities privately — see [SECURITY.md](SECURITY.md).

## Questions

Open a [GitHub Discussion](https://github.com/Hypersb/Data-Pilot-AI/discussions) or issue for questions about setup or architecture.
