import streamlit as st
from datetime import datetime
from collections import Counter
from database.db import add_journal, get_journals, add_mood, get_moods
from utils.auth import require_auth
from utils.styles import inject_theme, progress_ring
from utils.nlp_engine import analyze_text, wellness_from_journals
from utils.charts import sentiment_pie, trend_line

st.set_page_config(page_title="Emotion Engine", page_icon="💖", layout="wide")
inject_theme()
user = require_auth()
st.markdown('<div class="hero-title">💖 Emotion Intelligence Engine</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Journal", "😊 Mood Log"])

with tab1:
    text = st.text_area("How are you feeling today?", height=120)
    if st.button("Analyze Entry") and text.strip():
        r = analyze_text(text)
        add_journal(user["id"], text, r["polarity"], r["polarity"], r["subjectivity"], r["emotion"])
        st.success(f"Sentiment: {r['sentiment']} | Emotion: {r['emotion'].title()} | Polarity: {r['polarity']}")

with tab2:
    c = st.columns(4)
    mood = c[0].selectbox("Mood", ["Happy", "Calm", "Neutral", "Stressed", "Sad"])
    mscore = c[1].slider("Mood (1-10)", 1, 10, 6)
    stress = c[2].slider("Stress (1-10)", 1, 10, 4)
    energy = c[3].slider("Energy (1-10)", 1, 10, 6)
    if st.button("Log Mood"):
        add_mood(user["id"], mood, mscore, stress, energy)
        st.success("Mood logged!")

journals = get_journals(user["id"]); moods = get_moods(user["id"])
wellness = wellness_from_journals(journals)

st.write("")
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown(progress_ring(wellness, "Mental Wellness"), unsafe_allow_html=True)
with col2:
    if journals:
        counts = Counter(j["emotion"] for j in journals)
        st.plotly_chart(sentiment_pie(dict(counts)), use_container_width=True)
    else:
        st.info("Add journal entries to see your emotion distribution.")

if journals:
    js = list(reversed(journals))
    st.plotly_chart(trend_line(list(range(len(js))),
                    {"Polarity": [j["polarity"] for j in js]}, "Emotional Trend"),
                    use_container_width=True)
if moods:
    ms = list(reversed(moods))
    st.plotly_chart(trend_line(list(range(len(ms))),
                    {"Mood": [m["mood_score"] for m in ms],
                     "Stress": [m["stress_level"] for m in ms]}, "Mood vs Stress"),
                    use_container_width=True)