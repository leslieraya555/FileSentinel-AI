"""Machine-learning anomaly detection for file-system event bursts.

Author: Leslie Raya
GitHub: https://github.com/leslieraya555

Load a trained anomaly detector, summarize captured activity, and return
a prediction with supporting features. An anomaly requires investigation;
it is not proof of malicious activity.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from backend.config import EVENT_WINDOW_SECONDS, MODEL_FILE
from backend.database import load_events
from backend.rule_detector import recent_window


# Training and prediction must use the same feature names and order.
FEATURE_COLUMNS = [
    "modify_count",
    "delete_count",
    "rename_count",
    "create_count",
    "access_count",
    "events_per_second",
]


@lru_cache(maxsize=2)
def _load_model_cached(model_path: str, modified_at_ns: int):
    """Reuse the model until its file modification time changes."""
    # The timestamp is part of the cache key, not an argument to joblib.
    del modified_at_ns

    # Load only model files created or obtained from a trusted source.
    return joblib.load(model_path)


def load_model(path: Path | None = None):
    """Return the saved estimator, or None if it cannot be loaded."""
    target = Path(path) if path is not None else Path(MODEL_FILE)

    try:
        modified_at_ns = target.stat().st_mtime_ns
        return _load_model_cached(str(target.resolve()), modified_at_ns)
    except (OSError, ValueError, EOFError):
        return None


def extract_features(
    events: pd.DataFrame | None = None,
    window_seconds: int = EVENT_WINDOW_SECONDS,
) -> pd.DataFrame | None:
    """Convert the newest captured activity window into one feature row."""
    event_frame = load_events() if events is None else events
    recent = recent_window(event_frame, window_seconds)

    if recent.empty:
        return None

    event_types = recent["event_type"]

    # Counts represent event records, not unique files or processes.
    features = {
        "modify_count": int((event_types == "MODIFY").sum()),
        "delete_count": int((event_types == "DELETE").sum()),
        "rename_count": int(
            event_types.isin(["RENAMED_FROM", "RENAMED_TO"]).sum()
        ),
        "create_count": int((event_types == "CREATE").sum()),
        "access_count": int((event_types == "ACCESS").sum()),
        # Average over the configured window, including quiet intervals.
        "events_per_second": round(len(recent) / window_seconds, 3),
    }

    return pd.DataFrame([features], columns=FEATURE_COLUMNS)


def _risk_from_decision(decision: float, prediction: int) -> int:
    """Map the model output to a heuristic display score.

    This score is not a calibrated probability of ransomware.
    """
    if prediction == -1:
        return min(99, max(70, int(70 + abs(decision) * 150)))

    return min(49, max(1, int(25 - decision * 60)))


def get_ml_prediction(
    events: pd.DataFrame | None = None,
    model_path: Path | None = None,
) -> dict[str, object]:
    """Return the anomaly assessment and the features used to produce it."""
    model = load_model(model_path)

    if model is None:
        # Retain this status name for compatibility with existing callers.
        # A missing assessment must not be interpreted as normal activity.
        return {
            "status": "MODEL_NOT_FOUND",
            "risk_score": 0,
            "message": (
                "The model is missing or could not be loaded. "
                "Train it with: python3 -m ml.train_model"
            ),
            "features": None,
        }

    features = extract_features(events)

    if features is None:
        return {
            "status": "NO_DATA",
            "risk_score": 0,
            "message": "No file-system events are available for assessment.",
            "features": None,
        }

    try:
        prediction = int(model.predict(features)[0])
        decision = float(model.decision_function(features)[0])
    except (ValueError, AttributeError) as error:
        return {
            "status": "MODEL_ERROR",
            "risk_score": 0,
            "message": (
                "The saved model could not evaluate the current "
                f"features: {error}"
            ),
            "features": features.iloc[0].to_dict(),
        }

    anomaly = prediction == -1

    return {
        "status": "ANOMALY_DETECTED" if anomaly else "NORMAL",
        "risk_score": _risk_from_decision(decision, prediction),
        "message": (
            "Unusual file-system activity requires investigation."
            if anomaly
            else "Activity is within the learned baseline."
        ),
        "decision_score": round(decision, 4),
        "features": features.iloc[0].to_dict(),
    }