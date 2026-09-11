from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EVENTS_FILE = DATA_DIR / "events.csv"


def ensure_data_files():
    DATA_DIR.mkdir(exist_ok=True)

    if not EVENTS_FILE.exists():
        EVENTS_FILE.write_text("timestamp,event_type,file_name,file_path\n")