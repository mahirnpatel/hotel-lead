import streamlit as st
import sys
import os

st.set_page_config(
    page_title="LeadPulse — Contacts & Outreach",
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

.stButton > button {
    background: #3B82F6 !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.9rem !important;
    letter-spacing: 0.05em !important; padding: 0.65rem 2rem !important; transition: all 0.2s ease !important; width: 100% !important;
}
.stButton > button:hover { background: #2563EB !important; box-shadow: 0 0 20px rgba(59,130,246,0.35) !important; transform: translateY(-1px) !important; }
.stButton > button:disabled { background: #1E2D45 !important; color: #475569 !important; }

.dfwwarning { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.3); border-radius: 8px; padding: 0.75rem 1rem; color: #FCD34D; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }
.infobanner { background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.25); border-radius: 8px; padding: 0.75rem 1rem; color: #60A5FA; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }
.successbanner { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); border-radius: 8px; padding: 0.75rem 1rem; color: #34D399; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }

.category-tag { display: inline-block; padding: 0.15rem 0.5rem; background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.18); border-radius: 4px; font-size: 0.72rem; color: #93C5FD; font-family: 'DM Mono', monospace; }
.card-section-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: #3B82F6; margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #1E2D45; }
[data-testid="stExpander"] { background: #0D1520 !important; border: 1px solid #1E2D45 !important; border-radius: 10px !important; margin-bottom: 0.75rem !important; }
[data-testid="stExpander"] summary { padding: 1rem 1.25rem !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; color: #E2E8F0 !important; }
[data-testid="stExpander"]:hover { border-color: #3B82F6 !important; }

.org-header { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #E2E8F0; padding: 0.75rem 0 0.5rem; border-bottom: 1px solid #1E2D45; margin-bottom: 0.75rem; }
.contact-name { font-size: 0.88rem; color: #E2E8F0; font-weight: 500; }
.contact-meta { font-size: 0.75rem; color: #475569; font-family: 'DM Mono', monospace; }
.email-preview-header { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase; color: #475569; margin: 0.75rem 0 0.4rem; }
.email-body-preview { background: #080C14; border: 1px solid #1E2D45; border-radius: 8px; padding: 1rem; font-size: 0.83rem; color: #94A3B8; line-height: 1.7; max-height: 300px; overflow-y: auto; }
[data-testid="stSpinner"] { color: #3B82F6 !important; }

.regen-btn button {
    background: transparent !important; border: 1px solid rgba(59,130,246,0.4) !important; color: #60A5FA !important;
    font-size: 0.72rem !important; padding: 0.28rem 0.75rem !important; width: auto !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 0.06em !important; border-radius: 6px !important; font-weight: 500 !important;
}
.regen-btn button:hover { background: rgba(59,130,246,0.1) !important; border-color: #3B82F6 !important; color: #93C5FD !important; box-shadow: none !important; transform: none !important; }

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
                              "selected_event_ids", "agent1_city", "agent1_state", "confirm_startover"]
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
col_header, col_startover, col_logout = st.columns([8, 1.2, 1])
with col_header:
    st.markdown("""
    <div class="lp-logo">Lead<span>Pulse</span></div>
    <div class="lp-tagline">Step 3 of 3 &nbsp;·&nbsp; Contacts & Outreach</div>
    """, unsafe_allow_html=True)
with col_startover:
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="startover-btn">', unsafe_allow_html=True)
    if st.button("Start Over", key="startover_btn"):
        st.session_state["confirm_startover"] = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col_logout:
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("Logout", key="logout_btn"):
        st.session_state["authentication_status"] = None
        st.session_state["name"] = None
        st.session_state["username"] = None
        st.switch_page("app.py")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if "enrichment_report" not in st.session_state:
    st.warning("No enrichment data found. Please complete Step 2 first.")
    if st.button("← Back to Enrichment"):
        st.switch_page("pages/2_Enrichment.py")
    st.stop()

# ── Setup ──────────────────────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

enrichment_report = st.session_state["enrichment_report"]

MOCK_EMAILS = [
    {"name": "Jasmin Rudra", "email": "jasmin.rudra@gmail.com"},
    {"name": "Mahir Patel",  "email": "mahirpatel31703@gmail.com"},
    {"name": "Mahir P",      "email": "mahirp3107@gmail.com"},
]

def build_mock_contacts(org: str, job_titles: list, org_index: int) -> list:
    count = 2 if org_index % 2 == 0 else 3
    contacts = []
    for i in range(count):
        mock  = MOCK_EMAILS[i % len(MOCK_EMAILS)]
        title = job_titles[i % len(job_titles)] if job_titles else "Corporate Travel Manager"
        contacts.append({"name": mock["name"], "email": mock["email"], "company": org, "title": title})
    return contacts

# ── Back button ────────────────────────────────────────────────────────────────
if st.button("← Back to Enrichment", key="back_to_enrichment"):
    st.switch_page("pages/2_Enrichment.py")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Apollo Contact Discovery (Simulated) ──────────────────────────────────────
st.markdown('<div class="card-section-label">Apollo — Contact Discovery (Simulated)</div>', unsafe_allow_html=True)
st.markdown('<div class="infobanner">Contacts below are simulated from Apollo.io based on attending organizations. Select who to reach out to.</div>', unsafe_allow_html=True)

for e in enrichment_report.enriched_events:
    st.markdown(f'<div class="org-header" style="color:#3B82F6;font-size:1rem;margin-bottom:1rem">📋 {e.event_name}</div>', unsafe_allow_html=True)
    orgs_to_show = e.attending_organizations[:5]
    job_titles   = e.target_contacts.job_titles

    for org_idx, org in enumerate(orgs_to_show):
        st.markdown(f'<div class="org-header">🏢 {org}</div>', unsafe_allow_html=True)
        contacts = build_mock_contacts(org, job_titles, org_idx)
        for contact in contacts:
            ck = f"contact_{e.event_id}_{org_idx}_{contact['email']}"
            col_check, col_info = st.columns([0.05, 0.95])
            with col_check:
                st.checkbox("Select contact", key=ck, value=False, label_visibility="collapsed")
            with col_info:
                st.markdown(
                    f'<div style="padding:0.5rem 0.75rem;background:#080C14;border:1px solid #111927;border-radius:8px;margin-bottom:0.4rem;display:flex;justify-content:space-between;align-items:center">'
                    f'<div>'
                    f'<div class="contact-name">{contact["name"]}</div>'
                    f'<div class="contact-meta">{contact["title"]} &nbsp;·&nbsp; {contact["email"]}</div>'
                    f'</div>'
                    f'<span class="category-tag">{org}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

# ── Collect selected contacts ──────────────────────────────────────────────────
all_contacts_by_event = {}
for e in enrichment_report.enriched_events:
    orgs_to_show = e.attending_organizations[:5]
    job_titles   = e.target_contacts.job_titles
    selected_for_event = []
    for org_idx, org in enumerate(orgs_to_show):
        contacts = build_mock_contacts(org, job_titles, org_idx)
        for contact in contacts:
            ck = f"contact_{e.event_id}_{org_idx}_{contact['email']}"
            if st.session_state.get(ck, False):
                selected_for_event.append(contact)
    if selected_for_event:
        all_contacts_by_event[e.event_id] = {"event": e, "contacts": selected_for_event}

total_selected = sum(len(v["contacts"]) for v in all_contacts_by_event.values())

# ── Generate Emails ────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Email Generation</div>', unsafe_allow_html=True)

if total_selected > 0:
    st.markdown(f'<div class="infobanner">⚡ {total_selected} contact(s) selected across {len(all_contacts_by_event)} event(s)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="dfwwarning">No contacts selected — check at least one contact above to generate emails.</div>', unsafe_allow_html=True)

gen_btn = st.button(
    f"Generate Emails for {total_selected} Contact(s)",
    key="gen_emails",
    disabled=total_selected == 0,
)

if gen_btn:
    from core.email_agent import generate_email
    generated = {}
    with st.spinner("Generating personalized emails…"):
        for event_id, payload in all_contacts_by_event.items():
            e        = payload["event"]
            contacts = payload["contacts"]
            generated[event_id] = []
            for contact in contacts:
                email_data = generate_email(e, contact["name"], contact["company"])
                generated[event_id].append({
                    "contact": contact,
                    "subject": email_data["subject"],
                    "body":    email_data["body"],
                    "status":  None,
                    "version": 0,
                })
    st.session_state["generated_emails"] = generated

# ── Email Preview + Regenerate + Send ─────────────────────────────────────────
if "generated_emails" in st.session_state:
    generated = st.session_state["generated_emails"]

    st.markdown('<div class="card-section-label">Email Preview — Review, Edit & Send</div>', unsafe_allow_html=True)
    st.markdown('<div class="infobanner">Review each email. Add an instruction and hit ↺ Regenerate to rewrite, or edit manually. Send when ready.</div>', unsafe_allow_html=True)

    updated_generated = {}
    for event_id, email_list in generated.items():
        matching_event = next((e for e in enrichment_report.enriched_events if e.event_id == event_id), None)
        event_name = matching_event.event_name if matching_event else event_id
        st.markdown(f'<div class="org-header" style="color:#3B82F6;font-size:1rem;margin-bottom:1rem">📋 {event_name}</div>', unsafe_allow_html=True)
        updated_generated[event_id] = []

        for idx, item in enumerate(email_list):
            contact = item["contact"]
            version = item.get("version", 0)

            with st.expander(f"✉️  {contact['name']}  ·  {contact['company']}  ·  {contact['email']}", expanded=True):

                # ── Subject row ────────────────────────────────────────────────
                new_subject = st.text_input(
                    "Subject",
                    value=item["subject"],
                    key=f"subj_{event_id}_{idx}_v{version}",
                )

                # ── Body ───────────────────────────────────────────────────────
                new_body = st.text_area(
                    "Body (HTML)",
                    value=item["body"],
                    height=280,
                    key=f"body_{event_id}_{idx}_v{version}",
                )

                # ── Live preview ───────────────────────────────────────────────
                st.markdown('<div class="email-preview-header">Live Preview</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="email-body-preview">{new_body}</div>', unsafe_allow_html=True)

                # ── Regenerate section ─────────────────────────────────────────
                st.markdown('<div style="height:0.75rem"></div>', unsafe_allow_html=True)
                st.markdown('<div style="height:1px;background:#1E2D45;margin-bottom:0.75rem"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-label" style="margin-bottom:0.4rem">Regenerate with Instruction</div>', unsafe_allow_html=True)

                col_instr, col_regen = st.columns([8, 1.5])
                with col_instr:
                    instruction = st.text_input(
                        "Instruction",
                        placeholder='e.g. "Make it shorter" or "Use a more formal tone"',
                        key=f"instr_{event_id}_{idx}_v{version}",
                        label_visibility="collapsed",
                    )
                with col_regen:
                    st.markdown('<div class="regen-btn">', unsafe_allow_html=True)
                    if st.button("Regenerate", key=f"regen_{event_id}_{idx}_v{version}"):
                        from core.email_agent import refine_email
                        with st.spinner("Regenerating…"):
                            refined = refine_email(
                                original_subject=item["subject"],
                                original_body=item["body"],
                                instruction=instruction or "Improve the email.",
                                event=matching_event,
                                recipient_name=contact["name"],
                                company=contact["company"],
                            )
                        st.session_state["generated_emails"][event_id][idx]["subject"] = refined["subject"]
                        st.session_state["generated_emails"][event_id][idx]["body"]    = refined["body"]
                        st.session_state["generated_emails"][event_id][idx]["version"] = version + 1
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                updated_generated[event_id].append({
                    "contact": contact,
                    "subject": new_subject,
                    "body":    new_body,
                    "status":  item.get("status"),
                    "version": version,
                })

    st.session_state["generated_emails"] = updated_generated

    # ── Send ──────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    send_btn = st.button("🚀 Send All Emails", key="send_emails")

    if send_btn:
        from core.email_agent import send_email
        sent_count = failed_count = 0

        with st.spinner("Sending emails…"):
            for event_id, email_list in st.session_state["generated_emails"].items():
                for item in email_list:
                    status = send_email(item["subject"], item["body"], item["contact"]["email"])
                    item["status"] = status
                    if status == "sent":
                        sent_count += 1
                    else:
                        failed_count += 1

        if sent_count:
            st.markdown(f'<div class="successbanner">✅ {sent_count} email(s) sent successfully.</div>', unsafe_allow_html=True)
        if failed_count:
            st.markdown(f'<div class="dfwwarning">⚠️ {failed_count} email(s) failed — check SendGrid logs.</div>', unsafe_allow_html=True)

        st.markdown('<div class="card-section-label">Outreach Log</div>', unsafe_allow_html=True)
        for event_id, email_list in st.session_state["generated_emails"].items():
            for item in email_list:
                icon = "✅" if item["status"] == "sent" else "❌"
                st.markdown(
                    f'{icon} **{item["contact"]["name"]}** · {item["contact"]["company"]} · '
                    f'`{item["contact"]["email"]}` · _{item["subject"]}_'
                )
                
        # ── Next Step ──────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="successbanner">✅ Outreach complete — generate SEO blog posts for your events.</div>', unsafe_allow_html=True)

if st.button("Next → Generate Blog Content", key="go_blog"):
    st.switch_page("pages/4_Blog_Content.py")