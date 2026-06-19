"""
utils/styles.py
Dark glassmorphism theme, neon gradients, particle background,
animated counters, KPI cards, progress rings.
"""
import streamlit as st


def inject_theme():
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Orbitron:wght@500;700;900&display=swap');

    .stApp {
        background: radial-gradient(1200px 800px at 10% 0%, #14193a 0%, #0a0e1a 45%, #06080f 100%);
        color: #e8ecff;
        font-family: 'Inter', sans-serif;
    }

    /* Floating particle background */
    .particles {position: fixed; inset: 0; z-index: -1; overflow: hidden;}
    .particle {
        position: absolute; border-radius: 50%;
        background: radial-gradient(circle, rgba(123,92,255,.9), rgba(0,229,255,.1));
        filter: blur(1px); animation: float 14s infinite ease-in-out;
    }
    @keyframes float {
        0%,100% {transform: translateY(0) translateX(0); opacity:.5;}
        50% {transform: translateY(-120px) translateX(40px); opacity:1;}
    }

    /* Glass cards */
    .glass {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(123,92,255,0.25);
        border-radius: 22px;
        padding: 22px 26px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.45), inset 0 0 30px rgba(123,92,255,0.05);
        transition: transform .35s ease, box-shadow .35s ease, border .35s ease;
    }
    .glass:hover {
        transform: translateY(-6px) scale(1.01);
        border: 1px solid rgba(0,229,255,0.6);
        box-shadow: 0 16px 60px rgba(0,229,255,0.25);
    }

    .kpi-value {
        font-family: 'Orbitron', sans-serif; font-size: 2.6rem; font-weight: 900;
        background: linear-gradient(90deg,#00e5ff,#7b5cff,#ff5cf0);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: glow 3s ease-in-out infinite;
    }
    @keyframes glow {0%,100%{filter:drop-shadow(0 0 4px #7b5cff);}50%{filter:drop-shadow(0 0 18px #00e5ff);}}
    .kpi-label {font-size:.85rem; letter-spacing:2px; text-transform:uppercase; color:#9fb0e0;}

    .hero-title {
        font-family:'Orbitron',sans-serif; font-size:3rem; font-weight:900;
        background: linear-gradient(90deg,#00e5ff,#7b5cff 50%,#ff5cf0);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .hero-sub {color:#9fb0e0; font-size:1.1rem; max-width:680px;}

    /* Gradient buttons */
    .stButton>button {
        background: linear-gradient(90deg,#7b5cff,#00e5ff);
        color:#04060f; font-weight:700; border:none; border-radius:14px;
        padding:.6rem 1.4rem; transition:.3s; box-shadow:0 0 18px rgba(123,92,255,.5);
    }
    .stButton>button:hover {transform:translateY(-2px); box-shadow:0 0 30px rgba(0,229,255,.7);}

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(18,24,49,.95), rgba(8,11,22,.95));
        border-right:1px solid rgba(123,92,255,.2);
    }

    /* Skeleton loader */
    .skeleton {height:120px;border-radius:18px;
        background:linear-gradient(90deg,#11162e 25%,#1b2350 50%,#11162e 75%);
        background-size:200% 100%; animation:shimmer 1.4s infinite;}
    @keyframes shimmer {0%{background-position:200% 0;}100%{background-position:-200% 0;}}

    .pill {display:inline-block;padding:4px 14px;border-radius:30px;font-size:.78rem;
        border:1px solid rgba(0,229,255,.4);background:rgba(0,229,255,.08);color:#aef;}
    </style>

    <div class="particles">
    """ + "".join(
            f'<div class="particle" style="width:{6+i*2}px;height:{6+i*2}px;'
            f'left:{(i*7)%100}%;top:{(i*11)%100}%;animation-delay:{i*0.6}s;"></div>'
            for i in range(18)
        ) + "</div>",
        unsafe_allow_html=True,
    )


def kpi_card(label, value, suffix=""):
    return f"""
    <div class="glass" style="text-align:center;">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}{suffix}</div>
    </div>"""


def progress_ring(score, label):
    """SVG animated progress ring (0-100)."""
    score = max(0, min(100, score))
    circ = 2 * 3.14159 * 52
    offset = circ * (1 - score / 100)
    color = "#00e5ff" if score >= 70 else "#ffb627" if score >= 45 else "#ff4d6d"
    return f"""
    <div class="glass" style="text-align:center;">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="52" stroke="#1b2350" stroke-width="12" fill="none"/>
        <circle cx="70" cy="70" r="52" stroke="{color}" stroke-width="12" fill="none"
          stroke-linecap="round" stroke-dasharray="{circ}" stroke-dashoffset="{offset}"
          transform="rotate(-90 70 70)" style="transition:stroke-dashoffset 1.4s ease;">
          <animate attributeName="stroke-dashoffset" from="{circ}" to="{offset}" dur="1.4s" fill="freeze"/>
        </circle>
        <text x="70" y="78" text-anchor="middle" font-size="30" fill="{color}"
          font-family="Orbitron" font-weight="700">{int(score)}</text>
      </svg>
      <div class="kpi-label">{label}</div>
    </div>"""