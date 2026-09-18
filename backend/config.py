"""Central configuration for paths, detection windows, and web origins.

Author: Leslie Raya
GitHub: https://github.com/leslieraya555
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("FILESENTINEL_DATA_DIR", PROJECT_ROOT / "data"))
EVENTS_FILE = Path(os.getenv("FILESENTINEL_EVENTS_FILE", DATA_DIR / "events.csv"))
MODEL_FILE = Path(os.getenv("FILESENTINEL_MODEL_FILE", PROJECT_ROOT / "ml" / "model.pkl"))
MODEL_METADATA_FILE = MODEL_FILE.with_name("model_metadata.json")

EVENT_WINDOW_SECONDS = int(os.getenv("FILESENTINEL_EVENT_WINDOW_SECONDS", "10"))
MAX_API_EVENTS = int(os.getenv("FILESENTINEL_MAX_API_EVENTS", "100"))


def allowed_origins() -> list[str]:
    """Return configured browser origins accepted by the API."""
    raw_origins = os.getenv(
        "FILESENTINEL_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
