from datetime import timedelta
from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE_DIR / "data" / "events.csv"
MODEL_FILE = BASE_DIR / "ml" / "model.pkl"


def load_model():
    if not MODEL_FILE.exists():
        return None

    try:
        return joblib.load(MODEL_FILE)
    except Exception:
        return None


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


def extract_features():
    df = load_events()

    if df.empty:
        return None

    now = df["timestamp"].max()
    window_start = now - timedelta(seconds=10)
    recent = df[df["timestamp"] >= window_start]

    features = {
        "modify_count": len(recent[recent["event_type"] == "MODIFY"]),
        "delete_count": len(recent[recent["event_type"] == "DELETE"]),
        "rename_count": len(recent[recent["event_type"].isin(["RENAMED_FROM", "RENAMED_TO"])]),
        "create_count": len(recent[recent["event_type"] == "CREATE"]),
        "access_count": len(recent[recent["event_type"] == "ACCESS"]),
        "events_per_second": len(recent) / 10
    }

    return pd.DataFrame([features])


def get_ml_prediction():
    model = load_model()

    if model is None:
        return {
            "status": "MODEL_NOT_FOUND",
            "risk_score": 0,
            "message": "ML model not found. Run ml/train_model.py first."
        }

    features = extract_features()

    if features is None:
        return {
            "status": "NO_DATA",
            "risk_score": 0,
            "message": "No file events available yet."
        }

    prediction = model.predict(features)[0]

    if prediction == -1:
        return {
            "status": "ANOMALY_DETECTED",
            "risk_score": 90,
            "message": "The ML model detected abnormal file-system behavior.",
            "features": features.to_dict(orient="records")[0]
        }

    return {
        "status": "NORMAL",
        "risk_score": 10,
        "message": "File activity appears normal.",
        "features": features.to_dict(orient="records")[0]
    }