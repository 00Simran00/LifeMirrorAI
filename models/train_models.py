"""
models/train_models.py
Trains RandomForest + LogisticRegression for 6 risk targets.
Saves best model per target via joblib.
Run: python models/train_models.py
"""
import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "datasets", "health_dataset.csv")
FEATURES = ["age", "gender", "bmi", "sleep", "water", "exercise",
            "screen", "smoking", "alcohol", "stress"]
TARGETS = ["obesity", "diabetes", "hypertension",
           "sleep_disorder", "depression", "burnout"]


def train():
    if not os.path.exists(DATA):
        from datasets.generate_data import generate
        generate()
    df = pd.read_csv(DATA)
    X = df[FEATURES]

    for target in TARGETS:
        y = df[target]
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

        candidates = {
            "rf": Pipeline([("sc", StandardScaler()),
                            ("clf", RandomForestClassifier(n_estimators=200,
                                                           max_depth=8, random_state=42))]),
            "lr": Pipeline([("sc", StandardScaler()),
                            ("clf", LogisticRegression(max_iter=1000))]),
        }
        best, best_acc, best_name = None, 0, ""
        for name, pipe in candidates.items():
            pipe.fit(Xtr, ytr)
            acc = accuracy_score(yte, pipe.predict(Xte))
            if acc > best_acc:
                best, best_acc, best_name = pipe, acc, name

        path = os.path.join(HERE, f"{target}_model.joblib")
        joblib.dump(best, path)
        print(f"✅ {target}: {best_name} acc={best_acc:.3f} -> {path}")


if __name__ == "__main__":
    train()