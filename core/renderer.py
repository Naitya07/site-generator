"""
SiteForge — Jinja2 Template Renderer
Loads a named template and renders it with the generated content dict.
"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

# Palette definitions: each has primary, secondary, accent, background, surface, text
PALETTES = {
    "Modern Blue": {
        "primary": "#2563EB",
        "primary_dark": "#1D4ED8",
        "secondary": "#0EA5E9",
        "accent": "#F59E0B",
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "text": "#1E293B",
        "text_muted": "#64748B",
        "border": "#E2E8F0",
        "gradient_start": "#2563EB",
        "gradient_end": "#0EA5E9",
        "hero_text": "#FFFFFF",
        "nav_bg": "rgba(255,255,255,0.95)",
        "nav_text": "#1E293B",
        "footer_bg": "#1E293B",
        "footer_text": "#CBD5E1",
    },
    "Warm Orange": {
        "primary": "#EA580C",
        "primary_dark": "#C2410C",
        "secondary": "#F97316",
        "accent": "#FCD34D",
        "background": "#FFFBF5",
        "surface": "#FFFFFF",
        "text": "#292524",
        "text_muted": "#78716C",
        "border": "#FDE8D8",
        "gradient_start": "#EA580C",
        "gradient_end": "#F97316",
        "hero_text": "#FFFFFF",
        "nav_bg": "rgba(255,251,245,0.95)",
        "nav_text": "#292524",
        "footer_bg": "#292524",
        "footer_text": "#D6D3D1",
    },
    "Forest Green": {
        "primary": "#16A34A",
        "primary_dark": "#15803D",
        "secondary": "#059669",
        "accent": "#84CC16",
        "background": "#F0FDF4",
        "surface": "#FFFFFF",
        "text": "#14532D",
        "text_muted": "#4B7C59",
        "border": "#DCFCE7",
        "gradient_start": "#16A34A",
        "gradient_end": "#059669",
        "hero_text": "#FFFFFF",
        "nav_bg": "rgba(240,253,244,0.95)",
        "nav_text": "#14532D",
        "footer_bg": "#14532D",
        "footer_text": "#BBF7D0",
    },
    "Elegant Dark": {
        "primary": "#8B5CF6",
        "primary_dark": "#7C3AED",
        "secondary": "#A78BFA",
        "accent": "#F472B6",
        "background": "#0F0F1A",
        "surface": "#1A1A2E",
        "text": "#F1F0FB",
        "text_muted": "#A0A0C0",
        "border": "#2D2D4E",
        "gradient_start": "#7C3AED",
        "gradient_end": "#EC4899",
        "hero_text": "#FFFFFF",
        "nav_bg": "rgba(15,15,26,0.95)",
        "nav_text": "#F1F0FB",
        "footer_bg": "#07070F",
        "footer_text": "#A0A0C0",
    },
    "Clean Minimal": {
        "primary": "#111827",
        "primary_dark": "#030712",
        "secondary": "#374151",
        "accent": "#6B7280",
        "background": "#FFFFFF",
        "surface": "#F9FAFB",
        "text": "#111827",
        "text_muted": "#6B7280",
        "border": "#E5E7EB",
        "gradient_start": "#111827",
        "gradient_end": "#374151",
        "hero_text": "#FFFFFF",
        "nav_bg": "rgba(255,255,255,0.97)",
        "nav_text": "#111827",
        "footer_bg": "#111827",
        "footer_text": "#9CA3AF",
    },
}

TEMPLATE_NAMES = ["clean", "bold", "warm", "corporate", "starter"]
TEMPLATE_DISPLAY = {
    "clean": "Clean",
    "bold": "Bold",
    "warm": "Warm",
    "corporate": "Corporate",
    "starter": "Starter",
}


def get_palette(scheme_name: str) -> dict:
    return PALETTES.get(scheme_name, PALETTES["Modern Blue"])


def render_site(template_name: str, content: dict) -> str:
    """
    Render the named Jinja2 template with the given content dict.
    Returns the full HTML string.
    """
    env = Environment(
        loader=FileSystemLoader(os.path.abspath(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template(f"{template_name}.html")
    palette = get_palette(content.get("color_scheme", "Modern Blue"))
    sections = content.get("sections", [])

    ctx = {**content, "palette": palette, "sections": sections}
    return template.render(**ctx)
