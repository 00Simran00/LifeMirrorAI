import streamlit as st
from database.db import get_profile, get_moods, get_journals, save_scores
from utils.auth import require_auth
from utils.styles import inject_theme, progress_ring, kpi_card
from utils.scoring import (physical_score, mental_score, lifestyle_score,
                           overall_score, status_label)
from utils.charts import gauge

st.set_page_config(page_title="Digital Twin", page_icon="🪞", layout="wide")
inject_theme()
user = require_auth()
st.markdown('<div class="hero-title">🪞 Digital Health Twin</div>', unsafe_allow_html=True)

profile = get_profile(user["id"])
if not profile:
    st.warning("Complete your profile first."); st.stop()

moods = get_moods(user["id"]); journals = get_journals(user["id"])
phys = physical_score(profile); life = lifestyle_score(profile)
ment = mental_score(moods, journals); overall = overall_score(phys, ment, life)
label, color = status_label(overall)
save_scores(user["id"], phys, ment, life, overall)

st.markdown(f"""
<div class="glass" style="text-align:center;">
  <svg width="160" height="220" viewBox="0 0 160 220">
    <circle cx="80" cy="40" r="26" fill="none" stroke="{color}" stroke-width="3"/>
    <rect x="55" y="70" width="50" height="80" rx="20" fill="none" stroke="{color}" stroke-width="3"/>
    <line x1="55" y1="90" x2="25" y2="130" stroke="{color}" stroke-width="3"/>
    <line x1="105" y1="90" x2="135" y2="130" stroke="{color}" stroke-width="3"/>
    <line x1="68" y1="150" x2="60" y2="205" stroke="{color}" stroke-width="3"/>
    <line x1="92" y1="150" x2="100" y2="205" stroke="{color}" stroke-width="3"/>
  </svg>
  <h3 style="color:{color}; font-family:Orbitron;">Twin Status: {label}</h3>
</div>""", unsafe_allow_html=True)

st.write("")
rings = st.columns(4)
with rings[0]: st.markdown(progress_ring(overall, "Overall"), unsafe_allow_html=True)
with rings[1]: st.markdown(progress_ring(phys, "Physical"), unsafe_allow_html=True)
with rings[2]: st.markdown(progress_ring(ment, "Mental"), unsafe_allow_html=True)
with rings[3]: st.markdown(progress_ring(life, "Lifestyle"), unsafe_allow_html=True)

st.plotly_chart(gauge(overall, "Overall Wellness Index"), use_container_width=True)