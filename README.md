# 🚀 AeroForge AI — Mission Design Co-Pilot

AeroForge AI is an open-source spacecraft systems engineering tool built for student aerospace teams. Enter a mission objective, set your hardware parameters, and instantly receive a professional Systems Architecture Design Document backed by real aerospace physics.

---

## Features

- 8 validated aerospace physics equations running in the background
- AI-generated systems architecture reports tailored to your exact constraints
- Real-time design warnings for dangerous mass ratios, path loss, radiation, and orbital decay
- Download your mission report as a Markdown file
- Clean dashboard UI with live metric display

---

## Physics Engine

| Module | Output |
|--------|--------|
| Orbital Mechanics (Kepler's Laws) | Velocity & orbital period |
| Propulsion (Tsiolkovsky Rocket Equation) | Propellant mass & mass ratio |
| Communications (Free-Space Path Loss) | Signal loss in dB |
| Power (Eclipse-aware solar sizing) | Required solar array wattage |
| Atmospheric Drag | Orbital lifetime in days |
| Ground Coverage | Daily contact minutes |
| Radiation (AP8/AE8 model) | Total ionizing dose in krad |
| Thermal (Stefan-Boltzmann) | Temperature extremes & swing |

---

## Project Structure

```
aeroforge-ai/
├── app.py            ← Streamlit web application
├── physics.py        ← Aerospace physics engine
├── prompts.py        ← AI prompt architecture
├── requirements.txt  ← Dependencies
└── .streamlit/
    └── secrets.toml  ← API key (not committed to GitHub)
```

---

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/aeroforge-ai.git
cd aeroforge-ai
pip install -r requirements.txt
streamlit run app.py
```

---

> **Disclaimer:** Outputs are educational. Always verify with a licensed engineer before hardware procurement.