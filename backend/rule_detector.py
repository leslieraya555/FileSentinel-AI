"""Explainable threshold rules for ransomware-like event bursts.

Author: Leslie Raya
GitHub: https://github.com/leslieraya555
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import pandas as pd

from backend.config import EVENT_WINDOW_SECONDS
from backend.database import load_events


@dataclass(frozen=True)
class DetectionRule:
    """Describe one auditable threshold and its alert metadata."""

    event_types: tuple[str, ...]
    threshold: int
    severity: str
    alert_type: str
    risk_score: int
    action: str


RULES = (
    DetectionRule(
        ("MODIFY",),
        30,
        "HIGH",
        "MASS_MODIFICATION",
        90,
        "isolate the host and inspect changed files",
    ),
    DetectionRule(
        ("DELETE",),
        10,
        "CRITICAL",
        "MASS_DELETION",
        95,
        "stop destructive processes and begin recovery",
    ),
    DetectionRule(
        ("RENAMED_FROM", "RENAMED_TO"),
        20,
        "HIGH",
        "MASS_RENAME",
        85,
        "inspect renamed extensions and active processes",
    ),
    DetectionRule(
        ("CREATE",),
        40,
        "MEDIUM",
        "MASS_CREATION",
        70,
        "review the creating process and destination",
    ),
)


def recent_window(events: pd.DataFrame, window_seconds: int = EVENT_WINDOW_SECONDS) -> pd.DataFrame:
    """Select records within the configured interval of the newest event."""
    if events.empty:
        return events

    # Anchoring to captured telemetry supports repeatable offline investigations.
    newest_event = events["timestamp"].max()
    return events[events["timestamp"] >= newest_event - timedelta(seconds=window_seconds)]


def detect_suspicious_activity(
    events: pd.DataFrame | None = None,
    window_seconds: int = EVENT_WINDOW_SECONDS,
) -> list[dict[str, object]]:
    """Evaluate recent activity and return every triggered detection rule."""
    event_frame = load_events() if events is None else events
    recent = recent_window(event_frame, window_seconds)
    if recent.empty:
        return []

    alerts: list[dict[str, object]] = []
    for rule in RULES:
        count = int(recent["event_type"].isin(rule.event_types).sum())
        if count < rule.threshold:
            continue

        labels = "/".join(rule.event_types)
        alerts.append(
            {
                "severity": rule.severity,
                "type": rule.alert_type,
                "message": f"{count} {labels} events occurred within {window_seconds} seconds.",
                "risk_score": rule.risk_score,
                "event_count": count,
                "threshold": rule.threshold,
                "recommended_action": rule.action,
            }
        )

    return sorted(alerts, key=lambda alert: int(alert["risk_score"]), reverse=True)