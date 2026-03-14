"""
SiteForge — AI Content Generation via Ollama (llama3.2)
Generates all website copy: headlines, taglines, service descriptions, etc.
"""

import json
import re
import requests
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


def _call_ollama(prompt: str, timeout: int = 90) -> str:
    """Send a prompt to Ollama and return the full response text."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.75,
            "top_p": 0.9,
            "num_predict": 1200,
        },
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure it is running: `ollama serve`"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama took too long to respond. Try again.")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of an LLM response string."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find JSON block between ```json ... ``` or first { ... }
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return {}


def generate_website_content(business_info: dict) -> dict:
    """
    Given a dict of business info from the questionnaire, ask the LLM to
    produce all website copy and return it as a structured dict.

    business_info keys:
        name, description, phone, email, address,
        tone, sections (list), color_scheme
    """
    sections = business_info.get("sections", [])
    name = business_info.get("name", "My Business")
    description = business_info.get("description", "")
    tone = business_info.get("tone", "Professional")

    sections_str = ", ".join(sections) if sections else "Hero, About, Services, Contact"

    prompt = f"""You are an expert copywriter creating website content for a small business.

Business details:
- Name: {name}
- What they do: {description}
- Tone/vibe: {tone}
- Sections needed: {sections_str}
- Phone: {business_info.get("phone", "")}
- Email: {business_info.get("email", "")}
- Address: {business_info.get("address", "")}

Generate compelling, {tone.lower()} website copy. Return ONLY a valid JSON object (no extra text) with exactly these keys:

{{
  "hero_headline": "Short punchy headline (max 8 words)",
  "hero_subheadline": "One sentence value proposition (max 20 words)",
  "hero_cta": "Call-to-action button text (max 4 words)",
  "about_headline": "Section headline for About (max 6 words)",
  "about_paragraph": "2-3 sentences about the business, warm and credible",
  "about_highlight_1": "Short highlight point (max 6 words)",
  "about_highlight_2": "Short highlight point (max 6 words)",
  "about_highlight_3": "Short highlight point (max 6 words)",
  "services_headline": "Section headline for Services (max 6 words)",
  "services_subheadline": "One sentence intro to services (max 15 words)",
  "service_1_name": "Service name",
  "service_1_description": "2 sentence service description",
  "service_2_name": "Service name",
  "service_2_description": "2 sentence service description",
  "service_3_name": "Service name",
  "service_3_description": "2 sentence service description",
  "service_4_name": "Service name",
  "service_4_description": "2 sentence service description",
  "testimonials_headline": "Section headline for testimonials (max 6 words)",
  "testimonial_1_text": "Realistic customer testimonial (2-3 sentences)",
  "testimonial_1_name": "Customer full name",
  "testimonial_1_role": "Customer job title or type",
  "testimonial_2_text": "Realistic customer testimonial (2-3 sentences)",
  "testimonial_2_name": "Customer full name",
  "testimonial_2_role": "Customer job title or type",
  "testimonial_3_text": "Realistic customer testimonial (2-3 sentences)",
  "testimonial_3_name": "Customer full name",
  "testimonial_3_role": "Customer job title or type",
  "faq_headline": "Section headline for FAQ (max 6 words)",
  "faq_1_q": "Common question",
  "faq_1_a": "Clear answer (2-3 sentences)",
  "faq_2_q": "Common question",
  "faq_2_a": "Clear answer (2-3 sentences)",
  "faq_3_q": "Common question",
  "faq_3_a": "Clear answer (2-3 sentences)",
  "faq_4_q": "Common question",
  "faq_4_a": "Clear answer (2-3 sentences)",
  "contact_headline": "Section headline for Contact (max 5 words)",
  "contact_subheadline": "Inviting one-liner to get in touch (max 15 words)",
  "footer_tagline": "Short memorable brand tagline (max 8 words)",
  "meta_description": "SEO meta description (max 155 chars)"
}}

