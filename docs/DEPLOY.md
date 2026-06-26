# Deploying Prisma AI (quick reference)

**Full guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

## Production (5 minutes)

1. **Render** — deploy from [`render.yaml`](../render.yaml), set `CORS_ORIGINS` to your Vercel URL.
2. **Vercel** — root `frontend/`, set `NEXT_PUBLIC_API_URL` to Render URL.
3. Verify `/health` and upload a sample CSV.

## Local dev

```powershell
.\scripts\start-dev.ps1
```

Copy env templates:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```
