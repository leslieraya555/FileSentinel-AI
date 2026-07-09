from datetime import timedelta
from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE_DIR / "data" / "events.csv"
MODEL_FILE = BASE_DIR / "ml" / "model.pkl"

FEATURE_COLUMNS = [
    "modify_count",
    "delete_count",
    "rename_count",
    "create_count",
    "access_count",
    "events_per_second",
]


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


def extract_features():
    df = load_events()

    if df.empty:
        return None

    latest_time = df["timestamp"].max()
    recent = df[df["timestamp"] >= latest_time - timedelta(seconds=10)]

    features = {
        "modify_count": int((recent["event_type"] == "MODIFY").sum()),
        "delete_count": int((recent["event_type"] == "DELETE").sum()),
        "rename_count": int(recent["event_type"].isin(["RENAMED_FROM", "RENAMED_TO"]).sum()),
        "create_count": int((recent["event_type"] == "CREATE").sum()),
        "access_count": int((recent["event_type"] == "ACCESS").sum()),
        "events_per_second": len(recent) / 10.0,
    }

    return pd.DataFrame([features], columns=FEATURE_COLUMNS)


def get_ml_prediction():
    if not MODEL_FILE.exists():
        return {
            "status": "MODEL_NOT_FOUND",
            "risk_score": 0,
            "message": "Run python3 ml/train_model.py to create the model.",
        }

    features = extract_features()

    if features is None:
        return {
            "status": "NO_DATA",
            "risk_score": 0,
            "message": "No file-system events are available yet.",
        }

    try:
        model = joblib.load(MODEL_FILE)
        prediction = int(model.predict(features)[0])
    except Exception as error:
        return {
            "status": "MODEL_ERROR",
            "risk_score": 0,
            "message": f"Could not run the ML model: {error}",
        }

    feature_values = features.iloc[0].to_dict()

    if prediction == -1:
        return {
            "status": "ANOMALY_DETECTED",
            "risk_score": 90,
            "message": "The model detected abnormal file-system activity.",
            "features": feature_values,
        }

    return {
        "status": "NORMAL",
        "risk_score": 10,
        "message": "File-system activity appears normal.",
        "features": feature_values,
    }
