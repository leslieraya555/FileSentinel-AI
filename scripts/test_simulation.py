from datetime import datetime
from pathlib import Path
import csv
import time

BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_FILE = BASE_DIR / "data" / "events.csv"

def ensure_events_file():
    EVENTS_FILE.parent.mkdir(exist_ok=True)

    if not EVENTS_FILE.exists():
        with open(EVENTS_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "event_type", "file_name", "file_path"])

def add_event(event_type, file_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = f"/Users/leslieitzel/watch_folder/{file_name}"

    with open(EVENTS_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, event_type, file_name, file_path])

def simulate_normal_activity():
    add_event("CREATE", "normal_notes.txt")
    time.sleep(0.2)
    add_event("MODIFY", "normal_notes.txt")
    time.sleep(0.2)
    add_event("ACCESS", "normal_notes.txt")

def simulate_ransomware_like_activity():
    for i in range(50):
        add_event("CREATE", f"file_{i}.txt")

    for i in range(50):
        add_event("MODIFY", f"file_{i}.txt")

    for i in range(25):
        add_event("RENAMED_TO", f"file_{i}.locked")

    for i in range(15):
        add_event("DELETE", f"file_{i}.txt")

if __name__ == "__main__":
    ensure_events_file()

    print("Adding normal file activity...")
    simulate_normal_activity()

    print("Adding suspicious ransomware-like file activity...")
    simulate_ransomware_like_activity()

    print(f"Simulation complete. Events written to {EVENTS_FILE}")
