"""
SiteForge — AI-Powered Website Generator
Streamlit wizard app: business info → template → palette → AI content → preview & download
"""

import sys
import os
import time

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Path setup — allow imports from core/
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from core.content_gen import generate_website_content, ollama_is_available
from core.renderer import render_site, PALETTES, TEMPLATE_NAMES, TEMPLATE_DISPLAY
from core.exporter import build_zip

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SiteForge — AI Website Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Global CSS — dark theme matching config.toml
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
/* ── Import font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root overrides ── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Main container padding ── */
.block-container { padding-top: 2rem !important; padding-bottom: 4rem !important; max-width: 1100px !important; }

/* ── Gradient text helper ── */
.gradient-text {
    background: linear-gradient(135deg, #6C63FF, #A78BFA, #EC4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Hero section ── */
.sf-hero {
    text-align: center;
    padding: 4rem 2rem 3rem;
}
.sf-hero h1 {
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.05;
    margin-bottom: 1.25rem;
}
.sf-hero p {
    font-size: 1.2rem;
    color: #A0A0C0;
    max-width: 540px;
    margin: 0 auto 2.5rem;
    line-height: 1.7;
}

/* ── Feature chips ── */
.feature-chips {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 2.5rem;
}
.feature-chip {
    background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.25);
    color: #A78BFA;
    padding: 0.4rem 1rem;
    border-radius: 100px;
    font-size: 0.82rem;
    font-weight: 600;
}

/* ── Cards ── */
.sf-card {
    background: #1A1A2E;
    border: 1px solid #2D2D4E;
    border-radius: 16px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
    transition: all 0.2s ease;
}
.sf-card:hover {
    border-color: #6C63FF;
    box-shadow: 0 0 0 1px #6C63FF20, 0 8px 32px rgba(108,99,255,0.12);
}

/* ── Template cards ── */
.template-card {
    background: #1A1A2E;
    border: 2px solid #2D2D4E;
    border-radius: 16px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    height: 100%;
    position: relative;
    text-align: center;
}
.template-card.selected {
    border-color: #6C63FF;
    background: rgba(108,99,255,0.08);
    box-shadow: 0 0 0 1px #6C63FF40;
}
.template-card:hover {
    border-color: #6C63FF80;
    transform: translateY(-2px);
}
.template-preview {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    display: block;
}
.template-name {
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 0.4rem;
    color: #E8E8F0;
}
.template-desc {
    font-size: 0.8rem;
    color: #A0A0C0;
    line-height: 1.5;
}
.selected-badge {
    position: absolute;
    top: 0.75rem; right: 0.75rem;
    background: #6C63FF;
    color: white;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 100px;
    letter-spacing: 0.05em;
}

/* ── Palette cards ── */
.palette-card {
    background: #1A1A2E;
    border: 2px solid #2D2D4E;
    border-radius: 12px;
    padding: 1.25rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
}
.palette-card.selected {
    border-color: #6C63FF;
    box-shadow: 0 0 0 1px #6C63FF40;
}
.palette-card:hover {
    border-color: #6C63FF80;
    transform: translateY(-2px);
}
.palette-swatches {
    display: flex;
    gap: 4px;
    justify-content: center;
    margin-bottom: 0.75rem;
}
.swatch {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.1);
}
.palette-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #E8E8F0;
}

/* ── Step indicator ── */
.step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin-bottom: 2.5rem;
    padding: 0 1rem;
}
.step-dot {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 700;
    flex-shrink: 0;
    transition: all 0.3s;
}
.step-dot.active {
    background: #6C63FF;
    color: white;
    box-shadow: 0 0 0 4px rgba(108,99,255,0.25);
}
.step-dot.done {
    background: rgba(108,99,255,0.3);
    color: #A78BFA;
}
.step-dot.inactive {
    background: #2D2D4E;
    color: #555580;
}
.step-line {
    flex: 1;
    height: 2px;
    background: #2D2D4E;
    max-width: 60px;
}
.step-line.done {
    background: rgba(108,99,255,0.4);
}
.step-label {
    font-size: 0.72rem;
    color: #A0A0C0;
    text-align: center;
    margin-top: 0.35rem;
}

