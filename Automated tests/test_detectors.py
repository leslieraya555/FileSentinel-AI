"""Behavior tests for rule and feature detection.

Author: Leslie Raya
"""

from backend.ml_detector import extract_features
from backend.rule_detector import detect_suspicious_activity


def test_normal_activity_does_not_trigger_rules(normal_events) -> None:
    assert detect_suspicious_activity(normal_events) == []


def test_suspicious_activity_triggers_expected_rules(suspicious_events) -> None:
    alert_types = {alert["type"] for alert in detect_suspicious_activity(suspicious_events)}
    assert alert_types == {"MASS_MODIFICATION", "MASS_DELETION", "MASS_RENAME", "MASS_CREATION"}


def test_feature_order_matches_training_contract(suspicious_events) -> None:
    features = extract_features(suspicious_events)
    assert features is not None
    assert features.iloc[0]["modify_count"] == 45
    assert features.iloc[0]["delete_count"] == 12
    assert features.iloc[0]["events_per_second"] > 10
