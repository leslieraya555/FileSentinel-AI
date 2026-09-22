"""Safe telemetry simulation for demonstrations and detector testing.

Author: Leslie Raya
GitHub: https://github.com/leslieraya555
"""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EVENTS_FILE = PROJECT_ROOT / "data" / "events.csv"
CSV_HEADER = ["timestamp", "event_type", "file_name", "file_path"]


def append_event(writer: csv.writer, timestamp: datetime, event_type: str, name: str) -> None:
    """Write one synthetic record using the production event schema."""
    writer.writerow(
        [
            timestamp.isoformat(),
            event_type,
            name,
            f"/demo/watch-folder/{name}",
        ]
    )


def normal_events(start: datetime) -> list[tuple[datetime, str, str]]:
    """Return a small sequence representative of routine document editing."""
    return [
        (start, "CREATE", "notes.txt"),
        (start + timedelta(seconds=2), "MODIFY", "notes.txt"),
        (start + timedelta(seconds=4), "ACCESS", "notes.txt"),
    ]


def suspicious_events(start: datetime) -> list[tuple[datetime, str, str]]:
    """Return rapid bulk operations expected to trigger both detectors."""
    events: list[tuple[datetime, str, str]] = []
    for index in range(50):
        events.append((start + timedelta(milliseconds=index * 20), "CREATE", f"record_{index}.txt"))
        events.append(
            (start + timedelta(milliseconds=index * 20 + 5), "MODIFY", f"record_{index}.txt")
        )
    for index in range(25):
        events.append(
            (start + timedelta(milliseconds=index * 30), "RENAMED_TO", f"record_{index}.locked")
        )
    for index in range(15):
        events.append((start + timedelta(milliseconds=index * 40), "DELETE", f"record_{index}.txt"))
    return sorted(events, key=lambda item: item[0])


def write_simulation(path: Path, mode: str, reset: bool) -> int:
    """Append selected telemetry without creating or changing monitored files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    file_mode = "w" if reset or not path.exists() else "a"
    start = datetime.now(UTC).replace(microsecond=0)

    events: list[tuple[datetime, str, str]] = []
    if mode in {"normal", "both"}:
        events.extend(normal_events(start))
    if mode in {"suspicious", "both"}:
        attack_start = start + timedelta(seconds=20) if mode == "both" else start
        events.extend(suspicious_events(attack_start))

    with path.open(file_mode, newline="", encoding="utf-8") as event_file:
        writer = csv.writer(event_file)
        if file_mode == "w" or path.stat().st_size == 0:
            writer.writerow(CSV_HEADER)
        for timestamp, event_type, name in events:
            append_event(writer, timestamp, event_type, name)
    return len(events)


def parse_args() -> argparse.Namespace:
    """Parse explicit options so demonstrations are repeatable."""
    parser = argparse.ArgumentParser(description="Generate safe FileSentinel telemetry.")
    parser.add_argument("--mode", choices=("normal", "suspicious", "both"), default="both")
    parser.add_argument("--events-file", type=Path, default=DEFAULT_EVENTS_FILE)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Replace existing telemetry before simulation.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the requested telemetry-only demonstration."""
    args = parse_args()
    count = write_simulation(args.events_file, args.mode, args.reset)
    print(f"Wrote {count} safe synthetic events to {args.events_file}")
    print("No personal files were created, encrypted, renamed, or deleted.")


if __name__ == "__main__":
    main()