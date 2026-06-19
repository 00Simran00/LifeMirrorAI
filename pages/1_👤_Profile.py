import streamlit as st
from database.db import upsert_profile, get_profile, save_scores
from utils.auth import require_auth
from utils.styles import inject_theme
from utils.scoring import calc_bmi, physical_score, lifestyle_score, mental_score, overall_score

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")
inject_theme()
user = require_auth()

st.markdown('<div class="hero-title">👤 Profile Management</div>', unsafe_allow_html=True)
profile = get_profile(user["id"]) or {}

with st.form("profile_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", 10, 100, int(profile.get("age") or 25))
        gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                              index=["Male", "Female", "Other"].index(profile.get("gender", "Male")))
        height = st.number_input("Height (cm)", 100.0, 230.0, float(profile.get("height") or 170))
        weight = st.number_input("Weight (kg)", 30.0, 200.0, float(profile.get("weight") or 70))
    with c2:
        sleep = st.slider("Sleep Duration (hrs)", 0.0, 12.0, float(profile.get("sleep_hours") or 7))
        water = st.slider("Water Intake (L)", 0.0, 6.0, float(profile.get("water_intake") or 2))
        exercise = st.slider("Daily Exercise (min)", 0, 180, int(profile.get("exercise_minutes") or 30))
        screen = st.slider("Screen Time (hrs)", 0.0, 16.0, float(profile.get("screen_time") or 5))
    with c3:
        diet = st.selectbox("Diet Type", ["Balanced", "Vegetarian", "Vegan", "Keto", "High-Carb", "Junk"])
        smoking = st.selectbox("Smoking", ["No", "Yes"])
        alcohol = st.selectbox("Alcohol", ["None", "Moderate", "Heavy"])

    if st.form_submit_button("💾 Save Profile"):
        bmi = calc_bmi(weight, height)
        data = dict(age=age, gender=gender, height=height, weight=weight, bmi=bmi,
                    sleep_hours=sleep, water_intake=water, exercise_minutes=exercise,
                    screen_time=screen, diet_type=diet, smoking=smoking, alcohol=alcohol)
        upsert_profile(user["id"], data)
        p = physical_score(data); l = lifestyle_score(data); m = mental_score([], [])
        save_scores(user["id"], p, m, l, overall_score(p, m, l))
        st.success(f"✅ Profile saved! Your BMI is {bmi}")

profile = get_profile(user["id"])
if profile:
    st.markdown(f"""
    <div class="glass">
      <h4>📋 Current Profile</h4>
      <p>BMI: <b>{profile['bmi']}</b> • Sleep: {profile['sleep_hours']}h •
      Water: {profile['water_intake']}L • Exercise: {profile['exercise_minutes']}min •
      Screen: {profile['screen_time']}h • Diet: {profile['diet_type']}</p>
    </div>""", unsafe_allow_html=True)