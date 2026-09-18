"""Validated access to the CSV event store used by all detectors.

Author: Leslie Raya
GitHub: https://github.com/leslieraya555
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.config import EVENTS_FILE

EVENT_COLUMNS = ["timestamp", "event_type", "file_name", "file_path"]
KNOWN_EVENT_TYPES = {
    "CREATE",
    "MODIFY",
    "DELETE",
    "RENAMED_FROM",
    "RENAMED_TO",
    "ACCESS",
}


def ensure_event_store(path: Path | None = None) -> Path:
    """Create the event directory and a schema-only CSV when absent."""
    target = path or EVENTS_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.stat().st_size == 0:
        pd.DataFrame(columns=EVENT_COLUMNS).to_csv(target, index=False)
    return target


def load_events(path: Path | None = None, limit: int | None = None) -> pd.DataFrame:
    """Load normalized events while rejecting malformed telemetry rows.

    Args:
        path: Optional dataset location used by tests and offline analysis.
        limit: Optional number of newest valid records to return.

    Returns:
        A DataFrame with a stable schema and timezone-aware timestamps.
    """
    target = path or EVENTS_FILE
    if not target.exists() or target.stat().st_size == 0:
        return pd.DataFrame(columns=EVENT_COLUMNS)

    try:
        events = pd.read_csv(target, usecols=lambda column: column in EVENT_COLUMNS)
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError, ValueError):
        return pd.DataFrame(columns=EVENT_COLUMNS)

    if not set(EVENT_COLUMNS).issubset(events.columns):
        return pd.DataFrame(columns=EVENT_COLUMNS)

    # Invalid timestamps cannot be assigned to a reliable detection window.
    # Mixed precision is expected because kernel and simulation timestamps may
    # include either whole seconds or fractional seconds.
    events["timestamp"] = pd.to_datetime(
        events["timestamp"],
        errors="coerce",
        utc=True,
        format="mixed",
    )
    events["event_type"] = events["event_type"].astype(str).str.upper().str.strip()
    events = events.dropna(subset=["timestamp"])
    events = events[events["event_type"].isin(KNOWN_EVENT_TYPES)]
    events[["file_name", "file_path"]] = events[["file_name", "file_path"]].fillna("")
    events = events.sort_values("timestamp")

    return events.tail(limit).reset_index(drop=True) if limit else events.reset_index(drop=True)


def summarize_events(events: pd.DataFrame) -> dict[str, int]:
    """Calculate dashboard totals from a normalized event collection."""
    if events.empty:
        counts: dict[str, int] = {}
    else:
        counts = events["event_type"].value_counts().to_dict()

    return {
        "total_events": int(len(events)),
        "create_events": int(counts.get("CREATE", 0)),
        "modify_events": int(counts.get("MODIFY", 0)),
        "delete_events": int(counts.get("DELETE", 0)),
        "rename_events": int(counts.get("RENAMED_FROM", 0) + counts.get("RENAMED_TO", 0)),
        "access_events": int(counts.get("ACCESS", 0)),
    }


def serialize_events(events: pd.DataFrame) -> list[dict[str, str]]:
    """Convert normalized telemetry into JSON-safe API records."""
    if events.empty:
        return []

    output = events.copy()
    output["timestamp"] = output["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return output[EVENT_COLUMNS].to_dict(orient="records")