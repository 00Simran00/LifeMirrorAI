import streamlit as st
import copy
from database.db import get_profile, get_moods
from utils.auth import require_auth
from utils.styles import inject_theme, kpi_card
from utils.scoring import physical_score, mental_score, lifestyle_score, overall_score
from utils.ml import predict_risks
from utils.charts import trend_line

st.set_page_config(page_title="What-If Simulator", page_icon="🧪", layout="wide")
inject_theme()
user = require_auth()
st.markdown('<div class="hero-title">🧪 What-If Health Simulator</div>', unsafe_allow_html=True)

profile = get_profile(user["id"])
if not profile:
    st.warning("Complete your profile first."); st.stop()

moods = get_moods(user["id"])
avg_stress = sum(m["stress_level"] for m in moods)/len(moods) if moods else 5

st.markdown("#### Adjust your habits and see the future change instantly")
c = st.columns(4)
sleep = c[0].slider("Sleep (hrs)", 0.0, 12.0, float(profile["sleep_hours"]))
screen = c[1].slider("Screen (hrs)", 0.0, 16.0, float(profile["screen_time"]))
ex = c[2].slider("Exercise (min)", 0, 180, int(profile["exercise_minutes"]))
water = c[3].slider("Water (L)", 0.0, 6.0, float(profile["water_intake"]))

sim = copy.deepcopy(profile)
sim.update(sleep_hours=sleep, screen_time=screen, exercise_minutes=ex, water_intake=water)

# BEFORE
b_life = lifestyle_score(profile); b_phys = physical_score(profile)
b_ment = mental_score(moods, [])
b_overall = overall_score(b_phys, b_ment, b_life)
b_risks = predict_risks(profile, avg_stress)

# AFTER
a_life = lifestyle_score(sim); a_phys = physical_score(sim)
a_overall = overall_score(a_phys, b_ment, a_life)
a_risks = predict_risks(sim, avg_stress)

st.write("")
c1, c2, c3 = st.columns(3)
with c1: st.markdown(kpi_card("Before", b_overall), unsafe_allow_html=True)
with c2: st.markdown(kpi_card("After", a_overall), unsafe_allow_html=True)
delta = round(a_overall - b_overall, 1)
with c3: st.markdown(kpi_card("Improvement", f"{'+' if delta>=0 else ''}{delta}", "%"),
                     unsafe_allow_html=True)

st.markdown("#### Risk Comparison (Before → After)")
for k in b_risks:
    before, after = b_risks[k], a_risks[k]
    st.write(f"**{k.replace('_',' ').title()}**")
    st.progress(min(1.0, after/100),
                text=f"{before}% → {after}% ({'↓' if after<before else '↑'}{abs(round(after-before,1))})")

labels = [k.replace("_"," ").title() for k in b_risks]
st.plotly_chart(trend_line(labels,
    {"Before": list(b_risks.values()), "After": list(a_risks.values())},
    "Disease Risk: Before vs After"), use_container_width=True)