Return ONLY the JSON. No markdown, no explanation."""

    raw = _call_ollama(prompt)
    content = _extract_json(raw)

    # Merge with defaults so the templates never get KeyError
    defaults = _default_content(name, description, business_info)
    merged = {**defaults, **content}
    # Always inject the raw business info so templates can access it
    merged["business_name"] = name
    merged["phone"] = business_info.get("phone", "")
    merged["email"] = business_info.get("email", "")
    merged["address"] = business_info.get("address", "")
    merged["sections"] = sections
    merged["tone"] = tone
    merged["color_scheme"] = business_info.get("color_scheme", "Modern Blue")
    return merged


def _default_content(name: str, description: str, info: dict) -> dict:
    """Fallback content in case the LLM fails or returns partial JSON."""
    return {
        "hero_headline": f"Welcome to {name}",
        "hero_subheadline": description or "We deliver exceptional results for every client.",
        "hero_cta": "Get Started",
        "about_headline": "Who We Are",
        "about_paragraph": (
            f"{name} is dedicated to providing outstanding service to our community. "
            "With years of experience, we bring expertise and passion to everything we do. "
            "Our team is committed to your satisfaction."
        ),
        "about_highlight_1": "Trusted by hundreds",
        "about_highlight_2": "Expert team",
        "about_highlight_3": "Results guaranteed",
        "services_headline": "What We Offer",
        "services_subheadline": "Comprehensive solutions tailored to your needs.",
        "service_1_name": "Consultation",
        "service_1_description": "Expert guidance to help you make the best decisions. We listen, analyze, and advise.",
        "service_2_name": "Planning",
        "service_2_description": "Detailed planning to set your project up for success. We cover every detail.",
        "service_3_name": "Execution",
        "service_3_description": "Flawless delivery of every project. We take pride in our craft.",
        "service_4_name": "Support",
        "service_4_description": "Ongoing support to keep things running smoothly. We're here for you.",
        "testimonials_headline": "What Our Clients Say",
        "testimonial_1_text": "Working with this team was an absolute pleasure. They exceeded my expectations at every turn.",
        "testimonial_1_name": "Sarah Johnson",
        "testimonial_1_role": "Small Business Owner",
        "testimonial_2_text": "Professional, reliable, and incredibly skilled. I would recommend them to anyone.",
        "testimonial_2_name": "Mark Davis",
        "testimonial_2_role": "Entrepreneur",
        "testimonial_3_text": "The results speak for themselves. My business has grown significantly since working with them.",
        "testimonial_3_name": "Lisa Chen",
        "testimonial_3_role": "Startup Founder",
        "faq_headline": "Frequently Asked Questions",
        "faq_1_q": "How do I get started?",
        "faq_1_a": "Getting started is simple. Reach out via our contact form or give us a call. We'll schedule a free consultation.",
        "faq_2_q": "What is your pricing?",
        "faq_2_a": "Our pricing is transparent and competitive. We offer packages to fit every budget — contact us for a custom quote.",
        "faq_3_q": "How long does a project take?",
        "faq_3_a": "Project timelines vary depending on scope. Most projects are completed within 2-4 weeks.",
        "faq_4_q": "Do you offer guarantees?",
        "faq_4_a": "Absolutely. Your satisfaction is our priority and we stand behind every project we deliver.",
        "contact_headline": "Let's Work Together",
        "contact_subheadline": "Ready to get started? Reach out and we'll respond within 24 hours.",
        "footer_tagline": f"{name} — Excellence in everything we do.",
        "meta_description": f"{name}: {description or 'Professional services for your business needs.'}",
        "business_name": name,
        "phone": info.get("phone", ""),
        "email": info.get("email", ""),
        "address": info.get("address", ""),
        "sections": info.get("sections", ["Hero", "About", "Services", "Contact Form"]),
        "tone": info.get("tone", "Professional"),
        "color_scheme": info.get("color_scheme", "Modern Blue"),
    }


def ollama_is_available() -> bool:
    """Quick health check — returns True if Ollama is reachable."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False
