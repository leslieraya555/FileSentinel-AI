from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

MODEL_FILE = Path(__file__).resolve().parent / "model.pkl"

training_data = pd.DataFrame({
    "modify_count": [0, 1, 2, 3, 5, 8, 10, 40, 55, 70, 90, 120],
    "delete_count": [0, 0, 0, 1, 1, 2, 2, 8, 12, 20, 30, 40],
    "rename_count": [0, 0, 1, 1, 2, 2, 3, 15, 25, 40, 55, 70],
    "create_count": [0, 1, 2, 3, 5, 8, 10, 25, 45, 60, 80, 100],
    "access_count": [0, 1, 2, 3, 4, 5, 8, 20, 35, 50, 65, 80],
    "events_per_second": [0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 6.0, 8.0, 12.0, 16.0, 22.0],
})

model = IsolationForest(contamination=0.25, random_state=42)
model.fit(training_data)

joblib.dump(model, MODEL_FILE)

print(f"Model trained and saved to: {MODEL_FILE}")
