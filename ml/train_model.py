"""Reproducible training and validation for the anomaly detector.

Author: Leslie Raya
GitHub: https://github.com/leslieraya555
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_recall_fscore_support

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = PROJECT_ROOT / "ml" / "model.pkl"
METADATA_FILE = PROJECT_ROOT / "ml" / "model_metadata.json"
RANDOM_SEED = 42

FEATURE_COLUMNS = [
    "modify_count",
    "delete_count",
    "rename_count",
    "create_count",
    "access_count",
    "events_per_second",
]


def generate_normal_activity(rows: int, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Create varied, low-volume activity for unsupervised baseline training."""
    rng = np.random.default_rng(seed)
    activity = pd.DataFrame(
        {
            "modify_count": rng.poisson(4.0, rows),
            "delete_count": rng.poisson(0.35, rows),
            "rename_count": rng.poisson(0.6, rows),
            "create_count": rng.poisson(3.0, rows),
            "access_count": rng.poisson(6.0, rows),
        }
    )
    total_events = activity.sum(axis=1)
    activity["events_per_second"] = (total_events / 10.0).round(3)
    return activity[FEATURE_COLUMNS]


def generate_attack_scenarios(rows: int, seed: int = RANDOM_SEED + 1) -> pd.DataFrame:
    """Create labeled ransomware-like bursts used only for validation."""
    rng = np.random.default_rng(seed)
    attacks = pd.DataFrame(
        {
            "modify_count": rng.integers(35, 150, rows),
            "delete_count": rng.integers(8, 55, rows),
            "rename_count": rng.integers(18, 90, rows),
            "create_count": rng.integers(25, 120, rows),
            "access_count": rng.integers(5, 90, rows),
        }
    )
    attacks["events_per_second"] = (attacks.sum(axis=1) / 10.0).round(3)
    return attacks[FEATURE_COLUMNS]


def train_model() -> tuple[IsolationForest, dict[str, object]]:
    """Fit on normal behavior, validate on held-out normal and attack scenarios."""
    training_data = generate_normal_activity(1500)
    normal_validation = generate_normal_activity(300, RANDOM_SEED + 2)
    attack_validation = generate_attack_scenarios(300)

    # Attack examples remain outside fitting so the estimator learns a clean baseline.
    model = IsolationForest(
        n_estimators=300,
        contamination=0.02,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(training_data)

    validation = pd.concat([normal_validation, attack_validation], ignore_index=True)
    expected = np.concatenate([np.zeros(len(normal_validation)), np.ones(len(attack_validation))])
    predicted = (model.predict(validation) == -1).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        expected,
        predicted,
        average="binary",
        zero_division=0,
    )

    metadata: dict[str, object] = {
        "author": "Leslie Raya",
        "trained_at": datetime.now(UTC).isoformat(),
        "algorithm": "IsolationForest",
        "random_seed": RANDOM_SEED,
        "training_rows": len(training_data),
        "validation_rows": len(validation),
        "features": FEATURE_COLUMNS,
        "metrics": {
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "false_positive_rate": round(
                float((predicted[: len(normal_validation)] == 1).mean()),
                4,
            ),
        },
        "limitations": [
            "Synthetic training distributions require calibration with production telemetry.",
            "An anomaly identifies unusual behavior and is not proof of malware.",
        ],
    }
    return model, metadata


def main() -> None:
    """Train, persist, and summarize the reproducible model artifact."""
    model, metadata = train_model()
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    METADATA_FILE.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"Model saved to: {MODEL_FILE}")
    print(f"Validation metrics: {metadata['metrics']}")


if __name__ == "__main__":
    main()
