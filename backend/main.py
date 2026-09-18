"""FastAPI service for telemetry, statistics, and security assessments.

Author: Leslie Raya
GitHub: https://github.com/leslieraya555
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.config import EVENTS_FILE, MAX_API_EVENTS, MODEL_FILE, allowed_origins
from backend.database import ensure_event_store, load_events, serialize_events, summarize_events
from backend.ml_detector import get_ml_prediction
from backend.rule_detector import detect_suspicious_activity


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepare persistent resources before accepting requests."""
    ensure_event_store()
    yield


app = FastAPI(
    title="FileSentinel AI API",
    version="2.0.0",
    description="Explainable file-system monitoring with rules and anomaly detection.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home() -> dict[str, str]:
    """Return API identity and interactive documentation location."""
    return {"service": "FileSentinel AI", "version": "2.0.0", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, object]:
    """Report operational dependencies used by external health checks."""
    return {
        "status": "healthy",
        "event_store_ready": EVENTS_FILE.exists(),
        "model_ready": MODEL_FILE.exists(),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/events")
def get_events(limit: int = Query(MAX_API_EVENTS, ge=1, le=1000)) -> list[dict[str, str]]:
    """Return the newest validated telemetry records."""
    return serialize_events(load_events(limit=limit))


@app.get("/stats")
def get_stats() -> dict[str, int]:
    """Return aggregate event counts for the full stored dataset."""
    return summarize_events(load_events())


@app.get("/alerts/rules")
def rule_alerts() -> list[dict[str, object]]:
    """Return explainable alerts triggered by the latest activity window."""
    return detect_suspicious_activity()


@app.get("/alerts/ml")
def ml_alert() -> dict[str, object]:
    """Return the anomaly detector's latest assessment and evidence."""
    return get_ml_prediction()


@app.get("/overview")
def overview(limit: int = Query(MAX_API_EVENTS, ge=1, le=1000)) -> dict[str, object]:
    """Return one consistent snapshot for efficient dashboard refreshes."""
    events = load_events()
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "stats": summarize_events(events),
        "events": serialize_events(events.tail(limit)),
        "rule_alerts": detect_suspicious_activity(events),
        "ml_alert": get_ml_prediction(events),
    }