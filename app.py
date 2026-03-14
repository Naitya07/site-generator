"""
SiteForge — Small Business Website Generator
Streamlit wizard: business info → design → sections → AI generate → preview → download
"""

import base64
import time

import streamlit as st

from core.content_gen import generate_website_content, ollama_is_available
from core.exporter import build_zip
from core.renderer import PALETTES, TEMPLATE_NAMES, render_site

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SiteForge — Website Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family:'Inter',system-ui,sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top:0 !important; padding-bottom:2rem; max-width:none !important; }
section[data-testid="stSidebar"] { display:none; }

/* ── Header ── */
.sf-hero {
    background: linear-gradient(135deg,#1A1A2E 0%,#16213E 50%,#0F3460 100%);
    border-bottom:1px solid #2D2D4E;
    padding:2rem 3rem 1.75rem;
    margin:-1rem -1rem 0 -1rem;
}
.sf-logo-text { font-size:1.6rem;font-weight:800;color:#F1F0FB;letter-spacing:-0.03em; }
.sf-logo-text span { color:#6C63FF; }
.sf-logo-sub { font-size:0.78rem;color:#6B6B8A;font-weight:500;margin-top:0.1rem; }
.sf-badge { background:rgba(108,99,255,0.15);border:1px solid rgba(108,99,255,0.3);color:#A78BFA;padding:0.35rem 0.85rem;border-radius:100px;font-size:0.75rem;font-weight:600; }

/* ── Progress ── */
.sf-prog { padding:1.25rem 3rem;background:#0E0E1A;border-bottom:1px solid #1E1E32; }
.sf-prog-inner { max-width:680px;margin:0 auto; }
.sf-steps { display:flex;align-items:center;justify-content:space-between;position:relative; }
.sf-steps::before { content:'';position:absolute;top:17px;left:17px;right:17px;height:2px;background:#2D2D4E;z-index:0; }
.sf-step { display:flex;flex-direction:column;align-items:center;gap:0.35rem;position:relative;z-index:1; }
.sf-step-dot { width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:700;border:2px solid #2D2D4E;background:#1A1A2E;color:#5A5A7A; }
.sf-step-dot.active { background:#6C63FF;border-color:#6C63FF;color:white;box-shadow:0 0 0 4px rgba(108,99,255,0.2); }
.sf-step-dot.done { background:#22C55E;border-color:#22C55E;color:white; }
.sf-step-label { font-size:0.68rem;font-weight:600;color:#5A5A7A;white-space:nowrap; }
.sf-step-label.active { color:#A78BFA; }
.sf-step-label.done { color:#22C55E; }

/* ── Cards ── */
.sf-card-title { font-size:1.35rem;font-weight:800;color:#F1F0FB;letter-spacing:-0.025em;margin-bottom:0.35rem; }
.sf-card-sub { font-size:0.88rem;color:#6B6B8A;margin-bottom:1.75rem; }

/* ── Info boxes ── */
.sf-info { background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.2);border-radius:10px;padding:0.9rem 1.1rem;color:#A78BFA;font-size:0.86rem;margin-bottom:1rem; }
.sf-warn { background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.2);border-radius:10px;padding:0.9rem 1.1rem;color:#FCD34D;font-size:0.86rem;margin-bottom:1rem; }
.sf-ok   { background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:10px;padding:0.9rem 1.1rem;color:#4ADE80;font-size:0.86rem;margin-bottom:1rem; }

/* ── Inputs ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea {
    background:#0E0E1A !important;border:1.5px solid #2D2D4E !important;
    border-radius:10px !important;color:#E8E8F0 !important;
    font-family:'Inter',sans-serif !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
    border-color:#6C63FF !important;box-shadow:0 0 0 3px rgba(108,99,255,0.12) !important;
}
.stTextInput>label,.stTextArea>label { color:#A0A0C0 !important;font-size:0.84rem !important;font-weight:600 !important; }

/* ── Buttons ── */
.stButton>button {
    background:linear-gradient(135deg,#6C63FF,#A78BFA) !important;
    color:white !important;border:none !important;border-radius:10px !important;
    font-weight:700 !important;font-family:'Inter',sans-serif !important;
    font-size:0.92rem !important;padding:0.65rem 1.75rem !important;transition:all 0.2s !important;
}
.stButton>button:hover { filter:brightness(1.1) !important;box-shadow:0 6px 20px rgba(108,99,255,0.3) !important;transform:translateY(-1px) !important; }
.stDownloadButton>button {
    background:linear-gradient(135deg,#22C55E,#16A34A) !important;
    color:white !important;border:none !important;border-radius:10px !important;
    font-weight:700 !important;font-size:0.92rem !important;
}
.stDownloadButton>button:hover { filter:brightness(1.08) !important;box-shadow:0 6px 20px rgba(34,197,94,0.3) !important; }

/* ── Selectbox ── */
.stSelectbox>div>div { background:#0E0E1A !important;border:1.5px solid #2D2D4E !important;border-radius:10px !important;color:#E8E8F0 !important; }

/* ── Checkbox ── */
.stCheckbox label { color:#E8E8F0 !important;font-size:0.88rem !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background:#1A1A2E !important;border-radius:10px;padding:0.25rem;border:1px solid #2D2D4E; }
.stTabs [data-baseweb="tab"] { color:#6B6B8A !important;border-radius:8px !important;font-weight:600 !important; }
.stTabs [aria-selected="true"] { background:#6C63FF !important;color:white !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:1.5rem !important; }

/* ── Multiselect ── */
.stMultiSelect>div>div { background:#0E0E1A !important;border:1.5px solid #2D2D4E !important;border-radius:10px !important; }
.stMultiSelect span[data-baseweb="tag"] { background:rgba(108,99,255,0.2) !important;color:#A78BFA !important;border-radius:6px !important; }

/* ── edit field label ── */
.ef-label { font-size:0.75rem;font-weight:700;color:#6B6B8A;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.2rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
PALETTE_GRADIENTS = {
    "Modern Blue":   "linear-gradient(135deg,#2563EB,#0EA5E9)",
    "Warm Orange":   "linear-gradient(135deg,#EA580C,#F97316)",
    "Forest Green":  "linear-gradient(135deg,#16A34A,#059669)",
    "Elegant Dark":  "linear-gradient(135deg,#7C3AED,#EC4899)",
    "Clean Minimal": "linear-gradient(135deg,#111827,#374151)",
}

TEMPLATE_META = {
    "clean":     {"icon":"🤍","desc":"Minimal, white, lots of whitespace","bg":"linear-gradient(135deg,#F8FAFC,#E2E8F0)"},
    "bold":      {"icon":"⚡","desc":"Dark background, large typography","bg":"linear-gradient(135deg,#0D0D1A,#1A0A2E)"},
    "warm":      {"icon":"🧡","desc":"Soft colors, rounded, friendly","bg":"linear-gradient(135deg,#FFF7ED,#FEE2E2)"},
    "corporate": {"icon":"🏢","desc":"Professional, structured layout","bg":"linear-gradient(135deg,#EFF6FF,#DBEAFE)"},
    "starter":   {"icon":"🚀","desc":"Simple, effective, fastest load","bg":"linear-gradient(135deg,#F0FDF4,#DCFCE7)"},
}

SECTION_OPTIONS = ["Hero","About","Services","Testimonials","Gallery","Contact Form","Map","FAQ"]
SECTION_ICONS   = {"Hero":"🏠","About":"👋","Services":"🛠","Testimonials":"💬","Gallery":"🖼","Contact Form":"📬","Map":"📍","FAQ":"❓"}
SECTION_DESCS   = {"Hero":"Big headline + CTA","About":"Your story & highlights","Services":"4 service cards","Testimonials":"3 client reviews","Gallery":"Photo showcase grid","Contact Form":"Name/email/message form","Map":"Location + Google Maps link","FAQ":"4 common questions"}

TONE_OPTIONS = ["Professional","Friendly","Bold","Minimal","Luxury"]
TONE_ICONS   = {"Professional":"👔","Friendly":"😊","Bold":"💥","Minimal":"◻","Luxury":"✨"}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def _init():
    defaults = dict(
        step=1,
        business_name="", description="", phone="", email="", address="",
        color_scheme="Modern Blue",
        sections=["Hero","About","Services","Contact Form"],
        tone="Professional",
        template="clean",
        content=None, html=None,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="sf-hero">
      <div style="max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
        <div style="display:flex;align-items:center;gap:0.85rem;">
          <div style="width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#6C63FF,#A78BFA);display:flex;align-items:center;justify-content:center;font-size:1.4rem;">⚡</div>
          <div>
            <div class="sf-logo-text">Site<span>Forge</span></div>
            <div class="sf-logo-sub">Small Business Website Generator</div>
          </div>
        </div>
        <div class="sf-badge">Powered by Ollama · llama3.2</div>
      </div>
    </div>""", unsafe_allow_html=True)


def render_progress(current: int):
    labels = ["About","Design","Sections","Generate","Download"]
    dots = ""
    for i, label in enumerate(labels, 1):
        if i < current:   cls = "done";   mark = "✓"
        elif i == current: cls = "active"; mark = str(i)
        else:              cls = "";       mark = str(i)
        dots += f"""<div class="sf-step">
          <div class="sf-step-dot {cls}">{mark}</div>
          <div class="sf-step-label {cls}">{label}</div>
        </div>"""
    st.markdown(f"""<div class="sf-prog"><div class="sf-prog-inner"><div class="sf-steps">{dots}</div></div></div>""",
                unsafe_allow_html=True)


def card_header(title: str, sub: str = ""):
    st.markdown(f'<div class="sf-card-title">{title}</div><div class="sf-card-sub">{sub}</div>', unsafe_allow_html=True)


def info(msg):  st.markdown(f'<div class="sf-info">{msg}</div>', unsafe_allow_html=True)
def warn(msg):  st.markdown(f'<div class="sf-warn">{msg}</div>', unsafe_allow_html=True)
def ok(msg):    st.markdown(f'<div class="sf-ok">{msg}</div>', unsafe_allow_html=True)


def mini_card(label, value):
    return f"""<div style="background:#1A1A2E;border:1px solid #2D2D4E;border-radius:12px;padding:1.1rem;">
      <div style="font-size:0.68rem;font-weight:700;color:#6B6B8A;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">{label}</div>
      <div style="font-size:0.95rem;font-weight:700;color:#E8E8F0;">{value}</div>
    </div>"""


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Business Info
# ─────────────────────────────────────────────────────────────────────────────
def step_1():
    card_header("Tell us about your business",
                "We'll use this to generate all website copy — headlines, descriptions, CTAs.")

    st.session_state.business_name = st.text_input(
        "Business Name *", value=st.session_state.business_name,
        placeholder="e.g. Maple Street Bakery")

    st.session_state.description = st.text_area(
        "What does your business do? *", value=st.session_state.description,
        placeholder="e.g. We bake artisan breads, pastries, and custom cakes using locally sourced ingredients.",
        height=90)

    st.markdown("**Contact Information** *(optional but recommended)*")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.phone = st.text_input("Phone", value=st.session_state.phone, placeholder="+1 (555) 123-4567")
        st.session_state.email = st.text_input("Email", value=st.session_state.email, placeholder="hello@yourbusiness.com")
    with c2:
        st.session_state.address = st.text_input("Address", value=st.session_state.address, placeholder="123 Main St, Toronto, ON")

    st.markdown("---")
    if not st.session_state.business_name or not st.session_state.description:
        warn("Please fill in your business name and a short description to continue.")
    else:
        info(f"Great! We'll generate a website for <strong>{st.session_state.business_name}</strong>.")
        _, _, col = st.columns([1, 3, 1])
        with col:
            if st.button("Continue →", key="s1_next"):
                st.session_state.step = 2
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — Design
# ─────────────────────────────────────────────────────────────────────────────
def step_2():
    card_header("Choose your design",
                "Pick a color palette, template layout, and tone that matches your brand.")

    # ── Palette ──
    st.markdown("#### 🎨 Color Palette")
    cols = st.columns(5)
    for i, (name, grad) in enumerate(PALETTE_GRADIENTS.items()):
        with cols[i]:
            sel = name == st.session_state.color_scheme
            border = "2px solid #6C63FF" if sel else "2px solid #2D2D4E"
            shadow = "box-shadow:0 0 0 3px rgba(108,99,255,0.2);" if sel else ""
            mark = "✓ " if sel else ""
            st.markdown(f"""
            <div style="border-radius:12px;overflow:hidden;border:{border};{shadow}">
              <div style="height:52px;background:{grad}"></div>
              <div style="background:#1A1A2E;padding:0.5rem;text-align:center;font-size:0.71rem;font-weight:600;color:#A0A0C0;">{mark}{name}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(name, key=f"p_{name}", use_container_width=True):
                st.session_state.color_scheme = name
                st.rerun()

    st.markdown("---")

    # ── Template ──
    st.markdown("#### 🖼 Template Style")
    tcols = st.columns(5)
    for i, tname in enumerate(TEMPLATE_NAMES):
        meta = TEMPLATE_META[tname]
        with tcols[i]:
            sel = tname == st.session_state.template
            border = "2px solid #6C63FF" if sel else "2px solid #2D2D4E"
            shadow = "box-shadow:0 0 0 3px rgba(108,99,255,0.2);" if sel else ""
            mark = "✓ " if sel else ""
            st.markdown(f"""
            <div style="border-radius:14px;overflow:hidden;border:{border};{shadow}background:#0E0E1A;">
              <div style="height:100px;background:{meta['bg']};display:flex;align-items:center;justify-content:center;font-size:2.5rem;">{meta['icon']}</div>
              <div style="padding:0.85rem;">
                <div style="font-size:0.88rem;font-weight:700;color:#E8E8F0;">{mark}{tname.capitalize()}</div>
                <div style="font-size:0.7rem;color:#6B6B8A;margin-top:0.2rem;">{meta['desc']}</div>
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Select {tname.capitalize()}", key=f"t_{tname}", use_container_width=True):
                st.session_state.template = tname
                st.rerun()

    st.markdown("---")

    # ── Tone ──
    st.markdown("#### 💬 Brand Tone")
    tonecols = st.columns(5)
    for i, tone in enumerate(TONE_OPTIONS):
        with tonecols[i]:
            sel = tone == st.session_state.tone
            border = "2px solid #6C63FF" if sel else "2px solid #2D2D4E"
            bg = "rgba(108,99,255,0.12)" if sel else "#1A1A2E"
            st.markdown(f"""
            <div style="border-radius:12px;padding:1rem;border:{border};background:{bg};text-align:center;">
              <div style="font-size:1.8rem;margin-bottom:0.3rem;">{TONE_ICONS.get(tone,'')}</div>
              <div style="font-size:0.85rem;font-weight:700;color:#E8E8F0;">{'✓ ' if sel else ''}{tone}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(tone, key=f"tone_{tone}", use_container_width=True):
                st.session_state.tone = tone
                st.rerun()

    st.markdown("---")
    ca, _, cc = st.columns([1, 3, 1])
    with ca:
        if st.button("← Back", key="s2_back"): st.session_state.step = 1; st.rerun()
    with cc:
        if st.button("Continue →", key="s2_next"): st.session_state.step = 3; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — Sections
# ─────────────────────────────────────────────────────────────────────────────
def step_3():
    card_header("Choose your sections",
                "Select which sections appear on your website. Tip: Hero + Services + Contact is a great combo.")

    selected = list(st.session_state.sections)
    cols = st.columns(4)
    for i, sec in enumerate(SECTION_OPTIONS):
        with cols[i % 4]:
            checked = sec in selected
            border = "2px solid #6C63FF" if checked else "2px solid #2D2D4E"
            bg = "rgba(108,99,255,0.08)" if checked else "#1A1A2E"
            mark = "✓" if checked else ""
            st.markdown(f"""
            <div style="border-radius:12px;padding:1rem;border:{border};background:{bg};margin-bottom:0.5rem;">
              <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
                <span style="font-size:1.1rem;">{SECTION_ICONS.get(sec,'')}</span>
                <span style="font-size:0.88rem;font-weight:700;color:#E8E8F0;">{sec}</span>
                <span style="margin-left:auto;color:#6C63FF;font-weight:700;">{mark}</span>
              </div>
              <div style="font-size:0.7rem;color:#6B6B8A;">{SECTION_DESCS.get(sec,'')}</div>
            </div>""", unsafe_allow_html=True)
            label = f"{'Remove' if checked else 'Add'} {sec}"
            if st.button(label, key=f"sec_{sec}", use_container_width=True):
                if checked: selected.remove(sec)
                else:       selected.append(sec)
                st.session_state.sections = selected
                st.rerun()

    st.markdown("---")
    if not selected:
        warn("Select at least one section.")
    else:
        info(f"Selected: <strong>{', '.join(selected)}</strong> — {len(selected)} section(s)")

    ca, _, cc = st.columns([1, 3, 1])
    with ca:
        if st.button("← Back", key="s3_back"): st.session_state.step = 2; st.rerun()
    with cc:
        if selected:
            if st.button("Generate Website →", key="s3_next"): st.session_state.step = 4; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — Generate
# ─────────────────────────────────────────────────────────────────────────────
def step_4():
    card_header("Generating your website",
                "The AI is crafting personalized content for every section. Usually takes 20-40 seconds.")

    if st.session_state.content is not None:
        st.session_state.step = 5
        st.rerun()
        return

    if not ollama_is_available():
        st.error("**Ollama is not running.**\n\nStart it: `ollama serve`\nThen pull the model: `ollama pull llama3.2`")
        if st.button("← Back"): st.session_state.step = 3; st.rerun()
        return

    biz = dict(
        name=st.session_state.business_name,
        description=st.session_state.description,
        phone=st.session_state.phone,
        email=st.session_state.email,
        address=st.session_state.address,
        color_scheme=st.session_state.color_scheme,
        sections=st.session_state.sections,
        tone=st.session_state.tone,
    )

    prog  = st.progress(0, text="Connecting to Ollama...")
    status = st.empty()
    try:
        status.markdown("*AI is writing your headlines, descriptions, testimonials, FAQ...*")
        prog.progress(20, text="AI is generating content...")
        content = generate_website_content(biz)
        prog.progress(65, text="Rendering your template...")
        status.markdown("*Rendering the HTML template...*")
        html = render_site(st.session_state.template, content)
        prog.progress(95, text="Almost done...")
        time.sleep(0.3)
        st.session_state.content = content
        st.session_state.html    = html
        prog.progress(100, text="Done!")
        time.sleep(0.3)
        prog.empty(); status.empty()
        st.session_state.step = 5
        st.rerun()
    except RuntimeError as e:
        prog.empty()
        st.error(str(e))
        if st.button("← Back"): st.session_state.step = 3; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Preview / Edit / Download
# ─────────────────────────────────────────────────────────────────────────────
def step_5():
    content = st.session_state.content
    html    = st.session_state.html

    tab_prev, tab_edit, tab_dl = st.tabs(["Live Preview", "Edit Content", "Download & Deploy"])

    # ── PREVIEW ──────────────────────────────────────────────────────────────
    with tab_prev:
        ca, cb = st.columns(2)
        with ca:
            new_tmpl = st.selectbox("Switch Template", TEMPLATE_NAMES,
                                    index=TEMPLATE_NAMES.index(st.session_state.template))
        with cb:
            new_pal = st.selectbox("Switch Palette", list(PALETTES.keys()),
                                   index=list(PALETTES.keys()).index(st.session_state.color_scheme))
        if new_tmpl != st.session_state.template or new_pal != st.session_state.color_scheme:
            st.session_state.template = new_tmpl
            st.session_state.color_scheme = new_pal
            st.session_state.content["color_scheme"] = new_pal
            st.session_state.html = render_site(new_tmpl, st.session_state.content)
            st.rerun()

        # Browser chrome mockup
        st.markdown("""
        <div style="background:#1A1A2E;border:1px solid #2D2D4E;border-radius:16px 16px 0 0;padding:0.7rem 1rem;display:flex;align-items:center;gap:0.5rem;margin-top:1rem;">
          <div style="width:12px;height:12px;border-radius:50%;background:#FF5F57;"></div>
          <div style="width:12px;height:12px;border-radius:50%;background:#FEBC2E;"></div>
          <div style="width:12px;height:12px;border-radius:50%;background:#28C840;"></div>
          <div style="flex:1;margin:0 1rem;background:#0E0E1A;border-radius:6px;padding:0.25rem 0.75rem;font-size:0.7rem;color:#4A4A6A;">your-business.com</div>
        </div>""", unsafe_allow_html=True)

        encoded = base64.b64encode(html.encode("utf-8")).decode("utf-8")
        st.components.v1.html(
            f'<iframe src="data:text/html;base64,{encoded}" style="width:100%;height:720px;border:none;border-radius:0 0 14px 14px;background:#fff;" sandbox="allow-scripts allow-same-origin"></iframe>',
            height=722, scrolling=False,
        )

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Regenerate Content", key="regen"):
                st.session_state.content = None
                st.session_state.html = None
                st.session_state.step = 4
                st.rerun()
        with c2:
            if st.button("← Start Over", key="restart"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

    # ── EDIT ─────────────────────────────────────────────────────────────────
    with tab_edit:
        card_header("Edit your content",
                    "Tweak anything before downloading. Click 'Apply' to refresh the preview.")
        if not content:
            st.warning("No content generated yet.")
            return

        c = dict(content)

        def ef(label, key, multi=False):
            st.markdown(f'<div class="ef-label">{label}</div>', unsafe_allow_html=True)
            if multi:
                return st.text_area(label, value=c.get(key,""), key=f"e_{key}",
                                    label_visibility="collapsed", height=85)
            return st.text_input(label, value=c.get(key,""), key=f"e_{key}",
                                 label_visibility="collapsed")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Hero**")
            c["hero_headline"]    = ef("Hero Headline", "hero_headline")
            c["hero_subheadline"] = ef("Subheadline", "hero_subheadline")
            c["hero_cta"]         = ef("CTA Button", "hero_cta")
            st.markdown("**About**")
            c["about_headline"]   = ef("Headline", "about_headline")
            c["about_paragraph"]  = ef("Paragraph", "about_paragraph", multi=True)
            c["about_highlight_1"]= ef("Highlight 1", "about_highlight_1")
            c["about_highlight_2"]= ef("Highlight 2", "about_highlight_2")
            c["about_highlight_3"]= ef("Highlight 3", "about_highlight_3")
            st.markdown("**Services**")
            c["services_headline"]    = ef("Services Headline", "services_headline")
            c["services_subheadline"] = ef("Services Subheadline", "services_subheadline")
            for n in range(1,5):
                c[f"service_{n}_name"]        = ef(f"Service {n} Name", f"service_{n}_name")
                c[f"service_{n}_description"] = ef(f"Service {n} Description", f"service_{n}_description", multi=True)

        with col2:
            st.markdown("**Testimonials**")
            c["testimonials_headline"] = ef("Headline", "testimonials_headline")
            for n in range(1,4):
                c[f"testimonial_{n}_text"] = ef(f"Testimonial {n}", f"testimonial_{n}_text", multi=True)
                c[f"testimonial_{n}_name"] = ef(f"Name {n}", f"testimonial_{n}_name")
                c[f"testimonial_{n}_role"] = ef(f"Role {n}", f"testimonial_{n}_role")
            st.markdown("**FAQ**")
            c["faq_headline"] = ef("FAQ Headline", "faq_headline")
            for n in range(1,5):
                c[f"faq_{n}_q"] = ef(f"Q{n}", f"faq_{n}_q")
                c[f"faq_{n}_a"] = ef(f"A{n}", f"faq_{n}_a", multi=True)
            st.markdown("**Footer / SEO**")
            c["contact_headline"]    = ef("Contact Headline", "contact_headline")
            c["contact_subheadline"] = ef("Contact Subheadline", "contact_subheadline")
            c["footer_tagline"]      = ef("Footer Tagline", "footer_tagline")
            c["meta_description"]    = ef("SEO Meta Description", "meta_description")

        st.markdown("---")
        if st.button("Apply Changes & Refresh Preview", key="apply"):
            st.session_state.content = c
            st.session_state.html = render_site(st.session_state.template, c)
            ok("Changes applied! Switch to Live Preview to see them.")
            st.rerun()

    # ── DOWNLOAD ─────────────────────────────────────────────────────────────
    with tab_dl:
        card_header("Download & Deploy",
                    "Your website is ready. Download the files and go live in minutes.")

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(mini_card("Business", st.session_state.business_name), unsafe_allow_html=True)
        with c2: st.markdown(mini_card("Template", f"{st.session_state.template.capitalize()} · {st.session_state.color_scheme}"), unsafe_allow_html=True)
        with c3: st.markdown(mini_card("Sections", f"{len(st.session_state.sections)} included"), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Download")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "Download index.html (all-in-one)",
                data=st.session_state.html.encode("utf-8"),
                file_name="index.html", mime="text/html",
                use_container_width=True,
            )
            st.caption("All styles and scripts embedded in one file — just open in a browser.")
        with d2:
            zip_data = build_zip(st.session_state.html, st.session_state.business_name)
            slug = st.session_state.business_name.lower().replace(" ","-")
            st.download_button(
                "Download ZIP (index.html + style.css + script.js)",
                data=zip_data,
                file_name=f"{slug}-website.zip",
                mime="application/zip",
                use_container_width=True,
            )
            st.caption("Separated files + a `deploy.sh` script for GitHub Pages.")

        st.markdown("---")
        st.markdown("#### Deploy to GitHub Pages (free hosting)")
        st.markdown("""
<div style="background:#1A1A2E;border:1px solid #2D2D4E;border-radius:14px;padding:1.75rem;">
  <div style="font-size:0.92rem;font-weight:700;color:#E8E8F0;margin-bottom:1rem;">Three steps to go live:</div>
  <ol style="color:#A0A0C0;font-size:0.86rem;line-height:2.2;padding-left:1.25rem;">
    <li>Download the ZIP above and extract it to a folder</li>
    <li>Install the GitHub CLI if needed: <code style="background:#0E0E1A;padding:0.1rem 0.5rem;border-radius:4px;color:#A78BFA;">brew install gh &amp;&amp; gh auth login</code></li>
    <li>Run the deploy script: <code style="background:#0E0E1A;padding:0.1rem 0.5rem;border-radius:4px;color:#4ADE80;">bash deploy.sh your-github-username</code></li>
  </ol>
  <div style="margin-top:1rem;font-size:0.8rem;color:#6B6B8A;">
    Your site will be live at <strong style="color:#6C63FF;">https://your-username.github.io/your-business-website</strong> — forever, for free.
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Build Another Website", key="another"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    render_header()
    render_progress(st.session_state.step)
    _, center, _ = st.columns([0.3, 10, 0.3])
    with center:
        step = st.session_state.step
        if   step == 1: step_1()
        elif step == 2: step_2()
        elif step == 3: step_3()
        elif step == 4: step_4()
        elif step == 5: step_5()

if __name__ == "__main__":
    main()
