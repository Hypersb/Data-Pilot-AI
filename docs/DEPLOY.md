# Deploying Prisma AI

## Frontend (Vercel)

1. Import the repository in [Vercel](https://vercel.com).
2. Set root directory to `frontend`.
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your Render API URL (e.g. `https://prisma-api.onrender.com`)
4. Deploy.

## Backend (Render)

1. Create a **Web Service** from `render.yaml` or connect the repo.
2. Use the Docker build from `backend/Dockerfile` (port **8000**).
3. Set `CORS_ORIGINS` to your Vercel URL.

## Local development

```powershell
# Windows
.\scripts\start-dev.ps1
```

- Frontend: http://localhost:3000
- Backend: http://127.0.0.1:8080

Copy `frontend/.env.local.example` to `frontend/.env.local` before running the frontend.

## Docker Compose (full stack + Ollama)

```bash
docker compose up --build
```

- API: http://localhost:8000
- Streamlit (optional): http://localhost:8501

## Live demo checklist

- [ ] Backend health: `GET /docs` returns OpenAPI UI
- [ ] Frontend loads landing page
- [ ] Sample dataset upload works end-to-end
- [ ] CORS allows frontend origin
