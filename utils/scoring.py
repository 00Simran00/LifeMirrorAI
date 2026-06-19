"""
utils/scoring.py
Deterministic health score engine: Physical, Mental, Lifestyle, Overall.
"""


def calc_bmi(weight, height_cm):
    if not weight or not height_cm:
        return 0.0
    h = height_cm / 100.0
    return round(weight / (h * h), 1)


def _clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def physical_score(profile):
    """0-100 from BMI, exercise, smoking, alcohol."""
    bmi = profile.get("bmi") or 0
    ex = profile.get("exercise_minutes") or 0
    score = 100
    if bmi:
        if bmi < 18.5 or bmi > 30:
            score -= 30
        elif bmi > 25:
            score -= 15
    score -= max(0, (30 - ex)) * 0.8           # reward exercise
    if profile.get("smoking") == "Yes":
        score -= 20
    if profile.get("alcohol") == "Heavy":
        score -= 15
    elif profile.get("alcohol") == "Moderate":
        score -= 6
    return round(_clamp(score), 1)


def lifestyle_score(profile):
    """Sleep, water, screen time, exercise."""
    sleep = profile.get("sleep_hours") or 0
    water = profile.get("water_intake") or 0
    screen = profile.get("screen_time") or 0
    ex = profile.get("exercise_minutes") or 0
    score = 100
    score -= abs(7.5 - sleep) * 6              # ideal ~7.5h
    score -= max(0, (2.5 - water)) * 10        # ideal >=2.5L
    score -= max(0, (screen - 4)) * 5          # penalty >4h screen
    score -= max(0, (30 - ex)) * 0.6
    return round(_clamp(score), 1)


def mental_score(mood_logs, journals):
    """From mood/stress logs + journal sentiment."""
    if not mood_logs and not journals:
        return 60.0
    score = 100
    if mood_logs:
        avg_stress = sum(m["stress_level"] for m in mood_logs) / len(mood_logs)
        avg_mood = sum(m["mood_score"] for m in mood_logs) / len(mood_logs)
        score -= avg_stress * 5
        score += (avg_mood - 5) * 3
    if journals:
        avg_pol = sum(j["polarity"] for j in journals) / len(journals)
        score += avg_pol * 25
    return round(_clamp(score), 1)


def overall_score(physical, mental, lifestyle):
    return round(physical * 0.35 + mental * 0.35 + lifestyle * 0.30, 1)


def status_label(score):
    if score >= 80:
        return "Excellent", "#00e5ff"
    if score >= 65:
        return "Good", "#5cff9d"
    if score >= 45:
        return "Moderate", "#ffb627"
    return "Needs Attention", "#ff4d6d"