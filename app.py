import streamlit as st
import streamlit_authenticator as stauth
import json

st.set_page_config(
    page_title="LeadPulse — Login",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #080C14; color: #E2E8F0; }
.main .block-container { padding: 4rem 2rem; max-width: 420px; margin: 0 auto; }
.lp-logo { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 2rem; color: #FFFFFF; letter-spacing: -0.04em; text-align: center; margin-bottom: 0.25rem; }
.lp-logo span { color: #3B82F6; }
.lp-tagline { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #475569; letter-spacing: 0.12em; text-transform: uppercase; text-align: center; margin-bottom: 2.5rem; }
.lp-divider { height: 1px; background: linear-gradient(90deg, transparent 0%, #3B82F6 50%, transparent 100%); margin: 1.5rem 0 2rem; }
[data-testid="stSidebarNav"] { display: none; }

[data-testid="stTextInput"] input {
    background: #111927 !important; border: 1px solid #1E2D45 !important; border-radius: 8px !important;
    color: #E2E8F0 !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus { border-color: #3B82F6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important; }
[data-testid="stTextInput"] label { color: #94A3B8 !important; font-size: 0.78rem !important; font-family: 'DM Mono', monospace !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }

.stButton > button {
    background: #3B82F6 !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.9rem !important;
    letter-spacing: 0.05em !important; padding: 0.65rem 2rem !important; width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { background: #2563EB !important; box-shadow: 0 0 20px rgba(59,130,246,0.35) !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="lp-logo">Lead<span>Pulse</span></div>
<div class="lp-tagline">⚡ Hotel Lead Generation & Outreach</div>
<div class="lp-divider"></div>
""", unsafe_allow_html=True)


credentials = json.loads(json.dumps({
    "usernames": {
        username: dict(user_data)
        for username, user_data in st.secrets["credentials"]["usernames"].items()
    }
}))
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name=st.secrets["cookie"]["name"],
    cookie_key=st.secrets["cookie"]["key"],
    cookie_expiry_days=st.secrets["cookie"]["expiry_days"],
)

authenticator.login(location="main")

if st.session_state.get("authentication_status") is True:
    st.switch_page("pages/1_Event_Discovery.py")

elif st.session_state.get("authentication_status") is False:
    st.error("Incorrect username or password.")

elif st.session_state.get("authentication_status") is None:
    st.markdown('<div style="text-align:center;font-family:DM Mono,monospace;font-size:0.72rem;color:#475569;margin-top:1.5rem">Enter your credentials to access LeadPulse</div>', unsafe_allow_html=True)