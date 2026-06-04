# 🚀 AeroForge AI — Mission Design Co-Pilot

An open-source, AI-powered spacecraft systems engineering tool for student teams.
AeroForge AI combines a **validated aerospace physics engine** with **Claude** to instantly generate professional Systems Architecture Design Documents from a plain-English mission brief.

---

## What It Does

1. **Student inputs** a mission objective and sets hardware sliders in the sidebar.
2. **Physics Engine** calculates 8 hard constraints using real aerospace equations:
   - Orbital velocity & period (Kepler's Laws)
   - Required propellant mass (Tsiolkovsky Rocket Equation)
   - Communications path loss (Free-Space Path Loss)
   - Required solar array power (Eclipse-aware sizing)
   - Orbital lifetime (Atmospheric Drag Model)
   - Ground station contact time (Coverage geometry)
   - Radiation dose (AP8/AE8 trapped belt model)
   - Thermal swing (Stefan-Boltzmann radiative balance)
3. **Claude** receives those exact numbers via a strict system prompt and writes a full Systems Architecture Document covering mass budgets, subsystem recommendations, a risk matrix, and design trade-offs.

---

## System Architecture