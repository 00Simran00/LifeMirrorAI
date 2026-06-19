"""
app.py — LifeMirror AI main entry point.
Images are embedded as base64 so no external hosting is needed.
"""
import streamlit as st
from image_assets import IMG_CAPSULES, IMG_AI_HANDS, IMG_HOLOGRAM, IMG_DNA
from database.db import init_db, get_profile, get_moods, get_journals
from utils.auth import register, login, logout
from utils.scoring import (physical_score, mental_score, lifestyle_score,
                           overall_score, status_label)
from utils.charts import gauge

st.set_page_config(
    page_title="LifeMirror AI",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ─────────────────────────────────────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────────────────────────────────────
def inject_theme():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', sans-serif !important;
    background: #070c1a !important;
    color: #e2eaff !important;
}}

/* ── Animated orb layer ── */
[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 600px 500px at 8%  5%,  rgba(26,110,245,0.22) 0%, transparent 70%),
        radial-gradient(ellipse 500px 400px at 88% 30%, rgba(15,196,167,0.16) 0%, transparent 70%),
        radial-gradient(ellipse 400px 350px at 25% 88%, rgba(124,58,237,0.15) 0%, transparent 70%),
        radial-gradient(ellipse 300px 280px at 72% 82%, rgba(15,196,167,0.10) 0%, transparent 70%);
    animation: orb-drift 14s ease-in-out infinite alternate;
}}
@keyframes orb-drift {{
    0%   {{ transform: scale(1);    opacity: 1; }}
    100% {{ transform: scale(1.06); opacity: 0.85; }}
}}

/* ── Grid overlay ── */
[data-testid="stAppViewContainer"]::after {{
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,0.016) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.016) 1px, transparent 1px);
    background-size: 44px 44px;
}}

/* ── Sidebar — DNA helix background ── */
[data-testid="stSidebar"] {{
    background:
        linear-gradient(180deg, rgba(7,12,26,0.88) 0%, rgba(7,12,26,0.75) 100%),
        url("{IMG_DNA}") center/cover no-repeat !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    backdrop-filter: blur(2px);
}}
[data-testid="stSidebar"] * {{ color: #c8dcff !important; }}

[data-testid="stMain"], .main .block-container {{
    position: relative;
    z-index: 2;
}}
.block-container {{ padding: 1.5rem 2.5rem 4rem !important; max-width: 1140px !important; }}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background: rgba(255,255,255,0.04) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    gap: 4px !important;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 10px !important;
    color: rgba(180,210,255,0.5) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 8px 22px !important;
    transition: all 0.25s !important;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    background: rgba(26,110,245,0.22) !important;
    color: #7ab8ff !important;
    box-shadow: 0 0 0 1px rgba(26,110,245,0.4) inset !important;
}}
[data-testid="stTabPanel"] {{ padding-top: 20px !important; }}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stPasswordInput"] input {{
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e2eaff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}}
[data-testid="stTextInput"] input:focus,
[data-testid="stPasswordInput"] input:focus {{
    border-color: rgba(26,110,245,0.65) !important;
    box-shadow: 0 0 0 3px rgba(26,110,245,0.15) !important;
}}
[data-testid="stTextInput"] label,
[data-testid="stPasswordInput"] label {{
    color: rgba(180,210,255,0.55) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.4px !important;
}}

/* ── Buttons ── */
[data-testid="stFormSubmitButton"] button,
[data-testid="stButton"] button {{
    background: linear-gradient(135deg, #1a6ef5 0%, #0fc4a7 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px rgba(26,110,245,0.3) !important;
}}
[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stButton"] button:hover {{
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(26,110,245,0.45) !important;
}}

