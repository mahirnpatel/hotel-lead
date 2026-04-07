import streamlit as st
import asyncio
import sys
import os

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

st.set_page_config(
    page_title="LeadPulse — Enrichment",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #080C14; color: #E2E8F0; }
.main .block-container { padding: 2rem 3rem 4rem; max-width: 1280px; }
.lp-logo { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 2rem; color: #FFFFFF; letter-spacing: -0.04em; }
.lp-logo span { color: #3B82F6; }
.lp-tagline { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #475569; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 2.5rem; }
.lp-divider { height: 1px; background: linear-gradient(90deg, #3B82F6 0%, #1E3A5F 40%, transparent 100%); margin: 1.5rem 0 2.5rem; }
.section-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: #3B82F6; margin-bottom: 0.6rem; }

.stButton > button {
    background: #3B82F6 !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.9rem !important;
    letter-spacing: 0.05em !important; padding: 0.65rem 2rem !important; transition: all 0.2s ease !important; width: 100% !important;
}
.stButton > button:hover { background: #2563EB !important; box-shadow: 0 0 20px rgba(59,130,246,0.35) !important; transform: translateY(-1px) !important; }
.stButton > button:disabled { background: #1E2D45 !important; color: #475569 !important; }

.infobanner { background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.25); border-radius: 8px; padding: 0.75rem 1rem; color: #60A5FA; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }
.successbanner { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); border-radius: 8px; padding: 0.75rem 1rem; color: #34D399; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }

.score-badge { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 0.75rem; font-weight: 500; }
.score-high   { background: rgba(16,185,129,0.15); color: #34D399; border: 1px solid rgba(16,185,129,0.25); }
.score-medium { background: rgba(59,130,246,0.15); color: #60A5FA; border: 1px solid rgba(59,130,246,0.25); }
.score-low    { background: rgba(71,85,105,0.2);   color: #94A3B8; border: 1px solid rgba(71,85,105,0.3); }
.category-tag { display: inline-block; padding: 0.15rem 0.5rem; background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.18); border-radius: 4px; font-size: 0.72rem; color: #93C5FD; font-family: 'DM Mono', monospace; }

.card-section-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: #3B82F6; margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #1E2D45; }
[data-testid="stExpander"] { background: #0D1520 !important; border: 1px solid #1E2D45 !important; border-radius: 10px !important; margin-bottom: 0.75rem !important; }
[data-testid="stExpander"] summary { padding: 1rem 1.25rem !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; color: #E2E8F0 !important; }
[data-testid="stExpander"]:hover { border-color: #3B82F6 !important; }

.detail-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.25rem; }
.detail-item label { display: block; font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: #475569; margin-bottom: 0.3rem; }
.detail-item p { margin: 0; font-size: 0.88rem; color: #CBD5E1; }
.rationale-block { background: #080C14; border-left: 3px solid #3B82F6; border-radius: 0 6px 6px 0; padding: 0.75rem 1rem; font-size: 0.83rem; color: #94A3B8; line-height: 1.6; margin-top: 0.75rem; }
[data-testid="stSpinner"] { color: #3B82F6 !important; }
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="lp-logo">Lead<span>Pulse</span></div>
<div class="lp-tagline">⚡ Step 2 of 3 &nbsp;·&nbsp; Enrichment</div>
<div class="lp-divider"></div>
""", unsafe_allow_html=True)

# ── Guard: must have Agent 1 data ──────────────────────────────────────────────
if "agent1_report" not in st.session_state or "selected_event_ids" not in st.session_state:
    st.warning("No events found yet. Please complete Step 1 first.")
    if st.button("← Back to Event Discovery"):
        st.switch_page("pages/1_Event_Discovery.py")
    st.stop()

report           = st.session_state["agent1_report"]
selected_ids     = st.session_state["selected_event_ids"]
selected_events  = [ev for ev in report.events if ev.id in selected_ids]

if not selected_events:
    st.warning("No events selected. Go back and select at least one event.")
    if st.button("← Back to Event Discovery"):
        st.switch_page("pages/1_Event_Discovery.py")
    st.stop()

# ── Back button ────────────────────────────────────────────────────────────────
if st.button("← Back to Event Discovery", key="back_to_discovery"):
    st.switch_page("pages/1_Event_Discovery.py")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
st.markdown(f'<div class="infobanner">⚡ {len(selected_events)} event(s) selected for enrichment</div>', unsafe_allow_html=True)

# ── Run Enrichment ─────────────────────────────────────────────────────────────
run_enrichment_btn = st.button(
    f"Run Enrichment on {len(selected_events)} Event(s)",
    key="run_enrichment",
    disabled="enrichment_report" in st.session_state,
)

if run_enrichment_btn:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from core.enrichment_agent import run_enrichment_agent
    st.session_state.pop("generated_emails", None)

    filtered_report = report.__class__(
        city=report.city,
        state=report.state,
        generated_at=report.generated_at,
        total_found=report.total_found,
        filtered_out=report.filtered_out,
        events=selected_events,
    )
    with st.spinner(f"Enriching {len(selected_events)} event(s)…"):
        try:
            enrichment_report = run_async(run_enrichment_agent(filtered_report))
            st.session_state["enrichment_report"] = enrichment_report
        except Exception as e:
            st.error(f"Enrichment failed: {e}")
            st.stop()

# ── Enrichment Results ─────────────────────────────────────────────────────────
if "enrichment_report" in st.session_state:
    enrichment_report = st.session_state["enrichment_report"]

    st.markdown('<div class="card-section-label">Enrichment Results</div>', unsafe_allow_html=True)

    for e in enrichment_report.enriched_events:
        score_cls = "score-high" if e.hotel_lead_score >= 8 else "score-medium"
        elabel = f"{'🟢' if e.hotel_lead_score >= 8 else '🔵'} {e.event_name}  ·  Score {e.hotel_lead_score}/10  ·  Confidence: {e.confidence}"
        with st.expander(elabel, expanded=True):
            st.markdown(f'<div class="rationale-block">💡 {e.hotel_lead_reasoning}</div>', unsafe_allow_html=True)

            if e.attending_organizations:
                orgs = "".join([f'<span class="category-tag" style="margin:0.2rem">{o}</span>' for o in e.attending_organizations])
                st.markdown(f'<div style="margin-top:1rem"><div class="section-label" style="margin-bottom:0.5rem">Attending Organizations</div><div style="display:flex;flex-wrap:wrap;gap:0.3rem">{orgs}</div></div>', unsafe_allow_html=True)

            if e.target_contacts.job_titles:
                titles = "".join([f'<span class="category-tag" style="margin:0.2rem;border-color:rgba(16,185,129,0.25);color:#34D399;background:rgba(16,185,129,0.08)">{t}</span>' for t in e.target_contacts.job_titles])
                st.markdown(f'<div style="margin-top:1rem"><div class="section-label" style="margin-bottom:0.5rem">Target Contact Titles</div><div style="display:flex;flex-wrap:wrap;gap:0.3rem">{titles}</div></div>', unsafe_allow_html=True)

            if e.stakeholders:
                items = "".join([f'<div class="detail-item"><label>{s.type}</label><p>{s.name} — {s.role}</p></div>' for s in e.stakeholders])
                st.markdown(f'<div style="margin-top:1rem"><div class="section-label" style="margin-bottom:0.5rem">Key Stakeholders</div><div class="detail-grid">{items}</div></div>', unsafe_allow_html=True)

            if e.event_website:
                st.markdown(f'<div class="detail-item" style="margin-top:1rem"><label>Event Website</label><p><a href="{e.event_website}" target="_blank" style="color:#60A5FA">{e.event_website}</a></p></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="successbanner">✅ Enrichment complete — proceed to Contact Discovery & Outreach.</div>', unsafe_allow_html=True)

    if st.button("Next → Contacts & Outreach", key="go_outreach"):
        st.switch_page("pages/3_Contacts_Outreach.py")
