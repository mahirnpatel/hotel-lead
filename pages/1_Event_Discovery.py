import streamlit as st
import asyncio
import sys
import os
from datetime import date, timedelta

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
    page_title="LeadPulse — Event Discovery",
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

[data-testid="stTextInput"] input, [data-testid="stDateInput"] input {
    background: #111927 !important; border: 1px solid #1E2D45 !important; border-radius: 8px !important;
    color: #E2E8F0 !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; padding: 0.6rem 0.9rem !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stDateInput"] input:focus { border-color: #3B82F6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important; }
[data-testid="stTextInput"] label, [data-testid="stDateInput"] label { color: #94A3B8 !important; font-size: 0.78rem !important; font-family: 'DM Mono', monospace !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }

.stButton > button {
    background: #3B82F6 !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.9rem !important;
    letter-spacing: 0.05em !important; padding: 0.65rem 2rem !important; transition: all 0.2s ease !important; width: 100% !important;
}
.stButton > button:hover { background: #2563EB !important; box-shadow: 0 0 20px rgba(59,130,246,0.35) !important; transform: translateY(-1px) !important; }
.stButton > button:disabled { background: #1E2D45 !important; color: #475569 !important; }

.infobanner { background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.25); border-radius: 8px; padding: 0.75rem 1rem; color: #60A5FA; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }
.successbanner { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); border-radius: 8px; padding: 0.75rem 1rem; color: #34D399; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }

.results-count { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 700; color: #FFFFFF; }
.results-count span { color: #3B82F6; }

.event-table { width: 100%; border-collapse: collapse; margin-bottom: 2.5rem; font-size: 0.85rem; }
.event-table thead tr { border-bottom: 1px solid #1E2D45; }
.event-table th { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase; color: #475569; padding: 0.6rem 0.75rem; text-align: left; font-weight: 400; }
.event-table td { padding: 0.85rem 0.75rem; border-bottom: 1px solid #111927; vertical-align: middle; color: #CBD5E1; }
.event-table tbody tr:hover td { background: #0D1520; }
.event-name-cell { font-weight: 500; color: #E2E8F0; max-width: 280px; }

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

/* Hide default Streamlit multipage nav */
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="lp-logo">Lead<span>Pulse</span></div>
<div class="lp-tagline">⚡ Step 1 of 3 &nbsp;·&nbsp; Event Discovery</div>
<div class="lp-divider"></div>
""", unsafe_allow_html=True)

def score_badge(score):
    cls = "score-high" if score >= 8 else "score-medium" if score >= 6 else "score-low"
    return f'<span class="score-badge {cls}">{score}/10</span>'

def fmt_attendance(val):
    if val is None: return "—"
    return f"{val:,}" if isinstance(val, int) else str(val)

# ── Input panel ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Search Parameters</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1.5])
with col1:
    city = st.text_input("City", placeholder="e.g. Dallas", key="city")
with col2:
    state = st.text_input("State", placeholder="e.g. TX", key="state")
with col3:
    start_date = st.date_input("Start Date", value=date.today(), key="start_date")
with col4:
    end_date = st.date_input("End Date", value=date.today() + timedelta(days=90), key="end_date")
with col5:
    st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("Run Agent 1", key="run_agent1")

if run_btn:
    if not city or not state:
        st.error("Please enter both a city and state.")
        st.stop()
    if start_date >= end_date:
        st.error("End date must be after start date.")
        st.stop()

    for key in ["agent1_report", "enrichment_report", "generated_emails", "selected_event_ids"]:
        st.session_state.pop(key, None)

    with st.spinner("Agent 1 scanning PredictHQ for events…"):
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            import config.settings as app_settings
            app_settings.START_DATE = start_date.isoformat()
            app_settings.END_DATE   = end_date.isoformat()

            from core.research_agent import research_agent
            from agents import Runner, trace

            async def _run():
                prompt = (
                    f"Find upcoming business events in {city.strip()}, {state.strip()} "
                    f"between {start_date.isoformat()} and {end_date.isoformat()}."
                )
                with trace("Research Agent — Event Discovery"):
                    result = await Runner.run(research_agent, input=prompt)
                return result.final_output

            report = run_async(_run())
            st.session_state["agent1_report"]  = report
            st.session_state["agent1_city"]    = city
            st.session_state["agent1_state"]   = state
        except Exception as e:
            st.error(f"Agent 1 failed: {e}")
            st.stop()

# ── Results ────────────────────────────────────────────────────────────────────
if "agent1_report" in st.session_state:
    report      = st.session_state["agent1_report"]
    events      = report.events
    city_label  = st.session_state["agent1_city"]
    state_label = st.session_state["agent1_state"]

    if not events:
        st.warning("No qualifying events found. Try a wider date range or different city.")
        st.stop()

    st.markdown(f'<div class="results-count"><span>{len(events)}</span> qualifying events · {city_label}, {state_label}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Summary table
    st.markdown('<div class="section-label">Event Overview</div>', unsafe_allow_html=True)
    rows = ""
    for ev in events:
        rows += (
            f'<tr><td class="event-name-cell">{ev.title}</td>'
            f'<td>{ev.start or "—"}</td>'
            f'<td>{score_badge(ev.relevance_score)}</td>'
            f'<td><span class="category-tag">{ev.category or "—"}</span></td>'
            f'<td>{fmt_attendance(ev.phq_attendance)}</td></tr>'
        )
    st.markdown(
        '<table class="event-table"><thead><tr>'
        '<th>Event Name</th><th>Date</th><th>Score</th><th>Category</th><th>Expected Attendance</th>'
        f'</tr></thead><tbody>{rows}</tbody></table>',
        unsafe_allow_html=True,
    )

    # Detail cards + checkboxes
    st.markdown('<div class="card-section-label">Select Events for Enrichment</div>', unsafe_allow_html=True)
    st.markdown('<div class="infobanner">Expand each event and check the box to select it, then proceed to Step 2.</div>', unsafe_allow_html=True)

    selected_ids = set()
    for ev in events:
        score = ev.relevance_score
        label = f"{'🟢' if score >= 8 else '🔵'} {ev.title}  ·  Score {score}/10  ·  {ev.start or '—'}"
        with st.expander(label):
            selected = st.checkbox(
                "Select for enrichment",
                key=f"select_{ev.id}",
                value=ev.id in st.session_state.get("selected_event_ids", set()),
            )
            if selected:
                selected_ids.add(ev.id)

            acc = ev.accommodation_spend
            dur = ev.duration_days
            att = fmt_attendance(ev.phq_attendance)
            st.markdown(
                '<div class="detail-grid">'
                f'<div class="detail-item"><label>Category</label><p>{ev.category or "—"}</p></div>'
                f'<div class="detail-item"><label>Start Date</label><p>{ev.start or "—"}</p></div>'
                f'<div class="detail-item"><label>End Date</label><p>{ev.end or "—"}</p></div>'
                f'<div class="detail-item"><label>Venue</label><p>{ev.venue_name or ev.venue_address or "—"}</p></div>'
                f'<div class="detail-item"><label>Attendance</label><p>{att if att != "—" else (ev.estimated_attendees or "—")}</p></div>'
                f'<div class="detail-item"><label>Duration</label><p>{f"{dur} days" if dur else "—"}</p></div>'
                f'<div class="detail-item"><label>Score</label><p>{score}/10</p></div>'
                f'<div class="detail-item"><label>Rank (Global)</label><p>{ev.rank}</p></div>'
                f'<div class="detail-item"><label>Accom. Spend</label><p>{"${:,}".format(acc) if acc else "—"}</p></div>'
                '</div>',
                unsafe_allow_html=True,
            )
            if ev.relevance_reason:
                st.markdown(f'<div class="rationale-block">💡 {ev.relevance_reason}</div>', unsafe_allow_html=True)
            if ev.phq_labels:
                tags = "".join([f'<span class="category-tag" style="margin:0.2rem">{l}</span>' for l in ev.phq_labels])
                st.markdown(f'<div style="margin-top:1rem"><div class="section-label" style="margin-bottom:0.5rem">Industry Tags</div><div style="display:flex;flex-wrap:wrap;gap:0.3rem">{tags}</div></div>', unsafe_allow_html=True)
            if ev.target_companies:
                co_tags = "".join([f'<span class="category-tag" style="margin:0.2rem;border-color:rgba(16,185,129,0.25);color:#34D399;background:rgba(16,185,129,0.08)">{c}</span>' for c in ev.target_companies])
                st.markdown(f'<div style="margin-top:1rem"><div class="section-label" style="margin-bottom:0.5rem">Target Company Types</div><div style="display:flex;flex-wrap:wrap;gap:0.3rem">{co_tags}</div></div>', unsafe_allow_html=True)

    st.session_state["selected_event_ids"] = selected_ids
    selected_count = len(selected_ids)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)

    if selected_count > 0:
        st.markdown(f'<div class="successbanner">✅ {selected_count} event(s) selected — proceed to Enrichment.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="infobanner">Select at least one event above to proceed to Enrichment.</div>', unsafe_allow_html=True)

    if st.button("Next → Enrichment", disabled=selected_count == 0, key="go_enrichment"):
        st.switch_page("pages/2_Enrichment.py")
