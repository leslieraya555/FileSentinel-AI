from datetime import timedelta
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE_DIR / "data" / "events.csv"


def load_events() -> pd.DataFrame:
    if not EVENTS_FILE.exists():
        return pd.DataFrame(columns=["timestamp", "event_type", "file_name", "file_path"])

    try:
        df = pd.read_csv(EVENTS_FILE)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["timestamp", "event_type", "file_name", "file_path"])

    if df.empty or "timestamp" not in df.columns:
        return pd.DataFrame(columns=["timestamp", "event_type", "file_name", "file_path"])

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    return df


def detect_suspicious_activity():
    df = load_events()

    if df.empty:
        return []

    now = df["timestamp"].max()
    window_start = now - timedelta(seconds=10)
    recent = df[df["timestamp"] >= window_start]

    modify_count = len(recent[recent["event_type"] == "MODIFY"])
    delete_count = len(recent[recent["event_type"] == "DELETE"])
    rename_count = len(recent[recent["event_type"].isin(["RENAMED_FROM", "RENAMED_TO"])])
    create_count = len(recent[recent["event_type"] == "CREATE"])

    alerts = []

    if modify_count >= 30:
        alerts.append({
            "severity": "HIGH",
            "type": "MASS_MODIFICATION",
            "message": f"{modify_count} files were modified in the last 10 seconds.",
            "risk_score": 90
        })

    if delete_count >= 10:
        alerts.append({
            "severity": "HIGH",
            "type": "MASS_DELETION",
            "message": f"{delete_count} files were deleted in the last 10 seconds.",
            "risk_score": 95
        })

    if rename_count >= 20:
        alerts.append({
            "severity": "MEDIUM",
            "type": "MASS_RENAME",
            "message": f"{rename_count} rename events happened in the last 10 seconds.",
            "risk_score": 80
        })

    if create_count >= 40:
        alerts.append({
            "severity": "MEDIUM",
            "type": "MASS_CREATION",
            "message": f"{create_count} files were created in the last 10 seconds.",
            "risk_score": 70
        })

    return alerts