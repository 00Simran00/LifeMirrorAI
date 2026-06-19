"""
datasets/generate_data.py
Generates synthetic but realistic training data for the 6 risk models.
Run: python datasets/generate_data.py
"""
import numpy as np
import pandas as pd
import os

OUT = os.path.join(os.path.dirname(__file__), "health_dataset.csv")


def generate(n=5000, seed=42):
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 75, n)
    gender = rng.integers(0, 2, n)                 # 0 F, 1 M
    bmi = rng.normal(26, 5, n).clip(15, 45)
    sleep = rng.normal(6.8, 1.4, n).clip(3, 10)
    water = rng.normal(2.1, 0.8, n).clip(0.3, 5)
    exercise = rng.normal(28, 20, n).clip(0, 120)
    screen = rng.normal(6, 2.5, n).clip(1, 14)
    smoking = rng.integers(0, 2, n)
    alcohol = rng.integers(0, 3, n)                # 0 none,1 mod,2 heavy
    stress = rng.integers(1, 11, n)

    df = pd.DataFrame(dict(age=age, gender=gender, bmi=bmi, sleep=sleep,
                           water=water, exercise=exercise, screen=screen,
                           smoking=smoking, alcohol=alcohol, stress=stress))

    # Generate labels with logical risk relationships + noise
    def prob(x): return (1 / (1 + np.exp(-x)))

    df["obesity"] = (prob((df.bmi - 28) * 0.5 - df.exercise * 0.02) > rng.random(n)).astype(int)
    df["diabetes"] = (prob((df.bmi - 27) * 0.3 + df.age * 0.02 + df.alcohol * 0.3
                           - df.exercise * 0.01) > rng.random(n)).astype(int)
    df["hypertension"] = (prob((df.bmi - 26) * 0.25 + df.age * 0.03 + df.smoking * 0.8
                              + df.alcohol * 0.4 + df.stress * 0.1) > rng.random(n)).astype(int)
    df["sleep_disorder"] = (prob((6.5 - df.sleep) * 0.9 + df.screen * 0.15
                                + df.stress * 0.15) > rng.random(n)).astype(int)
    df["depression"] = (prob(df.stress * 0.3 + (6.5 - df.sleep) * 0.4
                            - df.exercise * 0.02 + df.screen * 0.1 - 2) > rng.random(n)).astype(int)
    df["burnout"] = (prob(df.stress * 0.35 + df.screen * 0.2 + (6.5 - df.sleep) * 0.3
                         - df.exercise * 0.015 - 2) > rng.random(n)).astype(int)

    df.to_csv(OUT, index=False)
    print(f"✅ Dataset saved -> {OUT} ({len(df)} rows)")
    return df


if __name__ == "__main__":
    generate()