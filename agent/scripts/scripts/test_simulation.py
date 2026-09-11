import os
import time
from pathlib import Path


WATCH_FOLDER = Path.home() / "watch_folder"


def create_test_files():
    WATCH_FOLDER.mkdir(exist_ok=True)

    for i in range(50):
        file_path = WATCH_FOLDER / f"test_file_{i}.txt"

        with open(file_path, "w") as file:
            file.write("safe test data\n")

    print("Created 50 test files.")


def modify_test_files():
    for i in range(50):
        file_path = WATCH_FOLDER / f"test_file_{i}.txt"

        with open(file_path, "a") as file:
            file.write("modified quickly\n")

    print("Modified 50 test files quickly.")


def rename_test_files():
    for i in range(20):
        old_path = WATCH_FOLDER / f"test_file_{i}.txt"
        new_path = WATCH_FOLDER / f"renamed_file_{i}.locked"

        if old_path.exists():
            old_path.rename(new_path)

    print("Renamed 20 files.")


def delete_test_files():
    for file_path in WATCH_FOLDER.glob("*"):
        file_path.unlink()

    print("Deleted all test files.")


if __name__ == "__main__":
    print(f"Using watch folder: {WATCH_FOLDER}")

    create_test_files()
    time.sleep(2)

    modify_test_files()
    time.sleep(2)

    rename_test_files()
    time.sleep(2)

    delete_test_files()

    print("Safe ransomware-like behavior simulation complete.")
    