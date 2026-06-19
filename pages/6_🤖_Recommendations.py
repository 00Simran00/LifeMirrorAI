import streamlit as st
from database.db import get_profile, get_moods, save_recommendation
from utils.auth import require_auth
from utils.styles import inject_theme
from utils.ml import predict_risks

st.set_page_config(page_title="Recommendations", page_icon="🤖", layout="wide")
inject_theme()
user = require_auth()
st.markdown('<div class="hero-title">🤖 AI Recommendation System</div>', unsafe_allow_html=True)

profile = get_profile(user["id"])
if not profile:
    st.warning("Complete your profile first."); st.stop()

moods = get_moods(user["id"])
avg_stress = sum(m["stress_level"] for m in moods)/len(moods) if moods else 5
risks = predict_risks(profile, avg_stress)

recs = []
if profile["sleep_hours"] < 7:
    recs.append(("😴", "Sleep", "Increase sleep to 7–8 hrs. Try a consistent bedtime and no screens 1h before bed."))
if profile["water_intake"] < 2.5:
    recs.append(("💧", "Hydration", "Drink at least 2.5L water daily. Keep a bottle within reach."))
if profile["exercise_minutes"] < 30:
    recs.append(("🏃", "Exercise", "Aim for 30 min daily activity — brisk walking counts!"))
if profile["screen_time"] > 6:
    recs.append(("📱", "Screen Time", "Apply the 20-20-20 rule and set app limits to reduce digital strain."))
if (profile["bmi"] or 24) > 25:
    recs.append(("🥗", "Nutrition", "Adopt a balanced, calorie-aware diet to optimize BMI."))
if avg_stress > 6:
    recs.append(("🧘", "Mental", "Practice daily 10-min meditation or breathing to lower stress."))
if risks["diabetes"] >= 50:
    recs.append(("🩸", "Diabetes Risk", "Reduce refined sugar and schedule a glucose screening."))
if not recs:
    recs.append(("🌟", "Great Job", "Your habits are excellent — keep maintaining your wellness!"))

cols = st.columns(2)
for i, (icon, cat, msg) in enumerate(recs):
    save_recommendation(user["id"], cat, msg, icon)
    with cols[i % 2]:
        st.markdown(f"""
        <div class="glass" style="margin-bottom:14px;">
          <h3>{icon} {cat}</h3>
          <p style="color:#bcd;">{msg}</p>
        </div>""", unsafe_allow_html=True)