/* ── Section headings ── */
.sf-section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #E8E8F0;
    margin-bottom: 0.4rem;
    letter-spacing: -0.02em;
}
.sf-section-sub {
    font-size: 0.9rem;
    color: #A0A0C0;
    margin-bottom: 2rem;
}

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #6C63FF, #8B5CF6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.75rem !important;
    font-size: 0.95rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(108,99,255,0.3) !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(108,99,255,0.45) !important;
    filter: brightness(1.08) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(108,99,255,0.12) !important;
    border: 1px solid rgba(108,99,255,0.3) !important;
    color: #A78BFA !important;
    box-shadow: none !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(108,99,255,0.2) !important;
    box-shadow: none !important;
    filter: none !important;
}

/* ── Info boxes ── */
.sf-info {
    background: rgba(108,99,255,0.08);
    border: 1px solid rgba(108,99,255,0.2);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    color: #A78BFA;
    font-size: 0.88rem;
    margin-bottom: 1.25rem;
}
.sf-warning {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    color: #FCD34D;
    font-size: 0.88rem;
    margin-bottom: 1.25rem;
}
.sf-success {
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.25);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    color: #6EE7B7;
    font-size: 0.88rem;
    margin-bottom: 1.25rem;
}

/* ── Content preview text areas ── */
div[data-testid="stTextArea"] textarea {
    background: #0E0E1A !important;
    border: 1px solid #2D2D4E !important;
    border-radius: 8px !important;
    color: #E8E8F0 !important;
    font-size: 0.88rem !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.2) !important;
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] textarea {
    background: #1A1A2E !important;
    border: 1px solid #2D2D4E !important;
    border-radius: 8px !important;
    color: #E8E8F0 !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #6C63FF !important;
}

/* ── Selectbox ── */
div[data-testid="stSelectbox"] > div > div {
    background: #1A1A2E !important;
    border-color: #2D2D4E !important;
}

/* ── Divider ── */
hr {
    border-color: #2D2D4E !important;
    margin: 2rem 0 !important;
}

/* ── Progress bar ── */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6C63FF, #A78BFA) !important;
}

/* ── Nav buttons row ── */
.nav-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1.5rem;
    border-top: 1px solid #2D2D4E;
    margin-top: 2rem;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #059669, #10B981) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.3) !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(16,185,129,0.45) !important;
    filter: brightness(1.08) !important;
}

/* ── Checkbox ── */
div[data-testid="stCheckbox"] label {
    color: #E8E8F0 !important;
}

/* ── Multiselect ── */
div[data-testid="stMultiSelect"] > div {
    background: #1A1A2E !important;
    border-color: #2D2D4E !important;
}

