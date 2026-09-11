from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import ensure_data_files
from ml_detector import get_ml_prediction
from rule_detector import detect_suspicious_activity


BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE_DIR / "data" / "events.csv"

app = FastAPI(title="FileSentinel AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensure_data_files()


@app.get("/")
def home():
    return {
        "message": "FileSentinel AI backend is running",
        "docs": "Go to /docs to test the API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/events")
def get_events():
    if not EVENTS_FILE.exists():
        return []

    try:
        df = pd.read_csv(EVENTS_FILE)
    except pd.errors.EmptyDataError:
        return []

    if df.empty:
        return []

    return df.tail(100).to_dict(orient="records")


@app.get("/stats")
def get_stats():
    if not EVENTS_FILE.exists():
        return {
            "total_events": 0,
            "create_events": 0,
            "modify_events": 0,
            "delete_events": 0,
            "rename_events": 0,
            "access_events": 0
        }

    try:
        df = pd.read_csv(EVENTS_FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["event_type"])

    if df.empty:
        return {
            "total_events": 0,
            "create_events": 0,
            "modify_events": 0,
            "delete_events": 0,
            "rename_events": 0,
            "access_events": 0
        }

    return {
        "total_events": len(df),
        "create_events": len(df[df["event_type"] == "CREATE"]),
        "modify_events": len(df[df["event_type"] == "MODIFY"]),
        "delete_events": len(df[df["event_type"] == "DELETE"]),
        "rename_events": len(df[df["event_type"].isin(["RENAMED_FROM", "RENAMED_TO"])]),
        "access_events": len(df[df["event_type"] == "ACCESS"])
    }


@app.get("/alerts/rules")
def get_rule_alerts():
    return detect_suspicious_activity()


@app.get("/alerts/ml")
def get_ml_alert():
    return get_ml_prediction()