"""Shared test fixtures for isolated FileSentinel datasets.

Author: Leslie Raya
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest


@pytest.fixture
def normal_events() -> pd.DataFrame:
    """Provide low-volume activity with valid UTC timestamps."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    rows = [
        (start, "CREATE", "notes.txt", "/watch/notes.txt"),
        (start + timedelta(seconds=2), "MODIFY", "notes.txt", "/watch/notes.txt"),
        (start + timedelta(seconds=4), "ACCESS", "notes.txt", "/watch/notes.txt"),
    ]
    return pd.DataFrame(rows, columns=["timestamp", "event_type", "file_name", "file_path"])


@pytest.fixture
def suspicious_events() -> pd.DataFrame:
    """Provide a concentrated event burst that exceeds every rule."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    rows: list[tuple[datetime, str, str, str]] = []
    event_counts = {"MODIFY": 45, "DELETE": 12, "RENAMED_TO": 22, "CREATE": 42}
    for event_type, count in event_counts.items():
        for index in range(count):
            timestamp = start + timedelta(milliseconds=index * 10)
            name = f"record_{event_type.lower()}_{index}.txt"
            rows.append((timestamp, event_type, name, f"/watch/{name}"))
    return pd.DataFrame(rows, columns=["timestamp", "event_type", "file_name", "file_path"])