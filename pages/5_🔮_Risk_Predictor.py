import streamlit as st
from database.db import get_profile, get_moods, save_predictions
from utils.auth import require_auth
from utils.styles import inject_theme
from utils.ml import predict_risks
from utils.charts import risk_bar, trend_line

st.set_page_config(page_title="Risk Predictor", page_icon="🔮", layout="wide")
inject_theme()
user = require_auth()
st.markdown('<div class="hero-title">🔮 Future Health Risk Predictor</div>', unsafe_allow_html=True)

profile = get_profile(user["id"])
if not profile:
    st.warning("Complete your profile first."); st.stop()

moods = get_moods(user["id"])
avg_stress = sum(m["stress_level"] for m in moods)/len(moods) if moods else 5

with st.spinner("🧬 Running ML risk models..."):
    risks = predict_risks(profile, avg_stress)
save_predictions(user["id"], risks)

st.plotly_chart(risk_bar(risks), use_container_width=True)

# Future timeline projection (compounding risk drift)
years = list(range(0, 6))
series = {k.replace("_", " ").title(): [min(99, round(v*(1+0.05*y),1)) for y in years]
          for k, v in risks.items()}
st.markdown("<h4>📈 5-Year Risk Forecast</h4>", unsafe_allow_html=True)
st.plotly_chart(trend_line(years, series, "Projected Risk Trajectory"), use_container_width=True)

high = [k.replace('_',' ').title() for k, v in risks.items() if v >= 60]
if high:
    st.error(f"⚠️ Elevated risks: {', '.join(high)}. Visit Recommendations & What-If Simulator.")
else:
    st.success("✅ All major risks are within manageable ranges.")