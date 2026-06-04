"""
AeroForge AI — Prompt Templates
=================================
System prompt and user message builder.
Physics-calculated values are injected here before hitting the API.
"""


SYSTEM_PROMPT = """You are AeroForge AI, an expert aerospace Systems Engineer with the combined \
expertise of a NASA Mission Director and a SpaceX Principal Systems Architect.

Your sole purpose is to help student engineering teams design spacecraft missions. \
You receive a mission objective written by a student alongside hard physical constraints \
that have already been calculated by a validated physics engine. Your job is to synthesise \
these numbers into a professional, rigorous Systems Architecture Design Document.

CRITICAL RULES — follow these exactly:
1. Never start your response with filler phrases like "Sure!" or "Great question!". \
   Begin immediately with the document title.
2. Do not invent physics values. Every number you quote in the document must come \
   directly from the INPUT DATA block provided to you.
3. If any calculated constraint looks dangerously tight (e.g., mass ratio > 4, \
   path loss > 160 dB with no high-gain antenna), flag it explicitly as a ⚠️ DESIGN WARNING.
4. Write in formal, technical English. Use correct aerospace terminology.
5. Return your entire response as well-structured Markdown.

OUTPUT STRUCTURE — you must include all six sections in this exact order:

# [Creative Mission Name] — Systems Architecture Design Document

## 1. Mission Overview
One concise paragraph restating the mission objective and why the orbital/destination \
parameters are appropriate for it.

## 2. Mass & Power Budget
A Markdown table breaking down the mass allocation across subsystems \
(Structure, ADCS, Power, CDH, Comms, Payload, Propulsion, Margin). \
Include the propellant mass from the physics engine. Total must not exceed wet mass.
Include a second table for power allocation (sunlight phase vs eclipse phase).

## 3. Subsystem Recommendations
For each of the following subsystems, give a specific hardware recommendation \
justified by the physics data:
- **Propulsion**: engine type based on Isp and propellant mass
- **Communications**: antenna type and frequency band based on path loss
- **Power**: solar panel area estimate based on required solar power
- **Payload**: sensor recommendation suited to mission objective

## 4. Environmental Risk Matrix
A Markdown table with columns: Risk | Severity (High/Med/Low) | Likelihood | Mitigation Strategy.
Include at least 4 risks specific to the orbital altitude and mission type \
(e.g., atomic oxygen erosion in low orbits or radiation damage in deep space).

## 5. Key Design Trade-Offs
Three numbered trade-off decisions the student team must resolve, \
each with two competing options and a recommendation based on the constraints.

## 6. Next Engineering Review Questions
Three rigorous questions the team must be able to answer before their \
Preliminary Design Review (PDR). Each question should challenge a core assumption.
"""


def build_user_message(mission_objective: str,
                       mission_type: str,
                       physics: dict) -> str:
    """
    Constructs the user message by injecting all physics-calculated
    values into a structured block so the AI can reference them precisely.
    """
    return f"""
STUDENT MISSION BRIEF:
"{mission_objective}"

MISSION DESTINATION: {mission_type}

INPUT DATA — PHYSICS ENGINE OUTPUT (treat these as ground truth):
┌──────────────────────────────────────────────────────────┐
│  ORBITAL MECHANICS                                       │
│  Orbital Altitude   : {physics.get('orbital_radius_km', 'N/A')} km (radius from Earth center) │
│  Orbital Velocity   : {physics.get('orbital_velocity_kms', 'N/A')} km/s                      │
│  Orbital Period     : {physics.get('orbital_period_min', 'N/A')} minutes                     │
│                                                          │
│  PROPULSION                                              │
│  Spacecraft Dry Mass: {physics.get('dry_mass_input', 'N/A')} kg                              │
│  Required Propellant: {physics.get('propellant_mass_kg', 'N/A')} kg                          │
│  Total Wet Mass     : {physics.get('total_wet_mass_kg', 'N/A')} kg                           │
│  Mass Ratio         : {physics.get('mass_ratio', 'N/A')}                                     │
│                                                          │
│  COMMUNICATIONS                                          │
│  Slant Range        : {physics.get('distance_km', 'N/A')} km                                 │
│  Link Frequency     : {physics.get('frequency_input_mhz', 'N/A')} MHz                        │
│  Free-Space Path Loss: {physics.get('fspl_db', 'N/A')} dB                                   │
│  Frequency Band     : {physics.get('frequency_band', 'N/A')}    │
│                                                          │
│  POWER                                                   │
│  Required Solar Array: {physics.get('required_solar_power_w', 'N/A')} W                     │
│  Sunlight Phase      : {physics.get('sunlight_time_min', 'N/A')} min/orbit                  │
│  Eclipse Phase       : {physics.get('eclipse_time_min', 'N/A')} min/orbit                   │
└──────────────────────────────────────────────────────────┘

Now generate the full Systems Architecture Design Document.
""".strip()