/* ── iframe border ── */
iframe {
    border-radius: 12px;
    border: 1px solid #2D2D4E !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
STEPS = ["Home", "Business Info", "Template", "Palette", "AI Content", "Preview"]
SECTIONS_OPTIONS = ["Hero", "About", "Services", "Testimonials", "Gallery", "FAQ", "Map", "Contact Form"]

TEMPLATE_META = {
    "clean": {
        "icon": "🪴",
        "desc": "Modern, minimal layout with soft shadows and gentle gradients. Great for most businesses.",
    },
    "bold": {
        "icon": "⚡",
        "desc": "High-contrast dark design with chunky typography and strong visual hierarchy.",
    },
    "warm": {
        "icon": "🌿",
        "desc": "Friendly, rounded design with warm gradients. Ideal for lifestyle and wellness brands.",
    },
    "corporate": {
        "icon": "🏛",
        "desc": "Formal, grid-based layout with a professional navy palette. Perfect for B2B.",
    },
    "starter": {
        "icon": "✦",
        "desc": "Ultra-minimal one-pager with maximum whitespace. Best for personal portfolios.",
    },
}

CONTENT_FIELDS = [
    ("hero_headline", "Hero Headline"),
    ("hero_subheadline", "Hero Subheadline"),
    ("hero_cta", "CTA Button Text"),
    ("about_headline", "About Headline"),
    ("about_paragraph", "About Paragraph"),
    ("about_highlight_1", "About Highlight 1"),
    ("about_highlight_2", "About Highlight 2"),
    ("about_highlight_3", "About Highlight 3"),
    ("services_headline", "Services Headline"),
    ("services_subheadline", "Services Intro"),
    ("service_1_name", "Service 1 Name"),
    ("service_1_description", "Service 1 Description"),
    ("service_2_name", "Service 2 Name"),
    ("service_2_description", "Service 2 Description"),
    ("service_3_name", "Service 3 Name"),
    ("service_3_description", "Service 3 Description"),
    ("service_4_name", "Service 4 Name"),
    ("service_4_description", "Service 4 Description"),
    ("testimonials_headline", "Testimonials Headline"),
    ("testimonial_1_text", "Testimonial 1 Text"),
    ("testimonial_1_name", "Testimonial 1 Name"),
    ("testimonial_1_role", "Testimonial 1 Role"),
    ("testimonial_2_text", "Testimonial 2 Text"),
    ("testimonial_2_name", "Testimonial 2 Name"),
    ("testimonial_2_role", "Testimonial 2 Role"),
    ("testimonial_3_text", "Testimonial 3 Text"),
    ("testimonial_3_name", "Testimonial 3 Name"),
    ("testimonial_3_role", "Testimonial 3 Role"),
    ("faq_headline", "FAQ Headline"),
    ("faq_1_q", "FAQ 1 Question"),
    ("faq_1_a", "FAQ 1 Answer"),
    ("faq_2_q", "FAQ 2 Question"),
    ("faq_2_a", "FAQ 2 Answer"),
    ("faq_3_q", "FAQ 3 Question"),
    ("faq_3_a", "FAQ 3 Answer"),
    ("faq_4_q", "FAQ 4 Question"),
    ("faq_4_a", "FAQ 4 Answer"),
    ("contact_headline", "Contact Headline"),
    ("contact_subheadline", "Contact Subheadline"),
    ("footer_tagline", "Footer Tagline"),
    ("meta_description", "SEO Meta Description"),
]

defaults = {
    "step": 0,
    # Business info
    "biz_name": "",
    "biz_tagline": "",
    "biz_description": "",
    "biz_industry": "",
    "biz_services": "",
    "biz_email": "",
    "biz_phone": "",
    "biz_address": "",
    "biz_tone": "Professional",
    "biz_sections": ["Hero", "About", "Services", "Contact Form"],
    # Template & palette
    "selected_template": "clean",
    "selected_palette": "Modern Blue",
    # Generated content
    "generated_content": {},
    "edited_content": {},
    "rendered_html": "",
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------------------------------------------------------------------
# Helper: step indicator
# ---------------------------------------------------------------------------
def render_step_indicator(current_step: int):
    step_labels = ["Home", "Info", "Template", "Palette", "AI", "Preview"]
    cols = st.columns(len(step_labels) * 2 - 1)
    for i, label in enumerate(step_labels):
        col_idx = i * 2
        with cols[col_idx]:
            if i < current_step:
                cls = "done"
                icon = "✓"
            elif i == current_step:
                cls = "active"
                icon = str(i + 1)
            else:
                cls = "inactive"
                icon = str(i + 1)
            st.markdown(
                f'<div style="text-align:center">'
                f'<div class="step-dot {cls}" style="margin:0 auto">{icon}</div>'
                f'<div class="step-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        if i < len(step_labels) - 1:
            line_cls = "done" if i < current_step else ""
            with cols[col_idx + 1]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;height:32px;">'
                    f'<div class="step-line {line_cls}" style="width:100%"></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def go_to(step: int):
    st.session_state.step = step
    st.rerun()


# ---------------------------------------------------------------------------
# STEP 0 — HOME
# ---------------------------------------------------------------------------
def render_home():
    st.markdown(
        """
<div class="sf-hero">
  <h1><span class="gradient-text">SiteForge</span></h1>
  <p>Generate a complete, professional website for your business in minutes — powered by local AI.</p>
  <div class="feature-chips">
    <span class="feature-chip">⚡ AI-Generated Copy</span>
    <span class="feature-chip">🎨 5 Pro Templates</span>
    <span class="feature-chip">🌈 5 Color Palettes</span>
    <span class="feature-chip">📦 Download as ZIP</span>
    <span class="feature-chip">🔒 100% Local — No API Keys</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
<div class="sf-card">
  <div style="font-size:2rem;margin-bottom:0.75rem">📝</div>
  <div style="font-weight:700;font-size:1rem;color:#E8E8F0;margin-bottom:0.4rem">1. Describe Your Business</div>
  <div style="font-size:0.85rem;color:#A0A0C0;line-height:1.6">Tell SiteForge your business name, what you do, and what sections you need.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
<div class="sf-card">
  <div style="font-size:2rem;margin-bottom:0.75rem">🎨</div>
  <div style="font-weight:700;font-size:1rem;color:#E8E8F0;margin-bottom:0.4rem">2. Pick Your Style</div>
  <div style="font-size:0.85rem;color:#A0A0C0;line-height:1.6">Choose from 5 professionally designed templates and 5 curated color palettes.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
<div class="sf-card">
  <div style="font-size:2rem;margin-bottom:0.75rem">🤖</div>
  <div style="font-weight:700;font-size:1rem;color:#E8E8F0;margin-bottom:0.4rem">3. AI Writes Your Copy</div>
  <div style="font-size:0.85rem;color:#A0A0C0;line-height:1.6">Ollama (llama3.2) generates all your headlines, service descriptions, testimonials, and FAQs.</div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(3)
    with col_a:
        st.markdown(
            """
<div class="sf-card">
  <div style="font-size:2rem;margin-bottom:0.75rem">👁</div>
  <div style="font-weight:700;font-size:1rem;color:#E8E8F0;margin-bottom:0.4rem">4. Preview Live</div>
  <div style="font-size:0.85rem;color:#A0A0C0;line-height:1.6">See your full website rendered in a live preview inside the app.</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            """
<div class="sf-card">
  <div style="font-size:2rem;margin-bottom:0.75rem">📦</div>
  <div style="font-weight:700;font-size:1rem;color:#E8E8F0;margin-bottom:0.4rem">5. Download & Deploy</div>
  <div style="font-size:0.85rem;color:#A0A0C0;line-height:1.6">Download as a ZIP with index.html, style.css, and a GitHub Pages deploy script.</div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Ollama status
    ollama_ok = ollama_is_available()
    if ollama_ok:
        st.markdown(
            '<div class="sf-success">✓ Ollama is running — AI content generation is ready.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sf-warning">⚠ Ollama is not running. Start it with <code>ollama serve</code> before generating AI content. You can still build manually.</div>',
            unsafe_allow_html=True,
        )

    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("Start Building →", use_container_width=True):
            go_to(1)


# ---------------------------------------------------------------------------
# STEP 1 — BUSINESS INFO
# ---------------------------------------------------------------------------
def render_business_info():
    st.markdown('<div class="sf-section-title">Tell us about your business</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sf-section-sub">Fill in what you know — the AI will fill in the gaps. Only the business name is required.</div>',
        unsafe_allow_html=True,
    )

    with st.form("biz_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Business Name *", value=st.session_state.biz_name, placeholder="e.g. Peak Plumbing Co.")
            tagline = st.text_input("Tagline", value=st.session_state.biz_tagline, placeholder="e.g. Trusted pipes, on time")
            industry = st.text_input("Industry", value=st.session_state.biz_industry, placeholder="e.g. Home Services, Retail, Consulting")
            email = st.text_input("Contact Email", value=st.session_state.biz_email, placeholder="hello@example.com")
        with col2:
            description = st.text_area(
                "What does your business do?",
                value=st.session_state.biz_description,
                placeholder="Describe what you offer, who you serve, and what makes you different...",
                height=120,
            )
            services_raw = st.text_input(
                "Main Services / Products (comma-separated)",
                value=st.session_state.biz_services,
                placeholder="e.g. Emergency plumbing, Pipe installation, Drain cleaning",
            )
            phone = st.text_input("Phone", value=st.session_state.biz_phone, placeholder="+1 (555) 000-0000")
            address = st.text_input("Address", value=st.session_state.biz_address, placeholder="123 Main St, City, State")

        st.markdown("---")
        col3, col4 = st.columns(2)
        with col3:
            tone = st.selectbox(
                "Tone / Voice",
                ["Professional", "Friendly", "Playful", "Luxury", "Technical"],
                index=["Professional", "Friendly", "Playful", "Luxury", "Technical"].index(
                    st.session_state.biz_tone
                ),
            )
        with col4:
            sections = st.multiselect(
                "Sections to include",
                SECTIONS_OPTIONS,
                default=st.session_state.biz_sections,
            )

        submitted = st.form_submit_button("Save & Continue →", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Business name is required.")
            return
        st.session_state.biz_name = name.strip()
        st.session_state.biz_tagline = tagline.strip()
        st.session_state.biz_description = description.strip()
        st.session_state.biz_industry = industry.strip()
        st.session_state.biz_services = services_raw.strip()
        st.session_state.biz_email = email.strip()
        st.session_state.biz_phone = phone.strip()
        st.session_state.biz_address = address.strip()
        st.session_state.biz_tone = tone
        st.session_state.biz_sections = sections if sections else ["Hero", "About", "Services", "Contact Form"]
        go_to(2)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home", key="back_home"):
        go_to(0)


# ---------------------------------------------------------------------------
# STEP 2 — CHOOSE TEMPLATE
# ---------------------------------------------------------------------------
def render_template_picker():
    st.markdown('<div class="sf-section-title">Choose your template</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sf-section-sub">Each template is a fully responsive Jinja2 layout — pick the style that fits your brand.</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(TEMPLATE_NAMES))
    for i, tname in enumerate(TEMPLATE_NAMES):
        meta = TEMPLATE_META[tname]
        is_selected = st.session_state.selected_template == tname
        badge = '<span class="selected-badge">SELECTED</span>' if is_selected else ""
        with cols[i]:
            st.markdown(
                f"""
<div class="template-card {'selected' if is_selected else ''}">
  {badge}
  <span class="template-preview">{meta['icon']}</span>
  <div class="template-name">{TEMPLATE_DISPLAY[tname]}</div>
  <div class="template-desc">{meta['desc']}</div>
</div>
""",
                unsafe_allow_html=True,
            )
            if st.button(
                f"Select {TEMPLATE_DISPLAY[tname]}",
                key=f"sel_tpl_{tname}",
                use_container_width=True,
            ):
                st.session_state.selected_template = tname
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("← Back", key="back_tpl"):
            go_to(1)
    with col_next:
        if st.button("Continue →", key="next_tpl", use_container_width=True):
            go_to(3)


# ---------------------------------------------------------------------------
# STEP 3 — CHOOSE PALETTE
# ---------------------------------------------------------------------------
def render_palette_picker():
    st.markdown('<div class="sf-section-title">Choose your color palette</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sf-section-sub">All colors are applied via CSS variables — you can always regenerate with a different palette.</div>',
        unsafe_allow_html=True,
    )

    palette_names = list(PALETTES.keys())
    cols = st.columns(len(palette_names))

    for i, pname in enumerate(palette_names):
        p = PALETTES[pname]
        is_selected = st.session_state.selected_palette == pname
        with cols[i]:
            swatches = "".join(
                [
                    f'<div class="swatch" style="background:{p[k]}"></div>'
                    for k in ["primary", "secondary", "accent", "background", "footer_bg"]
                ]
            )
            st.markdown(
                f"""
<div class="palette-card {'selected' if is_selected else ''}">
  <div class="palette-swatches">{swatches}</div>
  <div class="palette-name">{pname}</div>
</div>
""",
                unsafe_allow_html=True,
            )
            if st.button(
                "Select" if not is_selected else "✓ Selected",
                key=f"sel_pal_{i}",
                use_container_width=True,
            ):
                st.session_state.selected_palette = pname
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("← Back", key="back_pal"):
            go_to(2)
    with col_next:
        if st.button("Continue →", key="next_pal", use_container_width=True):
            go_to(4)


# ---------------------------------------------------------------------------
# STEP 4 — AI CONTENT GENERATION
# ---------------------------------------------------------------------------
def render_ai_content():
    st.markdown('<div class="sf-section-title">Generate AI content</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sf-section-sub">Ollama (llama3.2) will write all your website copy. Edit any field before continuing.</div>',
        unsafe_allow_html=True,
    )

    # Build business_info dict
    services_list = [
        s.strip() for s in st.session_state.biz_services.split(",") if s.strip()
    ] or ["Consultation", "Planning", "Execution", "Support"]

    business_info = {
        "name": st.session_state.biz_name or "My Business",
        "description": st.session_state.biz_description,
        "phone": st.session_state.biz_phone,
        "email": st.session_state.biz_email,
        "address": st.session_state.biz_address,
        "tone": st.session_state.biz_tone,
        "sections": st.session_state.biz_sections,
        "color_scheme": st.session_state.selected_palette,
        "services": services_list,
    }

    # Generate button
    ollama_ok = ollama_is_available()
    if not ollama_ok:
        st.markdown(
            '<div class="sf-warning">⚠ Ollama is not reachable. Run <code>ollama serve</code> in a terminal, then click Generate. Or skip to use default placeholder content.</div>',
            unsafe_allow_html=True,
        )

    col_gen, col_skip = st.columns([2, 1])
    with col_gen:
        gen_btn = st.button(
            "Generate with AI (llama3.2)",
            use_container_width=True,
            disabled=not ollama_ok,
        )
    with col_skip:
        skip_btn = st.button("Use Default Content", use_container_width=True)

    if gen_btn:
        progress = st.progress(0, text="Connecting to Ollama...")
        try:
            progress.progress(20, text="Crafting your copy with llama3.2...")
            content = generate_website_content(business_info)
            progress.progress(90, text="Finalising...")
            time.sleep(0.3)
            progress.progress(100, text="Done!")
            st.session_state.generated_content = content
            st.session_state.edited_content = dict(content)
            st.markdown(
                '<div class="sf-success">✓ Content generated! Review and edit below.</div>',
                unsafe_allow_html=True,
            )
        except RuntimeError as e:
            progress.empty()
            st.error(f"Generation failed: {e}")
            return

    if skip_btn:
        from core.content_gen import _default_content
        content = _default_content(
            business_info["name"], business_info["description"], business_info
        )
        content["color_scheme"] = st.session_state.selected_palette
        st.session_state.generated_content = content
        st.session_state.edited_content = dict(content)
        st.markdown(
            '<div class="sf-info">ℹ Using default placeholder content. You can still edit all fields below.</div>',
            unsafe_allow_html=True,
        )

    # Editable fields
    if st.session_state.edited_content:
        st.markdown("---")
        st.markdown(
            '<div style="font-weight:600;color:#A78BFA;margin-bottom:1rem">Edit generated content</div>',
            unsafe_allow_html=True,
        )

        # Group into expanders for cleaner UI
        groups = {
            "Hero": ["hero_headline", "hero_subheadline", "hero_cta"],
            "About": ["about_headline", "about_paragraph", "about_highlight_1", "about_highlight_2", "about_highlight_3"],
            "Services": [
                "services_headline", "services_subheadline",
                "service_1_name", "service_1_description",
                "service_2_name", "service_2_description",
                "service_3_name", "service_3_description",
                "service_4_name", "service_4_description",
            ],
            "Testimonials": [
                "testimonials_headline",
                "testimonial_1_text", "testimonial_1_name", "testimonial_1_role",
                "testimonial_2_text", "testimonial_2_name", "testimonial_2_role",
                "testimonial_3_text", "testimonial_3_name", "testimonial_3_role",
            ],
            "FAQ": [
                "faq_headline",
                "faq_1_q", "faq_1_a", "faq_2_q", "faq_2_a",
                "faq_3_q", "faq_3_a", "faq_4_q", "faq_4_a",
            ],
            "Contact & Footer": ["contact_headline", "contact_subheadline", "footer_tagline", "meta_description"],
        }

        field_label_map = dict(CONTENT_FIELDS)

        for group_name, fields in groups.items():
            relevant = [f for f in fields if f in st.session_state.edited_content]
            if not relevant:
                continue
            with st.expander(f"{group_name}", expanded=(group_name == "Hero")):
                for field in relevant:
                    label = field_label_map.get(field, field)
                    current = st.session_state.edited_content.get(field, "")
                    is_long = len(current) > 80 or "paragraph" in field or "description" in field or "_a" in field or "text" in field
                    if is_long:
                        new_val = st.text_area(label, value=current, key=f"edit_{field}", height=90)
                    else:
                        new_val = st.text_input(label, value=current, key=f"edit_{field}")
                    st.session_state.edited_content[field] = new_val

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("← Back", key="back_ai"):
            go_to(3)
    with col_next:
        can_continue = bool(st.session_state.edited_content)
        if st.button("Preview Website →", key="next_ai", use_container_width=True, disabled=not can_continue):
            # Merge edited content with non-editable fields
            final = dict(st.session_state.edited_content)
            final["business_name"] = st.session_state.biz_name or "My Business"
            final["phone"] = st.session_state.biz_phone
            final["email"] = st.session_state.biz_email
            final["address"] = st.session_state.biz_address
            final["sections"] = st.session_state.biz_sections
            final["color_scheme"] = st.session_state.selected_palette
            final["tone"] = st.session_state.biz_tone

            with st.spinner("Rendering your website..."):
                try:
                    html = render_site(st.session_state.selected_template, final)
                    st.session_state.rendered_html = html
                    st.session_state.edited_content = final
                    go_to(5)
                except Exception as e:
                    st.error(f"Render error: {e}")


# ---------------------------------------------------------------------------
# STEP 5 — PREVIEW & DOWNLOAD
# ---------------------------------------------------------------------------
def render_preview():
    st.markdown('<div class="sf-section-title">Preview & Download</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sf-section-sub">Your website is ready. Preview it below, then download the ZIP to deploy anywhere.</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.rendered_html:
        st.warning("No rendered site found. Go back and generate content first.")
        if st.button("← Back to AI Content"):
            go_to(4)
        return

    # Re-render button (if user went back and edited)
    col_re, col_dl = st.columns([1, 1])
    with col_re:
        if st.button("Re-render with current content", key="rerender"):
            final = dict(st.session_state.edited_content)
            final["business_name"] = st.session_state.biz_name or "My Business"
            final["phone"] = st.session_state.biz_phone
            final["email"] = st.session_state.biz_email
            final["address"] = st.session_state.biz_address
            final["sections"] = st.session_state.biz_sections
            final["color_scheme"] = st.session_state.selected_palette
            final["tone"] = st.session_state.biz_tone
            try:
                html = render_site(st.session_state.selected_template, final)
                st.session_state.rendered_html = html
                st.rerun()
            except Exception as e:
                st.error(f"Render error: {e}")

    with col_dl:
        zip_bytes = build_zip(
            st.session_state.rendered_html,
            st.session_state.biz_name or "website",
        )
        biz_slug = (
            (st.session_state.biz_name or "website")
            .lower()
            .replace(" ", "-")
            .replace("'", "")[:30]
        )
        st.download_button(
            label="Download ZIP",
            data=zip_bytes,
            file_name=f"{biz_slug}-website.zip",
            mime="application/zip",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Live preview
    st.markdown(
        '<div style="font-weight:600;color:#A78BFA;font-size:0.9rem;margin-bottom:0.75rem;letter-spacing:0.05em;text-transform:uppercase">Live Preview</div>',
        unsafe_allow_html=True,
    )
    components.html(st.session_state.rendered_html, height=620, scrolling=True)

    # Summary card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="sf-card">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem;text-align:center">
    <div>
      <div style="font-size:1.5rem;margin-bottom:0.25rem">🏢</div>
      <div style="font-size:0.72rem;color:#A0A0C0;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.2rem">Business</div>
      <div style="font-weight:600;font-size:0.88rem">{st.session_state.biz_name or "—"}</div>
    </div>
    <div>
      <div style="font-size:1.5rem;margin-bottom:0.25rem">{TEMPLATE_META[st.session_state.selected_template]['icon']}</div>
      <div style="font-size:0.72rem;color:#A0A0C0;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.2rem">Template</div>
      <div style="font-weight:600;font-size:0.88rem">{TEMPLATE_DISPLAY[st.session_state.selected_template]}</div>
    </div>
    <div>
      <div style="font-size:1.5rem;margin-bottom:0.25rem">🎨</div>
      <div style="font-size:0.72rem;color:#A0A0C0;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.2rem">Palette</div>
      <div style="font-weight:600;font-size:0.88rem">{st.session_state.selected_palette}</div>
    </div>
    <div>
      <div style="font-size:1.5rem;margin-bottom:0.25rem">📄</div>
      <div style="font-size:0.72rem;color:#A0A0C0;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.2rem">Sections</div>
      <div style="font-weight:600;font-size:0.88rem">{len(st.session_state.biz_sections)} sections</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_restart = st.columns([1, 1])
    with col_back:
        if st.button("← Edit Content", key="back_preview"):
            go_to(4)
    with col_restart:
        if st.button("Start Over", key="restart"):
            for k, v in defaults.items():
                st.session_state[k] = v
            go_to(0)


# ---------------------------------------------------------------------------
# MAIN ROUTER
# ---------------------------------------------------------------------------
def main():
    step = st.session_state.step

    # Render step indicator for all steps except home
    if step > 0:
        render_step_indicator(step)
        st.markdown("<br>", unsafe_allow_html=True)

    if step == 0:
        render_home()
    elif step == 1:
        render_business_info()
    elif step == 2:
        render_template_picker()
    elif step == 3:
        render_palette_picker()
    elif step == 4:
        render_ai_content()
    elif step == 5:
        render_preview()
    else:
        st.error("Unknown step. Resetting.")
        st.session_state.step = 0
        st.rerun()


if __name__ == "__main__":
    main()
