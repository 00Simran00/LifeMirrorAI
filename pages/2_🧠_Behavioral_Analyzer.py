import streamlit as st
from database.db import get_profile
from utils.auth import require_auth
from utils.styles import inject_theme, progress_ring
from utils.scoring import lifestyle_score
from utils.charts import radar, gauge

st.set_page_config(page_title="Behavioral Analyzer", page_icon="🧠", layout="wide")
inject_theme()
user = require_auth()
st.markdown('<div class="hero-title">🧠 Behavioral Health Analyzer</div>', unsafe_allow_html=True)

profile = get_profile(user["id"])
if not profile:
    st.warning("Complete your profile first."); st.stop()

sleep = profile["sleep_hours"]; screen = profile["screen_time"]
ex = profile["exercise_minutes"]; water = profile["water_intake"]
life = lifestyle_score(profile)

insights = []
if sleep < 6: insights.append("😴 Sleep deprivation detected — aim for 7–8 hours.")
if screen > 7: insights.append("📱 Excessive screen time — high digital addiction risk.")
if ex < 20: insights.append("🪑 Sedentary lifestyle — add 30 min daily movement.")
if water < 2: insights.append("💧 Low hydration — increase water intake.")
if not insights: insights.append("✅ Excellent behavioral balance — keep it up!")

c1, c2 = st.columns([1, 1])
with c1:
    cats = ["Sleep", "Activity", "Hydration", "Screen Balance", "Routine"]
    vals = [min(100, sleep/8*100), min(100, ex/60*100), min(100, water/3*100),
            max(0, 100-screen/12*100), life]
    st.plotly_chart(radar(cats, [round(v,1) for v in vals]), use_container_width=True)
with c2:
    st.plotly_chart(gauge(life, "Lifestyle Score"), use_container_width=True)

st.markdown('<h4>🔍 Behavioral Insights</h4>', unsafe_allow_html=True)
for i in insights:
    st.markdown(f'<div class="glass" style="margin-bottom:10px;">{i}</div>', unsafe_allow_html=True)