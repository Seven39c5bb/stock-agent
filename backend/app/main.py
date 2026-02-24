import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import AnalysisResponse, StockQuery
from .services.analyzer import analyze_stock

app = FastAPI(title="Stock Intel Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.on_event("startup")
def apply_proxy_settings() -> None:
    if settings.http_proxy:
        os.environ["HTTP_PROXY"] = settings.http_proxy
        os.environ["http_proxy"] = settings.http_proxy
    if settings.https_proxy:
        os.environ["HTTPS_PROXY"] = settings.https_proxy
        os.environ["https_proxy"] = settings.https_proxy
    if settings.no_proxy:
        os.environ["NO_PROXY"] = settings.no_proxy
        os.environ["no_proxy"] = settings.no_proxy


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(payload: StockQuery) -> AnalysisResponse:
    try:
        result = analyze_stock(payload.query)
        return AnalysisResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guardrail
        detail = str(exc) if settings.debug else "Analysis failed"
        raise HTTPException(status_code=500, detail=detail) from exc
