# SiteForge — AI-Powered Website Generator

Generate professional, responsive websites in minutes using AI. Answer a few questions about your business, pick a template and color palette, and SiteForge builds a complete single-page website you can download and deploy.

## Features

- **5 Professional Templates** — Clean, Bold, Warm, Corporate, Starter
- **5 Color Palettes** — Modern Blue, Warm Orange, Forest Green, Elegant Dark, Clean Minimal
- **AI Content Generation** — Ollama generates all website copy (headlines, services, testimonials, FAQs)
- **Live Preview** — See your website rendered in real-time before downloading
- **One-Click Export** — Download as ZIP with `index.html`, `style.css`, `script.js`, and a GitHub Pages deploy script
- **100% Local** — No API keys, no cloud, everything runs on your machine

## Quick Start

```bash
# 1. Install Ollama (https://ollama.com)
ollama pull llama3.2

# 2. Clone and install
git clone https://github.com/Naitya07/site-generator.git
cd site-generator
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

## Tech Stack

- **Frontend:** Streamlit with custom dark theme
- **AI:** Ollama (llama3.2) for content generation
- **Templating:** Jinja2 with responsive HTML/CSS/JS
- **Export:** ZIP packaging with CSS/JS extraction

## How It Works

1. **Business Info** — Enter your business name, description, services, and contact details
2. **Choose Template** — Pick from 5 professionally designed responsive templates
3. **Choose Palette** — Select a color scheme that matches your brand
4. **AI Generation** — Ollama generates all website content based on your inputs
5. **Preview & Download** — Review the live preview, then download as a ready-to-deploy ZIP
