import streamlit as st
import asyncio
import sys
import os
from datetime import date, timedelta
from streamlit_searchbox import st_searchbox
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

def score_badge(score):
    cls = "score-high" if score >= 8 else "score-medium" if score >= 6 else "score-low"
    return f'<span class="score-badge {cls}">{score}/10</span>'

def fmt_attendance(val):
    if val is None: return "—"
    return f"{val:,}" if isinstance(val, int) else str(val)

US_CITIES = [
    "Atlanta", "Austin", "Baltimore", "Boston", "Charlotte", "Chicago",
    "Cincinnati", "Cleveland", "Columbus", "Dallas", "Denver", "Detroit",
    "El Paso", "Fort Worth", "Houston", "Indianapolis", "Jacksonville",
    "Kansas City", "Las Vegas", "Los Angeles", "Louisville", "Memphis",
    "Miami", "Milwaukee", "Minneapolis", "Nashville", "New Orleans",
    "New York", "Oklahoma City", "Orlando", "Philadelphia", "Phoenix",
    "Pittsburgh", "Portland", "Raleigh", "Sacramento", "Salt Lake City",
    "San Antonio", "San Diego", "San Francisco", "San Jose", "Seattle",
    "St. Louis", "Tampa", "Tucson", "Tulsa", "Virginia Beach",
    "Washington DC", "Birmingham", "Richmond",
]

US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]

def search_cities(query: str):
    if not query:
        return []
    q = query.lower()
    return [c for c in US_CITIES if q in c.lower()]

def search_states(query: str):
    if not query:
        return []
    q = query.lower()
    return [s for s in US_STATES if q in s.lower()]
