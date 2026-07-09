from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ml_detector import get_ml_prediction
from rule_detector import detect_suspicious_activity

BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE_DIR / "data" / "events.csv"

app = FastAPI(title="FileSentinel AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "FileSentinel AI backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/events")
def get_events():
    if not EVENTS_FILE.exists():
        return []

    try:
        df = pd.read_csv(EVENTS_FILE)
    except (pd.errors.EmptyDataError, OSError):
        return []

    if df.empty:
        return []

    return df.tail(100).fillna("").to_dict(orient="records")


@app.get("/stats")
def get_stats():
    empty_stats = {
        "total_events": 0,
        "create_events": 0,
        "modify_events": 0,
        "delete_events": 0,
        "rename_events": 0,
        "access_events": 0,
    }

    if not EVENTS_FILE.exists():
        return empty_stats

    try:
        df = pd.read_csv(EVENTS_FILE)
    except (pd.errors.EmptyDataError, OSError):
        return empty_stats

    if df.empty or "event_type" not in df.columns:
        return empty_stats

    return {
        "total_events": len(df),
        "create_events": int((df["event_type"] == "CREATE").sum()),
        "modify_events": int((df["event_type"] == "MODIFY").sum()),
        "delete_events": int((df["event_type"] == "DELETE").sum()),
        "rename_events": int(df["event_type"].isin(["RENAMED_FROM", "RENAMED_TO"]).sum()),
        "access_events": int((df["event_type"] == "ACCESS").sum()),
    }


@app.get("/alerts/ml")
def ml_alert():
    return get_ml_prediction()


@app.get("/alerts/rules")
def rule_alerts():
    return detect_suspicious_activity()
