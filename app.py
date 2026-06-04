"""
AeroForge AI — Main Streamlit Application
==========================================
Run locally:  streamlit run app.py
Deploy:       Push to GitHub → connect to Streamlit Community Cloud
              Add ANTHROPIC_API_KEY in the Streamlit secrets manager.
"""

import streamlit as st
import anthropic

from physics import (
    calculate_orbital_mechanics,
    calculate_propellant_mass,
    calculate_fspl,
    calculate_solar_power,
    calculate_atmospheric_drag,
    calculate_ground_coverage,
    calculate_radiation_dose,
    calculate_thermal,
)
from prompts import SYSTEM_PROMPT, build_user_message

st.set_page_config(
    page_title="AeroForge AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
    div.stButton > button[kind="primary"] {
        background-color: #0d6efd;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("AeroForge AI")
    st.caption("AI-Powered Spacecraft Design Co-Pilot")
    st.divider()

    st.header("🛠️ Spacecraft Specifications")

    mission_type = st.selectbox(
        "Mission Destination",
        ["Low Earth Orbit (LEO)", "Lunar Orbit", "Mars Surface Lander"],
    )

    st.subheader("Orbital Parameters")
    altitude_km = st.slider("Target Orbital Altitude (km)", 200, 2000, 500, step=50)
    inclination_deg = st.slider("Orbit Inclination (°)", 0, 98, 51,
        help="ISS orbit = 51.6°. Sun-synchronous = ~98°. Equatorial = 0°.")

    st.subheader("Propulsion")
    dry_mass_kg = st.number_input("Spacecraft Dry Mass (kg)", min_value=1.0, max_value=5000.0, value=10.0, step=1.0)
    delta_v_ms  = st.number_input("Required ΔV (m/s)", min_value=0.0, max_value=10000.0, value=200.0, step=10.0)
    isp_seconds = st.slider("Engine Specific Impulse — Isp (s)", 50, 450, 220,
        help="Cold gas ≈ 70s, biprop ≈ 300s.")

    st.subheader("Communications")
    frequency_mhz = st.select_slider("Downlink Frequency (MHz)",
        options=[137, 401, 437, 2200, 2400, 8025, 8400], value=2200)

    st.subheader("Power Budget")
    power_sun_w     = st.number_input("Average Power Draw — Sunlight (W)", min_value=1.0, max_value=1000.0, value=15.0, step=1.0)
    power_eclipse_w = st.number_input("Average Power Draw — Eclipse (W)",  min_value=1.0, max_value=1000.0, value=10.0, step=1.0)

    st.subheader("Mission Profile")
    mission_duration_days = st.number_input("Mission Duration (days)", min_value=30, max_value=3650, value=365, step=30)

    st.divider()
    st.caption("AeroForge AI v1.0 · Open-source student engineering tool")

st.title("🚀 AeroForge AI: Mission Design Co-Pilot")
st.write(
    "Describe your mission. The physics engine calculates 8 aerospace constraints — "
    "then Claude writes your full Systems Architecture Document."
)

mission_objective = st.text_area(
    "Mission Objective",
    value="A 3U CubeSat equipped with a thermal infrared camera to monitor wildfire progression across California's national forests.",
    height=100,
)

generate_clicked = st.button("⚙️ Generate Mission Architecture Blueprint", type="primary")

if generate_clicked:

    if not mission_objective.strip():
        st.warning("Please enter a mission objective before generating.")
        st.stop()

    with st.spinner("Running physics engine…"):
        orbital   = calculate_orbital_mechanics(altitude_km)
        prop      = calculate_propellant_mass(dry_mass_kg, delta_v_ms, isp_seconds)
        comms     = calculate_fspl(altitude_km, frequency_mhz)
        power     = calculate_solar_power(power_sun_w, power_eclipse_w, orbital["orbital_period_min"])
        drag      = calculate_atmospheric_drag(altitude_km, dry_mass_kg)
        coverage  = calculate_ground_coverage(altitude_km)
        radiation = calculate_radiation_dose(altitude_km, inclination_deg, mission_duration_days)
        thermal   = calculate_thermal(altitude_km)

        physics = {
            **orbital, **prop, **comms, **power,
            **drag, **coverage, **radiation, **thermal,
            "dry_mass_input":        dry_mass_kg,
            "frequency_input_mhz":   frequency_mhz,
            "inclination_deg":       inclination_deg,
            "mission_duration_days": mission_duration_days,
        }

    st.divider()
    st.subheader("📊 Physics Engine — Calculated Constraints")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Orbital Velocity", f"{orbital['orbital_velocity_kms']} km/s")
        st.metric("Orbital Period",   f"{orbital['orbital_period_min']} min")
    with c2:
        st.metric("Propellant Mass",  f"{prop['propellant_mass_kg']} kg")
        st.metric("Total Wet Mass",   f"{prop['total_wet_mass_kg']} kg")
    with c3:
        st.metric("Path Loss (FSPL)", f"{comms['fspl_db']} dB")
        st.metric("Frequency Band",   comms['frequency_band'].split("(")[0].strip())
    with c4:
        st.metric("Required Solar Power", f"{power['required_solar_power_w']} W")
        st.metric("Eclipse Duration", f"{power['eclipse_time_min']} min/orbit")

    st.write("")

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.metric("Orbital Lifetime", f"{drag['orbital_lifetime_days']} days")
        st.caption(drag['lifetime_verdict'])
    with d2:
        st.metric("Contact Time/Day", f"{coverage['total_contact_min_day']} min")
        st.caption(f"{coverage['passes_per_day']} passes/day · {coverage['contact_per_pass_min']} min/pass")
    with d3:
        st.metric("Total Radiation Dose", f"{radiation['total_dose_krad']} krad")
        st.caption(radiation['shielding_recommendation'])
    with d4:
        st.metric("Temp (Sun / Eclipse)", f"{thermal['temp_sunlight_c']}°C / {thermal['temp_eclipse_c']}°C")
        st.caption(thermal['thermal_verdict'])

    if prop["mass_ratio"] > 4.0:
        st.error(f"⚠️ **DESIGN WARNING — High Mass Ratio ({prop['mass_ratio']})** — Consider a higher Isp engine or reducing ΔV.")
    elif prop["mass_ratio"] > 2.5:
        st.warning(f"⚠️ Mass ratio of {prop['mass_ratio']} is feasible but tight.")

    if comms["fspl_db"] > 160:
        st.warning(f"⚠️ Path loss of {comms['fspl_db']} dB is high. A high-gain directional antenna will be required.")

    if radiation["radiation_risk_level"] in ["High", "Critical"]:
        st.error(f"🔴 **RADIATION WARNING — {radiation['radiation_risk_level']} Risk** — {radiation['shielding_recommendation']}")

    if drag["orbital_lifetime_days"] < 30:
        st.error(f"⚠️ **LIFETIME WARNING** — Satellite re-enters in {drag['orbital_lifetime_days']} days. Raise altitude.")

    st.divider()
    st.subheader("📋 AI Systems Architecture Report")

    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception:
        st.error("**Anthropic API key not found.** Add `ANTHROPIC_API_KEY = 'sk-ant-...'` to `.streamlit/secrets.toml`.")
        st.stop()

    user_message = build_user_message(mission_objective, mission_type, physics)

    try:
        with st.spinner("Claude is drafting your Systems Architecture Document…"):
            report_placeholder = st.empty()
            full_response = ""

            with client.messages.stream(
                model="claude-sonnet-4-5",
                max_tokens=2500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    report_placeholder.markdown(full_response + "▌")
            report_placeholder.markdown(full_response)

    except Exception as e:
        st.error(f"API call failed: {e}")
        st.stop()

    st.divider()
    st.download_button(
        label="⬇️ Download Report as Markdown",
        data=full_response,
        file_name="aeroforge_mission_report.md",
        mime="text/markdown",
    )

st.divider()
st.caption(
    "AeroForge AI uses 8 validated aerospace physics equations combined with Claude. "
    "Results are educational — always verify with a licensed engineer before hardware procurement."
)