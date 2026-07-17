"""Punto de entrada de la API de DISPOLA SAS."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configurar_logging
from app.core.middleware import CorrelationIdMiddleware

configurar_logging()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Chequeo de estado — usado para verificar el arranque end-to-end."""
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}
