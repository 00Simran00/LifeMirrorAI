"""
utils/ml.py
Load joblib models and produce risk percentages. Falls back to a
heuristic estimator if model files are missing (so the app never crashes).
"""
import os
import joblib
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TARGETS = ["obesity", "diabetes", "hypertension",
           "sleep_disorder", "depression", "burnout"]
FEATURES = ["age", "gender", "bmi", "sleep", "water", "exercise",
            "screen", "smoking", "alcohol", "stress"]

_cache = {}


def _load(target):
    if target in _cache:
        return _cache[target]
    path = os.path.join(MODELS_DIR, f"{target}_model.joblib")
    model = joblib.load(path) if os.path.exists(path) else None
    _cache[target] = model
    return model


def build_feature_vector(profile, avg_stress=5):
    gender = 1 if (profile.get("gender") == "Male") else 0
    smoking = 1 if profile.get("smoking") == "Yes" else 0
    alcohol = {"None": 0, "Moderate": 1, "Heavy": 2}.get(profile.get("alcohol"), 0)
    return np.array([[
        profile.get("age") or 30, gender, profile.get("bmi") or 24,
        profile.get("sleep_hours") or 7, profile.get("water_intake") or 2,
        profile.get("exercise_minutes") or 30, profile.get("screen_time") or 5,
        smoking, alcohol, avg_stress
    ]])


def _heuristic(profile, avg_stress):
    bmi = profile.get("bmi") or 24
    sleep = profile.get("sleep_hours") or 7
    screen = profile.get("screen_time") or 5
    ex = profile.get("exercise_minutes") or 30
    return {
        "obesity": min(95, max(5, (bmi - 22) * 6)),
        "diabetes": min(95, max(5, (bmi - 22) * 3 + avg_stress * 2)),
        "hypertension": min(95, max(5, (bmi - 22) * 3 + avg_stress * 3)),
        "sleep_disorder": min(95, max(5, (7 - sleep) * 12 + screen * 3)),
        "depression": min(95, max(5, avg_stress * 6 + (7 - sleep) * 5)),
        "burnout": min(95, max(5, avg_stress * 7 + screen * 3 - ex * 0.3)),
    }


def predict_risks(profile, avg_stress=5):
    """Return dict target -> risk percentage (0-100)."""
    X = build_feature_vector(profile, avg_stress)
    out = {}
    any_model = False
    for t in TARGETS:
        m = _load(t)
        if m is not None:
            any_model = True
            try:
                prob = m.predict_proba(X)[0][1]
                out[t] = round(float(prob) * 100, 1)
            except Exception:
                out[t] = None
        else:
            out[t] = None
    if not any_model or any(v is None for v in out.values()):
        h = _heuristic(profile, avg_stress)
        for t in TARGETS:
            if out.get(t) is None:
                out[t] = round(h[t], 1)
    return out