# SiteForge — Small Business Website Generator

Answer 5-6 questions → AI generates a complete, responsive website → preview it live → download and deploy.

## Setup

```bash
cd ~/site-generator
pip install -r requirements.txt
```

Pull the AI model (one-time):

```bash
ollama pull llama3.2
ollama serve          # keep this running in a terminal
```

Run the app:

```bash
streamlit run app.py
```

## What You Get

- **5-step wizard** — business info, design, sections, AI generation, download
- **5 templates** — Clean, Bold, Warm, Corporate, Starter
- **5 color palettes** — Modern Blue, Warm Orange, Forest Green, Elegant Dark, Clean Minimal
- **8 optional sections** — Hero, About, Services, Testimonials, Gallery, Contact Form, Map, FAQ
- **AI-generated copy** — headlines, taglines, descriptions, testimonials, FAQ answers
- **Live preview** — rendered in an iframe inside the app
- **Edit mode** — tweak any text before downloading
- **ZIP download** — index.html + style.css + script.js + deploy.sh
- **GitHub Pages deploy script** — go live for free in minutes

## File Structure

```
site-generator/
├── app.py                  Main Streamlit app
├── core/
│   ├── content_gen.py      AI content via Ollama (llama3.2)
│   ├── renderer.py         Jinja2 template rendering + palettes
│   └── exporter.py         ZIP builder + deploy script
├── templates/
│   ├── clean.html
│   ├── bold.html
│   ├── warm.html
│   ├── corporate.html
│   └── starter.html
├── .streamlit/
│   └── config.toml         Dark theme
└── requirements.txt
```

## Tech Stack

- **Streamlit** — UI framework
- **Ollama (llama3.2)** — Local AI, no API key needed
- **Jinja2** — HTML templating
- **Python stdlib** — zipfile, base64, requests

## Generated Site Features

- Google Fonts (Inter / Poppins)
- Smooth scroll navigation
- Mobile-first responsive layout
- Fade-in animations on scroll
- Working contact form (mailto:)
- SEO meta tags
- GitHub Pages deploy script
