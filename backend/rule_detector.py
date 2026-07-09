from datetime import timedelta
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE_DIR / "data" / "events.csv"


def load_events():
    columns = ["timestamp", "event_type", "file_name", "file_path"]

    if not EVENTS_FILE.exists():
        return pd.DataFrame(columns=columns)

    try:
        df = pd.read_csv(EVENTS_FILE)
    except (pd.errors.EmptyDataError, OSError):
        return pd.DataFrame(columns=columns)

    if df.empty or "timestamp" not in df.columns or "event_type" not in df.columns:
        return pd.DataFrame(columns=columns)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df.dropna(subset=["timestamp"])


def detect_suspicious_activity():
    df = load_events()

    if df.empty:
        return []

    latest_time = df["timestamp"].max()
    recent = df[df["timestamp"] >= latest_time - timedelta(seconds=10)]

    modify_count = int((recent["event_type"] == "MODIFY").sum())
    delete_count = int((recent["event_type"] == "DELETE").sum())
    rename_count = int(recent["event_type"].isin(["RENAMED_FROM", "RENAMED_TO"]).sum())
    create_count = int((recent["event_type"] == "CREATE").sum())

    alerts = []

    if modify_count >= 30:
        alerts.append({
            "severity": "HIGH",
            "type": "MASS_MODIFICATION",
            "message": f"{modify_count} files were modified in 10 seconds.",
            "risk_score": 90,
        })

    if delete_count >= 10:
        alerts.append({
            "severity": "HIGH",
            "type": "MASS_DELETION",
            "message": f"{delete_count} files were deleted in 10 seconds.",
            "risk_score": 95,
        })

    if rename_count >= 20:
        alerts.append({
            "severity": "MEDIUM",
            "type": "MASS_RENAME",
            "message": f"{rename_count} rename events happened in 10 seconds.",
            "risk_score": 80,
        })

    if create_count >= 40:
        alerts.append({
            "severity": "MEDIUM",
            "type": "MASS_CREATION",
            "message": f"{create_count} files were created in 10 seconds.",
            "risk_score": 70,
        })

    return alerts