/* ── Alerts ── */
[data-testid="stSuccess"] {{
    background: rgba(15,196,167,0.1) !important;
    border: 1px solid rgba(15,196,167,0.3) !important;
    border-radius: 12px !important; color: #0fc4a7 !important;
}}
[data-testid="stError"] {{
    background: rgba(220,60,60,0.1) !important;
    border: 1px solid rgba(220,60,60,0.25) !important;
    border-radius: 12px !important; color: #ff7070 !important;
}}
[data-testid="stWarning"] {{
    background: rgba(245,163,26,0.1) !important;
    border: 1px solid rgba(245,163,26,0.3) !important;
    border-radius: 12px !important; color: #f5a31a !important;
}}
[data-testid="stInfo"] {{
    background: rgba(26,110,245,0.1) !important;
    border: 1px solid rgba(26,110,245,0.25) !important;
    border-radius: 12px !important; color: #7ab8ff !important;
}}

/* ── Plotly ── */
[data-testid="stPlotlyChart"] {{ border-radius: 18px !important; overflow: hidden; }}
.js-plotly-plot .plotly, .main-svg {{ background: transparent !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.03); }}
::-webkit-scrollbar-thumb {{ background: rgba(26,110,245,0.4); border-radius: 4px; }}

/* ── Hero title ── */
.hero-title {{
    font-size: 2.7rem;
    font-weight: 700;
    letter-spacing: -1.2px;
    background: linear-gradient(130deg, #ffffff 0%, #7ab8ff 35%, #0fc4a7 70%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 200% 200%;
    animation: grad-move 6s ease-in-out infinite alternate;
    line-height: 1.12;
    margin-bottom: 0.5rem;
}}
@keyframes grad-move {{
    0%   {{ background-position: 0%   50%; }}
    100% {{ background-position: 100% 50%; }}
}}

.hero-sub {{
    font-size: 1rem;
    color: rgba(180,210,255,0.52) !important;
    line-height: 1.65;
    max-width: 640px;
}}

/* ── ECG banner ── */
.ecg-banner {{
    width: 100%; overflow: hidden; height: 46px;
    margin: 8px 0 18px; opacity: 0.38; position: relative;
}}
.ecg-banner svg {{
    position: absolute; width: 200%;
    animation: ecg-run 3.4s linear infinite;
}}
@keyframes ecg-run {{
    from {{ transform: translateX(0); }}
    to   {{ transform: translateX(-50%); }}
}}

/* ── Auth hero image ── */
.auth-hero {{
    width: 100%;
    height: 220px;
    background:
        linear-gradient(180deg, rgba(7,12,26,0) 0%, rgba(7,12,26,0.85) 100%),
        url("{IMG_CAPSULES}") center/cover no-repeat;
    border-radius: 20px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    animation: hero-breathe 5s ease-in-out infinite alternate;
}}
@keyframes hero-breathe {{
    0%   {{ transform: scale(1);    filter: brightness(0.9); }}
    100% {{ transform: scale(1.02); filter: brightness(1.1); }}
}}
.auth-hero-text {{
    position: absolute;
    bottom: 18px; left: 22px;
}}

/* ── Logo pulse ── */
.logo-pulse {{
    font-size: 3.6rem;
    display: inline-block;
    animation: logo-beat 2.8s ease-in-out infinite;
    filter: drop-shadow(0 0 14px rgba(26,110,245,0.5));
}}
@keyframes logo-beat {{
    0%, 100% {{ transform: scale(1);    filter: drop-shadow(0 0 10px rgba(26,110,245,0.4)); }}
    50%       {{ transform: scale(1.1); filter: drop-shadow(0 0 26px rgba(15,196,167,0.75)); }}
}}

/* ── Auth card ── */
.auth-card {{
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 22px;
    padding: 28px 26px;
    backdrop-filter: blur(24px);
    box-shadow: 0 28px 80px rgba(0,0,0,0.5);
    animation: card-rise 0.65s cubic-bezier(0.16,1,0.3,1) both;
}}
@keyframes card-rise {{
    from {{ opacity: 0; transform: translateY(28px) scale(0.97); }}
    to   {{ opacity: 1; transform: translateY(0)    scale(1); }}
}}

/* ── Welcome banner with hologram image ── */
.welcome-band {{
    width: 100%;
    min-height: 130px;
    background:
        linear-gradient(90deg, rgba(7,12,26,0.92) 40%, rgba(7,12,26,0.55) 100%),
        url("{IMG_HOLOGRAM}") right center/cover no-repeat;
    border: 1px solid rgba(26,110,245,0.22);
    border-radius: 22px;
    padding: 26px 30px;
    margin-bottom: 26px;
    animation: card-rise 0.55s cubic-bezier(0.16,1,0.3,1) both;
    position: relative;
    overflow: hidden;
}}
.welcome-band h2 {{
    font-size: 1.3rem !important; font-weight: 600 !important;
    color: #d0e8ff !important; margin-bottom: 6px;
}}
.welcome-band p {{
    font-size: 13px;
    color: rgba(180,210,255,0.52) !important;
    line-height: 1.6; max-width: 520px;
}}

/* ── KPI card ── */
.kpi-card {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 20px 18px 16px;
    position: relative;
    overflow: hidden;
    animation: kpi-pop 0.55s cubic-bezier(0.16,1,0.3,1) both;
    transition: border-color 0.3s, transform 0.2s, box-shadow 0.3s;
}}
.kpi-card:hover {{
    border-color: rgba(26,110,245,0.45);
    transform: translateY(-3px);
    box-shadow: 0 14px 40px rgba(26,110,245,0.2);
}}
@keyframes kpi-pop {{
    from {{ opacity: 0; transform: scale(0.88); }}
    to   {{ opacity: 1; transform: scale(1); }}
}}
.kpi-label {{
    font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.7px; color: rgba(180,210,255,0.42);
    margin-bottom: 10px; font-weight: 500;
}}
.kpi-value {{
    font-size: 2.5rem; font-weight: 700; line-height: 1;
    background: linear-gradient(135deg, #fff 0%, rgba(200,220,255,0.72) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 14px;
}}
.kpi-bar {{ height: 4px; background: rgba(255,255,255,0.07); border-radius: 4px; overflow: hidden; }}
.kpi-fill {{ height: 100%; border-radius: 4px; transition: width 1.5s cubic-bezier(0.4,0,0.2,1); }}
.kpi-glow {{
    position: absolute; width: 110px; height: 110px;
    border-radius: 50%; top: -35px; right: -35px;
    opacity: 0.13; pointer-events: none;
}}
.kpi-delta {{ font-size: 11px; margin-top: 7px; font-weight: 500; }}
.d-up   {{ color: #0fc4a7; }}
.d-down {{ color: #f5591a; }}

/* ── Ring card ── */
.ring-card {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px; padding: 16px 10px;
    text-align: center;
    animation: kpi-pop 0.6s cubic-bezier(0.16,1,0.3,1) both;
    transition: border-color 0.3s, transform 0.2s;
}}
.ring-card:hover {{ border-color: rgba(15,196,167,0.4); transform: translateY(-2px); }}
.ring-lbl {{
    font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.6px; color: rgba(180,210,255,0.4);
    margin-top: 8px;
}}

/* ── AI insight banner with image ── */
.ai-glass {{
    background:
        linear-gradient(135deg, rgba(26,110,245,0.1) 0%, rgba(7,12,26,0.75) 100%),
        url("{IMG_AI_HANDS}") right center/cover no-repeat;
    border: 1px solid rgba(26,110,245,0.22);
    border-radius: 22px;
    padding: 24px 26px;
    margin-top: 22px;
    animation: kpi-pop 0.6s 0.25s cubic-bezier(0.16,1,0.3,1) both;
    min-height: 130px;
    position: relative;
    overflow: hidden;
}}
.ai-glass::before {{
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(90deg, rgba(7,12,26,0.82) 55%, transparent 100%);
    border-radius: inherit;
    pointer-events: none;
}}
.ai-glass-inner {{ position: relative; z-index: 1; max-width: 65%; }}
.ai-glass h4 {{ font-size: 15px; font-weight: 600; margin-bottom: 8px; }}
.ai-glass p  {{ font-size: 13px; color: rgba(180,210,255,0.58) !important; line-height: 1.65; }}

/* ── Section label ── */
.section-label {{
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.8px;
    color: rgba(180,210,255,0.28); font-weight: 600;
    margin: 26px 0 14px;
    display: flex; align-items: center; gap: 10px;
}}
.section-label::after {{
    content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.06);
}}

/* ── Pill badge ── */
.pill {{
    display: inline-block;
    background: rgba(15,196,167,0.12);
    border: 1px solid rgba(15,196,167,0.3);
    color: #0fc4a7; font-size: 11px; font-weight: 600;
    padding: 4px 12px; border-radius: 30px; letter-spacing: 0.4px;
    animation: pulse-pill 2.5s ease-in-out infinite;
}}
@keyframes pulse-pill {{
    0%, 100% {{ box-shadow: 0 0 0 0   rgba(15,196,167,0); }}
    50%       {{ box-shadow: 0 0 0 6px rgba(15,196,167,0.15); }}
}}

/* ── Status badge ── */
.sbadge {{
    display: inline-block; padding: 3px 13px;
    border-radius: 30px; font-size: 12px; font-weight: 600;
}}

/* ── Sparkline wrap ── */
.chart-wrap {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px; padding: 16px 18px;
    animation: kpi-pop 0.6s 0.1s cubic-bezier(0.16,1,0.3,1) both;
}}

/* ── Quick action card ── */
.qa-card {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px; padding: 18px 14px;
    text-align: center; cursor: pointer;
    animation: kpi-pop 0.55s cubic-bezier(0.16,1,0.3,1) both;
    transition: border-color 0.3s, transform 0.2s, box-shadow 0.25s;
}}
.qa-card:hover {{
    border-color: rgba(26,110,245,0.4);
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(26,110,245,0.18);
}}
.qa-icon {{ font-size: 1.9rem; margin-bottom: 8px; }}
.qa-title {{ font-size: 13px; font-weight: 600; color: #c8dcff; margin-bottom: 4px; }}
.qa-desc  {{ font-size: 11px; color: rgba(180,210,255,0.38); line-height: 1.45; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  COMPONENT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def ecg_banner() -> str:
    return """
<div class="ecg-banner">
  <svg viewBox="0 0 1400 46" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
    <defs>
      <linearGradient id="eg" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%"   stop-color="#1a6ef5"/>
        <stop offset="50%"  stop-color="#0fc4a7"/>
        <stop offset="100%" stop-color="#1a6ef5"/>
      </linearGradient>
    </defs>
    <polyline
      points="0,23 70,23 90,23 112,4 132,42 152,23 172,23 232,23
              252,23 272,4  292,42 312,23 332,23 392,23
              412,23 432,4  452,42 472,23 492,23 552,23
              572,23 592,4  612,42 632,23 652,23 712,23
              732,23 752,4  772,42 792,23 812,23 872,23
              892,23 912,4  932,42 952,23 972,23 1032,23
              1052,23 1072,4 1092,42 1112,23 1132,23 1192,23
              1212,23 1232,4 1252,42 1272,23 1400,23"
      fill="none" stroke="url(#eg)" stroke-width="1.8" stroke-linecap="round"/>
  </svg>
</div>
"""


def kpi_card(label: str, value: int, gradient: str,
             glow: str, delta: str = "") -> str:
    d = ""
    if delta:
        cls = "d-up" if delta.startswith("+") else "d-down"
        arrow = "▲" if delta.startswith("+") else "▼"
        d = f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'
    return f"""
<div class="kpi-card">
  <div class="kpi-glow" style="background:{glow};"></div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-bar"><div class="kpi-fill" style="width:{value}%;background:{gradient};"></div></div>
  {d}
</div>"""


def progress_ring(score: int, label: str, stroke: str) -> str:
    c = 2 * 3.14159 * 30
    f = (score / 100) * c
    e = c - f
    return f"""
<div class="ring-card">
  <svg width="80" height="80" viewBox="0 0 80 80">
    <circle cx="40" cy="40" r="30"
      fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="6"/>
    <circle cx="40" cy="40" r="30"
      fill="none" stroke="{stroke}" stroke-width="6" stroke-linecap="round"
      stroke-dasharray="{f:.1f} {e:.1f}"
      transform="rotate(-90 40 40)"
      style="transition:stroke-dasharray 1.4s cubic-bezier(0.4,0,0.2,1);"/>
    <text x="40" y="45" text-anchor="middle"
      font-size="14" font-weight="600" fill="#e2eaff"
      font-family="Inter,sans-serif">{score}</text>
  </svg>
  <div class="ring-lbl">{label}</div>
</div>"""


def section_label(text: str) -> str:
    return f'<div class="section-label">{text}</div>'


def status_badge(label: str, color: str) -> str:
    return (f'<span class="sbadge" style="background:{color}22;'
            f'border:1px solid {color}44;color:{color};">{label}</span>')


def qa_card(icon: str, title: str, desc: str) -> str:
    return f"""
<div class="qa-card">
  <div class="qa-icon">{icon}</div>
  <div class="qa-title">{title}</div>
  <div class="qa-desc">{desc}</div>
</div>"""


# ─────────────────────────────────────────────────────────────────────────────
#  AUTH SCREEN
# ─────────────────────────────────────────────────────────────────────────────
def auth_screen():
    # Hero image banner at the top
    st.markdown(f"""
<div class="auth-hero">
  <div class="auth-hero-text">
    <div class="hero-title" style="font-size:2rem;margin-bottom:4px;">🪞 LifeMirror AI</div>
    <p style="font-size:13px;color:rgba(200,230,255,0.6);">
      Predictive Digital Health Twin — powered by AI
    </p>
  </div>
</div>
{ecg_banner()}
""", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div style="text-align:center;margin-bottom:16px;">'
                    #'<span class="logo-pulse">🪞</span>'
                    '<div class="hero-title" style="font-size:1.9rem;">LifeMirror AI</div>'
                    '<p class="hero-sub" style="margin:6px auto 0;text-align:center;">'
                    'Your personalized AI healthcare companion.</p>'
                    '</div>', unsafe_allow_html=True)

        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔑 Login", "✨ Register"])

        with tab_login:
            with st.form("login_form"):
                u = st.text_input("Username", placeholder="Enter your username")
                p = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Login →"):
                    ok, msg = login(u, p)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()

        with tab_reg:
            with st.form("reg_form"):
                ru = st.text_input("Choose Username", placeholder="Pick a username")
                re = st.text_input("Email", placeholder="you@email.com")
                rp = st.text_input("Choose Password", type="password",
                                   placeholder="Min 8 characters")
                if st.form_submit_button("Create Account →"):
                    ok, msg = register(ru, re, rp)
                    (st.success if ok else st.error)(msg)

        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HOME DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def home_dashboard():
    user = st.session_state.user

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
<div style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.07);">
  <div style="font-size:1.05rem;font-weight:600;color:#c8dcff;margin-bottom:8px;">
    👋 {user['username']}
  </div>
  <span class="pill">⚡ AI Health Twin Active</span>
</div>
""", unsafe_allow_html=True)
        st.info("Navigate the pages above to explore all wellness modules.")
        st.write("")
        if st.button("🚪 Logout"):
            logout()
            st.rerun()

    # ── ECG + Hero title ─────────────────────────────────────────────────────
    st.markdown(ecg_banner(), unsafe_allow_html=True)
    st.markdown("""
<div class="hero-title">Your Digital Health Twin</div>
<p class="hero-sub">
  A living, AI-powered mirror of your physical, mental, and lifestyle wellness —
  updated in real time as you log new data.
</p>
""", unsafe_allow_html=True)
    st.write("")

    # ── Load data ─────────────────────────────────────────────────────────────
    profile  = get_profile(user["id"])
    moods    = get_moods(user["id"])
    journals = get_journals(user["id"])

    if not profile:
        st.warning("⚠️  Complete your **👤 Profile** page to activate your Digital Health Twin.")
        return

    # ── Scores ───────────────────────────────────────────────────────────────
    phys    = physical_score(profile)
    life    = lifestyle_score(profile)
    ment    = mental_score(moods, journals)
    overall = overall_score(phys, ment, life)
    label, color = status_label(overall)

    # ── Welcome banner (hologram image bg) ───────────────────────────────────
    st.markdown(f"""
<div class="welcome-band">
  <h2>Welcome back, {user['username']} 👋</h2>
  <p>
    Your AI Health Twin is active. Here's a live snapshot of your wellness index.
    Keep your profile updated for more accurate predictions and personalised insights.
  </p>
</div>
""", unsafe_allow_html=True)

    # ── KPI Row ───────────────────────────────────────────────────────────────
    st.markdown(section_label("Wellness Scores"), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Overall Score", overall,
            "linear-gradient(90deg,#1a6ef5,#0fc4a7)", "#1a6ef5", "+2 this week"),
            unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Physical", phys,
            "linear-gradient(90deg,#f5591a,#f5a31a)", "#f5591a"),
            unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Mental", ment,
            "linear-gradient(90deg,#7c3aed,#1a6ef5)", "#7c3aed"),
            unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Lifestyle", life,
            "linear-gradient(90deg,#0fc4a7,#1af577)", "#0fc4a7"),
            unsafe_allow_html=True)

    st.write("")

    # ── Gauge + Rings ─────────────────────────────────────────────────────────
    st.markdown(section_label("Index Breakdown"), unsafe_allow_html=True)
    gcol, rcol = st.columns([1.15, 0.85])

    with gcol:
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(gauge(overall, "Overall Wellness Index"),
                        use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with rcol:
        st.markdown(section_label("Domain Rings"), unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(progress_ring(phys, "Physical", "#f5591a"),
                        unsafe_allow_html=True)
        with r2:
            st.markdown(progress_ring(ment, "Mental",   "#7c3aed"),
                        unsafe_allow_html=True)
        with r3:
            st.markdown(progress_ring(life, "Lifestyle","#0fc4a7"),
                        unsafe_allow_html=True)

    # ── AI Insight — uses ai_handshake image as background ────────────────────
    if overall >= 80:
        ic = "#0fc4a7"
        msg = ("🌟 You're thriving! Excellent scores across all domains — "
               "maintain your routines and explore the What-If Simulator.")
    elif overall >= 60:
        ic = "#f5a31a"
        msg = ("You're on solid ground. Small, consistent improvements in your "
               "lower-scoring domains will compound quickly. Check Recommendations.")
    else:
        ic = "#f5591a"
        msg = ("Your wellness index needs attention. Visit the Recommendations "
               "&amp; What-If Simulator to build a personalised recovery plan.")

    badge = status_badge(label, ic)

    st.markdown(f"""
<div class="ai-glass" style="border-color:{ic}33;">
  <div class="ai-glass-inner">
    <h4 style="color:{ic};">🤖 AI Insight &nbsp; {badge}</h4>
    <p style="margin-top:8px;">
      Your overall wellness index is
      <strong style="color:{ic};">{overall}/100</strong>. {msg}
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Quick Actions ─────────────────────────────────────────────────────────
    st.write("")
    st.markdown(section_label("Quick Actions"), unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)

    actions = [
        ("💪", "Log Workout",   "Track a new physical activity session."),
        ("😌", "Log Mood",      "Record how you're feeling right now."),
        ("📝", "Write Journal", "Reflect on your day with a quick note."),
        ("🔮", "What-If Sim",   "Simulate score changes before committing."),
    ]
    for col, (icon, title, desc) in zip([q1, q2, q3, q4], actions):
        with col:
            st.markdown(qa_card(icon, title, desc), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────
inject_theme()

if st.session_state.authenticated:
    home_dashboard()
else:
    auth_screen()