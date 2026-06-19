"""
LifeMirror AI - AI Recommendation System
Rule-based personalized recommendations engine.
"""


def generate_recommendations(profile, scores, risks, emotional_states):
    """Generate prioritized health recommendations."""
    recs = []

    # Sleep
    if profile['sleep_duration'] < 7:
        recs.append({"icon": "😴", "category": "Sleep",
                     "text": "Aim for 7–9 hours of sleep. Set a consistent bedtime and avoid screens 1 hour before bed.",
                     "priority": "High"})
    # Exercise
    if profile['daily_exercise'] < 0.5:
        recs.append({"icon": "🏃", "category": "Exercise",
                     "text": "Increase physical activity to at least 30 minutes daily to boost cardiovascular health.",
                     "priority": "High"})
    # Water
    if profile['water_intake'] < 2:
        recs.append({"icon": "💧", "category": "Hydration",
                     "text": "Drink at least 2 liters of water daily to improve metabolism and energy.",
                     "priority": "Medium"})
    # BMI
    if profile['bmi'] >= 25:
        recs.append({"icon": "⚖️", "category": "Weight",
                     "text": "Your BMI is elevated. Focus on balanced nutrition and portion control.",
                     "priority": "High"})
    elif profile['bmi'] < 18.5:
        recs.append({"icon": "🍽️", "category": "Weight",
                     "text": "Your BMI is low. Increase nutrient-dense calorie intake.",
                     "priority": "Medium"})
    # Screen time
    if profile['screen_time'] > 6:
        recs.append({"icon": "📱", "category": "Digital Wellness",
                     "text": "Reduce screen time. Use the 20-20-20 rule and take regular digital detox breaks.",
                     "priority": "Medium"})
    # Smoking
    if profile['smoking_status'] == "Yes":
        recs.append({"icon": "🚭", "category": "Habits",
                     "text": "Quitting smoking dramatically lowers your disease risk. Consider a cessation program.",
                     "priority": "Critical"})
    # Mental health
    for state, _ in emotional_states:
        if "Stress" in state or "Burnout" in state:
            recs.append({"icon": "🧘", "category": "Mental Wellness",
                         "text": "Practice mindfulness or meditation 10 min daily to reduce stress & burnout risk.",
                         "priority": "High"})
            break
    # Risk-based
    if risks.get('diabetes', 0) > 50:
        recs.append({"icon": "🩸", "category": "Diabetes Prevention",
                     "text": "Elevated diabetes risk. Reduce sugar intake and schedule a blood glucose check.",
                     "priority": "Critical"})
    if risks.get('hypertension', 0) > 50:
        recs.append({"icon": "❤️", "category": "Heart Health",
                     "text": "High hypertension risk. Reduce sodium, manage stress, and monitor blood pressure.",
                     "priority": "Critical"})

    if not recs:
        recs.append({"icon": "✨", "category": "Great Job",
                     "text": "Your health metrics look excellent! Keep maintaining your healthy lifestyle.",
                     "priority": "Low"})
    return recs