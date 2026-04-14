import streamlit as st
import sys
import os
import markdown as md_lib

st.set_page_config(
    page_title="LeadPulse — Blog Content",
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
.lp-tagline { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #475569; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0; }
.lp-divider { height: 1px; background: linear-gradient(90deg, #3B82F6 0%, #1E3A5F 40%, transparent 100%); margin: 1.5rem 0 2rem; }
.section-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: #3B82F6; margin-bottom: 0.6rem; font-weight: 600; }

.stButton > button {
    background: #3B82F6 !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.9rem !important;
    letter-spacing: 0.05em !important; padding: 0.65rem 2rem !important;
    transition: all 0.2s ease !important; width: 100% !important; height: 42px !important;
}
.stButton > button:hover { background: #2563EB !important; box-shadow: 0 0 20px rgba(59,130,246,0.35) !important; transform: translateY(-1px) !important; }
.stButton > button:disabled { background: #1E2D45 !important; color: #475569 !important; }

.infobanner { background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.25); border-radius: 8px; padding: 0.75rem 1rem; color: #60A5FA; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }
.successbanner { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); border-radius: 8px; padding: 0.75rem 1rem; color: #34D399; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }
.warningbanner { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.3); border-radius: 8px; padding: 0.75rem 1rem; color: #FCD34D; font-size: 0.82rem; font-family: 'DM Mono', monospace; margin-bottom: 1.5rem; }

.blog-preview { background: #0D1520; border: 1px solid #1E2D45; border-radius: 10px; padding: 2.5rem 3rem; margin-top: 1.5rem; }
.blog-preview h1 { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.5rem; }
.blog-preview h2 { font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 700; color: #93C5FD; margin-top: 1.5rem; margin-bottom: 0.5rem; }
.blog-preview h3 { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 600; color: #60A5FA; margin-top: 1.25rem; margin-bottom: 0.4rem; }
.blog-preview p { font-size: 0.92rem; color: #94A3B8; line-height: 1.8; margin-bottom: 1rem; }
.blog-preview strong { color: #CBD5E1; }
.blog-preview ul, .blog-preview ol { color: #94A3B8; font-size: 0.92rem; line-height: 1.8; padding-left: 1.5rem; }

.meta-box { background: rgba(59,130,246,0.06); border: 1px solid rgba(59,130,246,0.15); border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1rem; }
.meta-box label { font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: #475569; display: block; margin-bottom: 0.25rem; }
.meta-box p { margin: 0; font-size: 0.85rem; color: #CBD5E1; }

.event-info-box { background: rgba(59,130,246,0.06); border: 1px solid rgba(59,130,246,0.15); border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; }
.event-info-box label { font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; color: #475569; display: block; margin-bottom: 0.25rem; }
.event-info-box p { margin: 0; font-size: 0.9rem; color: #E2E8F0; font-weight: 600; }

.logout-btn button {
    background: transparent !important; border: 1px solid #1E2D45 !important; color: #475569 !important;
    font-size: 0.75rem !important; padding: 0.35rem 0.9rem !important; width: auto !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 0.08em !important; height: auto !important;
}
.logout-btn button:hover { border-color: #3B82F6 !important; color: #60A5FA !important; box-shadow: none !important; transform: none !important; }

.startover-btn button {
    background: transparent !important; border: 1px solid rgba(239,68,68,0.3) !important; color: #F87171 !important;
    font-size: 0.75rem !important; padding: 0.35rem 0.9rem !important; width: auto !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 0.08em !important; height: auto !important;
}
.startover-btn button:hover { border-color: #EF4444 !important; color: #EF4444 !important; box-shadow: none !important; transform: none !important; }

[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
col_header, col_btns = st.columns([7, 3])
with col_header:
    st.markdown("""
    <div class="lp-logo">Lead<span>Pulse</span></div>
    <div class="lp-tagline">Step 4 of 4 &nbsp;·&nbsp; Blog Content</div>
    """, unsafe_allow_html=True)
with col_btns:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        st.markdown('<div class="startover-btn">', unsafe_allow_html=True)
        if st.button("Start Over", key="startover_btn"):
            for k in ["agent1_report", "enrichment_report", "generated_emails",
                      "selected_event_ids", "agent1_city", "agent1_state", "generated_blog"]:
                st.session_state.pop(k, None)
            st.switch_page("pages/1_Event_Discovery.py")
        st.markdown('</div>', unsafe_allow_html=True)
    with b2:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            st.session_state["authentication_status"] = None
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if "enrichment_report" not in st.session_state:
    st.warning("No enrichment data found. Please complete Step 2 first.")
    if st.button("Back to Enrichment"):
        st.switch_page("pages/2_Enrichment.py")
    st.stop()

enrichment_report = st.session_state["enrichment_report"]
events = enrichment_report.enriched_events

if not events:
    st.warning("No enriched events available.")
    st.stop()

selected_event = events[0]

# ── Back button ────────────────────────────────────────────────────────────────
if st.button("Back to Contacts & Outreach", key="back_btn"):
    st.switch_page("pages/3_Contacts_Outreach.py")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Event info ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">SEO Blog Post</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="event-info-box"><label>Event</label><p>{selected_event.event_name}</p></div>',
    unsafe_allow_html=True,
)

# ── Guard: blog must already be generated ─────────────────────────────────────
if "generated_blog" not in st.session_state:
    st.markdown('<div class="warningbanner">No blog post found. Go back to Contacts & Outreach and click Next — Generate Blog Content.</div>', unsafe_allow_html=True)
    st.stop()

# ── Blog Preview ───────────────────────────────────────────────────────────────
blog = st.session_state["generated_blog"]

st.markdown('<div class="successbanner">Blog post generated — preview below.</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="meta-box">
    <label>SEO Title</label>
    <p><strong>{blog.seo_title}</strong></p>
</div>
<div class="meta-box">
    <label>Meta Description</label>
    <p>{blog.meta_description}</p>
</div>
<div class="meta-box">
    <label>URL Slug</label>
    <p style="font-family:'DM Mono',monospace;color:#60A5FA">/{blog.slug}/</p>
</div>
""", unsafe_allow_html=True)

try:
    body_html = md_lib.markdown(blog.body_markdown, extensions=["extra"])
except Exception:
    body_html = blog.body_markdown.replace("\n", "<br>")

st.markdown(
    f'<div class="blog-preview"><h1>{blog.seo_title}</h1>{body_html}</div>',
    unsafe_allow_html=True,
)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="description" content="{blog.meta_description}">
    <title>{blog.seo_title}</title>
    <style>
        body {{ font-family: Georgia, serif; max-width: 800px; margin: 60px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.8; }}
        h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        h2 {{ font-size: 1.3rem; margin-top: 2rem; color: #1a4fa0; }}
        h3 {{ font-size: 1.1rem; margin-top: 1.5rem; color: #333; }}
        p {{ margin-bottom: 1rem; }}
        ul, ol {{ margin-bottom: 1rem; padding-left: 1.5rem; }}
        .meta {{ font-size: 0.85rem; color: #666; margin-bottom: 2rem; }}
    </style>
</head>
<body>
    <h1>{blog.seo_title}</h1>
    <div class="meta">URL: /{blog.slug}/ &nbsp;|&nbsp; {blog.meta_description}</div>
    {body_html}
</body>
</html>"""
# ── Refine Blog ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:#1E2D45;margin-bottom:1rem"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label" style="margin-bottom:0.4rem">Refine Blog Post</div>', unsafe_allow_html=True)

refine_instruction = st.text_input(
    "Refine Instruction",
    placeholder='e.g. "Make it more formal" or "Add more urgency to the CTA"',
    key="blog_refine_instruction",
    label_visibility="collapsed",
)
if st.button("Regenerate Blog Post", key="refine_blog"):
    if not refine_instruction.strip():
        st.warning("Please enter an instruction before regenerating.")
    else:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from core.content_agent import refine_blog_post
        with st.spinner("Regenerating blog post…"):
            try:
                refined_blog = refine_blog_post(
                    original_blog=st.session_state["generated_blog"],
                    instruction=refine_instruction.strip(),
                )
                st.session_state["generated_blog"] = refined_blog
                st.rerun()
            except Exception as e:
                st.error(f"Refinement failed: {e}")
                
st.download_button(
    label="Download as HTML",
    data=full_html,
    file_name=f"{blog.slug}.html",
    mime="text/html",
    key="download_blog",
)

# ── Bottom navigation ──────────────────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="lp-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="successbanner">Pipeline complete — go back to pick the next event.</div>', unsafe_allow_html=True)

if st.button("Back to Events List", key="back_to_discovery_final"):
    st.session_state.pop("enrichment_report", None)
    st.session_state.pop("generated_emails", None)
    st.session_state.pop("generated_blog", None)
    st.switch_page("pages/1_Event_Discovery.py")