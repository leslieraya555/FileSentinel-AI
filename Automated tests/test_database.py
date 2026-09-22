"""Validation tests for the CSV event store.

Author: Leslie Raya
"""

from pathlib import Path

from backend.database import EVENT_COLUMNS, ensure_event_store, load_events, summarize_events


def test_missing_store_returns_stable_schema(tmp_path: Path) -> None:
    events = load_events(tmp_path / "missing.csv")
    assert list(events.columns) == EVENT_COLUMNS
    assert events.empty


def test_invalid_rows_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,event_type,file_name,file_path\n"
        "2026-01-01T00:00:00Z,CREATE,valid.txt,/watch/valid.txt\n"
        "not-a-date,DELETE,bad.txt,/watch/bad.txt\n"
        "2026-01-01T00:00:01Z,UNKNOWN,ignored.txt,/watch/ignored.txt\n",
        encoding="utf-8",
    )
    events = load_events(path)
    assert len(events) == 1
    assert events.iloc[0]["file_name"] == "valid.txt"


def test_store_creation_and_summary(tmp_path: Path) -> None:
    path = ensure_event_store(tmp_path / "nested" / "events.csv")
    assert path.exists()
    assert summarize_events(load_events(path))["total_events"] == 0


def test_mixed_timestamp_precision_is_preserved(tmp_path: Path) -> None:
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,event_type,file_name,file_path\n"
        "2026-01-01T00:00:00Z,CREATE,first.txt,/watch/first.txt\n"
        "2026-01-01T00:00:00.125000Z,MODIFY,first.txt,/watch/first.txt\n",
        encoding="utf-8",
    )
    assert len(load_events(path)) == 2