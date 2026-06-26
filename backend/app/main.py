import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings

logger = logging.getLogger("uvicorn.error")

from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.routers import (
    analysis,
    anomalies,
    automl,
    chat,
    cleaning,
    comparison,
    dashboard,
    experiment_lab,
    experiments,
    forecast,
    health,
    insights,
    model_arena,
    profile,
    query,
    report,
    report_v2,
    root_cause,
    samples,
    sql,
    storytelling,
    team,
    upload,
    visualize,
    xai,
)

app = FastAPI(
    title="Prisma AI API",
    description="Intelligent data analysis copilot backend",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)


def _cors_headers(origin: str | None) -> dict[str, str]:
    if origin and origin in settings.cors_origin_list:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=_cors_headers(request.headers.get("origin")),
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers=_cors_headers(request.headers.get("origin")),
    )


@app.exception_handler(ResponseValidationError)
async def response_validation_handler(request: Request, exc: ResponseValidationError):
    logger.exception("Response validation failed for %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Response validation failed"},
        headers=_cors_headers(request.headers.get("origin")),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error for %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=_cors_headers(request.headers.get("origin")),
    )


app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(profile.router)
app.include_router(health.router)
app.include_router(insights.router)
app.include_router(anomalies.router)
app.include_router(visualize.router)
app.include_router(forecast.router)
app.include_router(automl.router)
app.include_router(xai.router)
app.include_router(chat.router)
app.include_router(query.router)
app.include_router(report.router)
app.include_router(report_v2.router)
app.include_router(root_cause.router)
app.include_router(storytelling.router)
app.include_router(comparison.router)
app.include_router(cleaning.router)
app.include_router(sql.router)
app.include_router(dashboard.router)
app.include_router(experiments.router)
app.include_router(experiment_lab.router)
app.include_router(model_arena.router)
app.include_router(samples.router)
app.include_router(team.router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "prisma-ai-backend",
        "version": "3.0.0",
        "llm_provider": settings.resolved_llm_provider(),
    }
