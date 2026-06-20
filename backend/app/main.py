from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import anomalies, automl, chat, forecast, insights, profile, query, report, upload, visualize, xai

app = FastAPI(
    title="Prisma AI API",
    description="Intelligent data analysis copilot backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(profile.router)
app.include_router(insights.router)
app.include_router(anomalies.router)
app.include_router(visualize.router)
app.include_router(forecast.router)
app.include_router(automl.router)
app.include_router(xai.router)
app.include_router(chat.router)
app.include_router(query.router)
app.include_router(report.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "prisma-ai-backend"}