st.set_page_config(
    page_title="LeadPulse — Event Discovery",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Auth Guard ─────────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.switch_page("app.py")

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

.score-badge { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 6px; font-family: 'DM Mono', monospace; font-size: 0.75rem; font-weight: 500; }
.score-high   { background: rgba(16,185,129,0.15); color: #34D399; border: 1px solid rgba(16,185,129,0.25); }
.score-medium { background: rgba(59,130,246,0.15); color: #60A5FA; border: 1px solid rgba(59,130,246,0.25); }
.score-low    { background: rgba(71,85,105,0.2);   color: #94A3B8; border: 1px solid rgba(71,85,105,0.3); }
.category-tag { display: inline-block; padding: 0.15rem 0.5rem; background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.18); border-radius: 4px; font-size: 0.72rem; color: #93C5FD; font-family: 'DM Mono', monospace; }
.queued-tag { display: inline-block; padding: 0.2rem 0.6rem; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 4px; font-size: 0.72rem; color: #34D399; font-family: 'DM Mono', monospace; }

.detail-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1rem; }
.detail-item label { display: block; font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: #475569; margin-bottom: 0.3rem; }
.detail-item p { margin: 0; font-size: 0.85rem; color: #CBD5E1; }
.rationale-block { background: #080C14; border-left: 3px solid #3B82F6; border-radius: 0 6px 6px 0; padding: 0.75rem 1rem; font-size: 0.83rem; color: #94A3B8; line-height: 1.6; margin-bottom: 1rem; }

/* Expander styling — matches row context */
[data-testid="stExpander"] { background: #0A1628 !important; border: 1px solid #1E2D45 !important; border-radius: 8px !important; margin-bottom: 0.35rem !important; }
[data-testid="stExpander"] summary { padding: 0 !important; }
[data-testid="stExpander"]:hover { border-color: #2D4A6B !important; }

.queue-btn button {
    background: transparent !important; border: 1px solid rgba(59,130,246,0.4) !important; color: #60A5FA !important;
    font-size: 0.50rem !important; padding: 0.18rem 0.20rem !important; width: auto !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 0.06em !important; border-radius: 6px !important; font-weight: 500 !important;
}
.queue-btn button:hover { background: rgba(59,130,246,0.1) !important; border-color: #3B82F6 !important; color: #93C5FD !important; box-shadow: none !important; transform: none !important; }

.queued-btn button {
    background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.35) !important; color: #34D399 !important;
    font-size: 0.50rem !important; padding: 0.18rem 0.20rem !important; width: auto !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 0.06em !important; border-radius: 6px !important; font-weight: 500 !important;
}
.queued-btn button:hover { background: rgba(239,68,68,0.08) !important; border-color: rgba(239,68,68,0.4) !important; color: #F87171 !important; box-shadow: none !important; transform: none !important; }

.logout-btn button {
    background: transparent !important; border: 1px solid #1E2D45 !important; color: #475569 !important;
    font-size: 0.75rem !important; padding: 0.35rem 0.9rem !important; width: auto !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 0.08em !important;
}
.logout-btn button:hover { border-color: #3B82F6 !important; color: #60A5FA !important; box-shadow: none !important; transform: none !important; }

.startover-btn button {
    background: transparent !important; border: 1px solid rgba(239,68,68,0.3) !important; color: #F87171 !important;
    font-size: 0.75rem !important; padding: 0.35rem 0.9rem !important; width: auto !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 0.08em !important;
}
.startover-btn button:hover { border-color: #EF4444 !important; color: #EF4444 !important; box-shadow: none !important; transform: none !important; }

[data-testid="stSpinner"] { color: #3B82F6 !important; }
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Start Over Dialog ──────────────────────────────────────────────────────────
@st.dialog("Start Over?")
def confirm_startover_dialog():
    st.markdown(
        '<p style="font-family:DM Sans,sans-serif;color:#94A3B8;font-size:0.9rem;margin-bottom:1.5rem">'
        'This will clear all events, enrichment data, and generated emails. Are you sure?'
        '</p>', unsafe_allow_html=True,
    )
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Yes, Start Over", key="confirm_yes"):
            keys_to_clear = ["agent1_report", "enrichment_report", "generated_emails",
                              "selected_event_ids", "agent1_city", "agent1_state",
                              "confirm_startover", "queued_event_ids"]
            for k in keys_to_clear:
                st.session_state.pop(k, None)
            st.switch_page("pages/1_Event_Discovery.py")
    with col_no:
        if st.button("Cancel", key="confirm_no"):
            st.session_state["confirm_startover"] = False
            st.rerun()

if st.session_state.get("confirm_startover"):
    confirm_startover_dialog()

# ── Header ─────────────────────────────────────────────────────────────────────
col_header, col_buttons = st.columns([7, 3])
with col_header:
    st.markdown("""
    <div class="lp-logo">Lead<span>Pulse</span></div>
    <div class="lp-tagline">Step 1 of 3 &nbsp;·&nbsp; Event Discovery</div>
    """, unsafe_allow_html=True)
with col_buttons:
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    if st.session_state.get("agent1_report") is not None:
        btn_cols = st.columns([1, 1])
        with btn_cols[0]:
            st.markdown('<div class="startover-btn">', unsafe_allow_html=True)
            if st.button("Start Over", key="startover_btn"):
                st.session_state["confirm_startover"] = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with btn_cols[1]:
            st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
            if st.button("Logout", key="logout_btn"):
                st.session_state["authentication_status"] = None
                st.session_state["name"] = None
                st.session_state["username"] = None
                st.switch_page("app.py")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        btn_cols = st.columns([1])
        with btn_cols[0]:
            st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
            if st.button("Logout", key="logout_btn"):
                st.session_state["authentication_status"] = None
                st.session_state["name"] = None
                st.session_state["username"] = None
                st.switch_page("app.py")
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)

# ── Search Input ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Search Parameters</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1.5])
with col1:
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:0.78rem;color:#94A3B8;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.3rem">City</div>', unsafe_allow_html=True)
    city = st_searchbox(search_cities, placeholder="e.g. Dallas", key="city_search")
with col2:
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:0.78rem;color:#94A3B8;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.3rem">State</div>', unsafe_allow_html=True)
    state = st_searchbox(search_states, placeholder="e.g. Texas", key="state_search")
with col3:
    start_date = st.date_input("Start Date", value=date.today(), key="start_date")
with col4:
    end_date = st.date_input("End Date", value=date.today() + timedelta(days=90), key="end_date")
with col5:
    st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("Discover Events", key="run_agent1")

if run_btn:
    if not city or not state:
        st.error("Please enter both a city and state.")
        st.stop()
    if start_date >= end_date:
        st.error("End date must be after start date.")
        st.stop()

    for key in ["agent1_report", "enrichment_report", "generated_emails",
                "selected_event_ids", "queued_event_ids"]:
        st.session_state.pop(key, None)

    with st.spinner(f"Discovering events in {city.strip()}, {state.strip()}…"):
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
            st.session_state["agent1_report"]    = report
            st.session_state["agent1_city"]      = city
            st.session_state["agent1_state"]     = state
            st.session_state["queued_event_ids"] = set()
        except Exception as e:
            st.error(f"Agent 1 failed: {e}")
            st.stop()

# ── Events Table ───────────────────────────────────────────────────────────────
if "agent1_report" in st.session_state:
    report      = st.session_state["agent1_report"]
    events      = report.events
    city_label  = st.session_state["agent1_city"]
    state_label = st.session_state["agent1_state"]

    if not events:
        st.warning("No qualifying events found. Try a wider date range or different city.")
        st.stop()

    if "queued_event_ids" not in st.session_state:
        st.session_state["queued_event_ids"] = set()

    queued_ids = st.session_state["queued_event_ids"]

    st.markdown(f'<div class="results-count"><span>{len(events)}</span> qualifying events · {city_label}, {state_label}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Events — Queue for Enrichment</div>', unsafe_allow_html=True)
    st.markdown('<div class="infobanner">Click <strong>+ Queue</strong> to add an event. Expand any row to see full details. Hit <strong>Run Enrichment</strong> when ready.</div>', unsafe_allow_html=True)


    # ── Rows with expandable details ───────────────────────────────────────────
    for i, ev in enumerate(events):
        is_queued = ev.id in queued_ids
        border_color = "rgba(16,185,129,0.25)" if is_queued else "#1E2D45"
        bg_color     = "rgba(16,185,129,0.03)" if is_queued else "#0A1628"

        expander_label = f"{'✅ ' if is_queued else ''}{ev.title}"

        with st.expander(expander_label, expanded=False):
            # ── Row summary inside expander header area ────────────────────────
            row_cols = st.columns([3.5, 1.5, 1.1, 1.3, 1.5, 1.2])
            with row_cols[0]:
                st.markdown(
                    f'<div style="font-size:0.875rem;color:#E2E8F0;font-weight:600;padding:0.4rem 0">{ev.title}</div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                st.markdown(
                    f'<div style="font-size:0.83rem;color:#94A3B8;font-family:DM Mono,monospace;padding:0.4rem 0">{ev.start or "—"}</div>',
                    unsafe_allow_html=True,
                )
            with row_cols[2]:
                st.markdown(
                    f'<div style="padding:0.3rem 0">{score_badge(ev.relevance_score)}</div>',
                    unsafe_allow_html=True,
                )
            with row_cols[3]:
                st.markdown(
                    f'<div style="padding:0.3rem 0"><span class="category-tag">{ev.category or "—"}</span></div>',
                    unsafe_allow_html=True,
                )
            with row_cols[4]:
                st.markdown(
                    f'<div style="font-size:0.83rem;color:#94A3B8;font-family:DM Mono,monospace;padding:0.4rem 0">{fmt_attendance(ev.phq_attendance)}</div>',
                    unsafe_allow_html=True,
                )
            with row_cols[5]:
                if is_queued:
                    st.markdown('<div class="queued-btn">', unsafe_allow_html=True)
                    if st.button("Select", key=f"queue_{i}_{ev.id}"):
                        queued_ids.discard(ev.id)
                        st.session_state["queued_event_ids"] = queued_ids
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="queue-btn">', unsafe_allow_html=True)
                    if st.button("Select", key=f"queue_{ev.id}"):
                        queued_ids.add(ev.id)
                        st.session_state["queued_event_ids"] = queued_ids
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # ── Detail panel ───────────────────────────────────────────────────
            st.markdown('<div style="height:0.75rem"></div>', unsafe_allow_html=True)
            st.markdown('<div style="height:1px;background:#1E2D45;margin-bottom:1rem"></div>', unsafe_allow_html=True)

            acc = ev.accommodation_spend
            dur = ev.duration_days
            att = fmt_attendance(ev.phq_attendance)

            st.markdown(
                '<div class="detail-grid">'
                f'<div class="detail-item"><label>Venue</label><p>{ev.venue_name or ev.venue_address or "—"}</p></div>'
                f'<div class="detail-item"><label>Start Date</label><p>{ev.start or "—"}</p></div>'
                f'<div class="detail-item"><label>End Date</label><p>{ev.end or "—"}</p></div>'
                f'<div class="detail-item"><label>Duration</label><p>{f"{dur} days" if dur else "—"}</p></div>'
                f'<div class="detail-item"><label>Attendance</label><p>{att if att != "—" else (ev.estimated_attendees or "—")}</p></div>'
                f'<div class="detail-item"><label>Global Rank</label><p>{ev.rank}</p></div>'
                f'<div class="detail-item"><label>Accom. Spend</label><p>{"${:,}".format(acc) if acc else "—"}</p></div>'
                f'<div class="detail-item"><label>Score</label><p>{ev.relevance_score}/10</p></div>'
                '</div>',
                unsafe_allow_html=True,
            )

            if ev.relevance_reason:
                st.markdown(f'<div class="rationale-block">💡 {ev.relevance_reason}</div>', unsafe_allow_html=True)

            if ev.phq_labels:
                tags = "".join([f'<span class="category-tag" style="margin:0.2rem">{l}</span>' for l in ev.phq_labels])
                st.markdown(
                    f'<div style="margin-bottom:0.75rem"><div class="section-label" style="margin-bottom:0.5rem">Industry Tags</div>'
                    f'<div style="display:flex;flex-wrap:wrap;gap:0.3rem">{tags}</div></div>',
                    unsafe_allow_html=True,
                )

            if ev.target_companies:
                co_tags = "".join([
                    f'<span class="category-tag" style="margin:0.2rem;border-color:rgba(16,185,129,0.25);color:#34D399;background:rgba(16,185,129,0.08)">{c}</span>'
                    for c in ev.target_companies
                ])
                st.markdown(
                    f'<div><div class="section-label" style="margin-bottom:0.5rem">Target Company Types</div>'
                    f'<div style="display:flex;flex-wrap:wrap;gap:0.3rem">{co_tags}</div></div>',
                    unsafe_allow_html=True,
                )

    # ── Queue summary + Run ────────────────────────────────────────────────────
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)

    queued_count = len(queued_ids)

    if queued_count > 0:
        queued_names = [ev.title for ev in events if ev.id in queued_ids]
        tags = "".join([f'<span class="queued-tag">{n}</span>' for n in queued_names])
        st.markdown(
            f'<div style="margin-bottom:1.25rem">'
            f'<div class="section-label" style="margin-bottom:0.6rem">Queued for Enrichment ({queued_count})</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:0.4rem">{tags}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="successbanner">✅ Ready — click below button to process all queued events.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="infobanner">No events queued yet — click <strong>+ Queue</strong> on any row above.</div>', unsafe_allow_html=True)

    if st.button(
        f"Enrich {queued_count} Event(s)" if queued_count > 0 else "Enrich Events",
        key="go_enrichment",
        disabled=queued_count == 0,
    ):
        st.session_state["selected_event_ids"] = queued_ids
        st.switch_page("pages/2_Enrichment.py")