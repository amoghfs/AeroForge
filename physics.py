"""
AeroForge AI — Physics Engine
==============================
Eight core aerospace equations used to generate hard constraints
that are injected into the AI system prompt.
"""

import math


# ─────────────────────────────────────────────────────────────
# 1. ORBITAL MECHANICS  (Kepler's Laws)
# ─────────────────────────────────────────────────────────────
def calculate_orbital_mechanics(altitude_km: float) -> dict:
    R_EARTH = 6371.0
    MU      = 398600.44

    r = R_EARTH + altitude_km
    velocity_kms   = math.sqrt(MU / r)
    period_seconds = 2 * math.pi * math.sqrt((r ** 3) / MU)
    period_minutes = period_seconds / 60

    return {
        "orbital_velocity_kms": round(velocity_kms, 3),
        "orbital_period_min":   round(period_minutes, 2),
        "orbital_radius_km":    round(r, 1),
    }


# ─────────────────────────────────────────────────────────────
# 2. PROPULSION  (Tsiolkovsky Rocket Equation)
# ─────────────────────────────────────────────────────────────
def calculate_propellant_mass(dry_mass_kg: float,
                              delta_v_ms: float,
                              isp_seconds: float) -> dict:
    G0 = 9.80665

    exponent      = delta_v_ms / (isp_seconds * G0)
    wet_mass_kg   = dry_mass_kg * math.exp(exponent)
    propellant_kg = wet_mass_kg - dry_mass_kg

    return {
        "propellant_mass_kg": round(propellant_kg, 2),
        "total_wet_mass_kg":  round(wet_mass_kg, 2),
        "mass_ratio":         round(wet_mass_kg / dry_mass_kg, 3),
    }


# ─────────────────────────────────────────────────────────────
# 3. COMMUNICATIONS  (Free-Space Path Loss)
# ─────────────────────────────────────────────────────────────
def calculate_fspl(distance_km: float, frequency_mhz: float) -> dict:
    C = 299_792_458

    d_m  = distance_km   * 1_000
    f_hz = frequency_mhz * 1_000_000

    fspl_linear = ((4 * math.pi * d_m * f_hz) / C) ** 2
    fspl_db     = 10 * math.log10(fspl_linear)

    if frequency_mhz < 300:
        band = "VHF (low data rate — basic telemetry only)"
    elif frequency_mhz < 3_000:
        band = "UHF/S-Band (suitable for CubeSat imagery)"
    elif frequency_mhz < 30_000:
        band = "X-Band (high data rate — recommended for Earth observation)"
    else:
        band = "Ka-Band (very high throughput)"

    return {
        "fspl_db":        round(fspl_db, 1),
        "frequency_band": band,
        "distance_km":    distance_km,
    }


# ─────────────────────────────────────────────────────────────
# 4. POWER  (Solar Array Sizing — Eclipse-Aware)
# ─────────────────────────────────────────────────────────────
def calculate_solar_power(power_sunlight_w: float,
                          power_eclipse_w: float,
                          orbital_period_min: float,
                          eclipse_fraction: float = 0.368) -> dict:
    EFFICIENCY = 0.70

    t_eclipse = eclipse_fraction * orbital_period_min
    t_sun     = orbital_period_min - t_eclipse

    energy_needed  = (power_sunlight_w * t_sun) + (power_eclipse_w * t_eclipse)
    required_power = (energy_needed / t_sun) / EFFICIENCY

    return {
        "required_solar_power_w": round(required_power, 1),
        "eclipse_time_min":       round(t_eclipse, 1),
        "sunlight_time_min":      round(t_sun, 1),
    }


# ─────────────────────────────────────────────────────────────
# 5. ATMOSPHERIC DRAG  (Orbital Lifetime Estimate)
# ─────────────────────────────────────────────────────────────
def calculate_atmospheric_drag(altitude_km: float,
                                dry_mass_kg: float,
                                cross_section_m2: float = 0.03,
                                cd: float = 2.2) -> dict:
    if altitude_km < 200:
        rho0, h0, H = 2.789e-10, 175, 26.8
    elif altitude_km < 300:
        rho0, h0, H = 5.464e-11, 250, 37.2
    elif altitude_km < 400:
        rho0, h0, H = 1.916e-11, 350, 45.5
    elif altitude_km < 500:
        rho0, h0, H = 5.606e-12, 450, 60.8
    elif altitude_km < 600:
        rho0, h0, H = 1.454e-12, 550, 73.0
    elif altitude_km < 700:
        rho0, h0, H = 3.614e-13, 650, 88.7
    elif altitude_km < 800:
        rho0, h0, H = 1.170e-13, 750, 124.6
    else:
        rho0, h0, H = 5.245e-14, 850, 181.0

    rho = rho0 * math.exp(-(altitude_km - h0) / H)

    R_EARTH = 6371.0
    MU      = 398600.44e9
    r       = (R_EARTH + altitude_km) * 1000

    v = math.sqrt(MU / r)
    f_drag = 0.5 * rho * v**2 * cd * cross_section_m2

    period_s      = 2 * math.pi * math.sqrt(r**3 / MU)
    delta_v_orbit = (f_drag * period_s) / dry_mass_kg
    delta_h_orbit = (2 * r * delta_v_orbit) / v

    if delta_h_orbit > 0:
        orbits_to_reentry = (altitude_km * 1000) / delta_h_orbit
        lifetime_days     = (orbits_to_reentry * period_s) / 86400
    else:
        lifetime_days = 99999

    if lifetime_days < 30:
        verdict = "⚠️ Critical — re-entry within 1 month. Raise altitude or add drag makeup."
    elif lifetime_days < 180:
        verdict = "⚠️ Short mission life. Plan for deorbit or periodic reboost."
    elif lifetime_days < 730:
        verdict = "✅ Acceptable for a 1–2 year student mission."
    else:
        verdict = "✅ Long mission life. Compliant with 25-year deorbit guideline."

    return {
        "orbital_lifetime_days": round(min(lifetime_days, 99999), 1),
        "drag_force_n":          round(f_drag * 1e6, 4),
        "atm_density_kg_m3":     f"{rho:.3e}",
        "lifetime_verdict":      verdict,
    }


# ─────────────────────────────────────────────────────────────
# 6. GROUND STATION COVERAGE
# ─────────────────────────────────────────────────────────────
def calculate_ground_coverage(altitude_km: float,
                               min_elevation_deg: float = 5.0) -> dict:
    R_EARTH = 6371.0
    MU      = 398600.44

    r              = R_EARTH + altitude_km
    period_seconds = 2 * math.pi * math.sqrt((r**3) / MU)
    period_minutes = period_seconds / 60

    rho_rad    = math.asin(R_EARTH / r)
    elev_rad   = math.radians(min_elevation_deg)
    lambda_rad = math.pi / 2 - elev_rad - rho_rad

    if lambda_rad <= 0:
        contact_per_pass_min = 0.0
    else:
        contact_per_pass_min = round((2 * lambda_rad / (2 * math.pi)) * period_minutes, 2)

    passes_per_day    = round(86400 / period_seconds, 1)
    total_contact_min = round(contact_per_pass_min * passes_per_day, 1)

    if total_contact_min < 10:
        coverage_verdict = "⚠️ Very limited contact window. Consider multiple ground stations."
    elif total_contact_min < 30:
        coverage_verdict = "✅ Adequate for telemetry. Tight for large image downlinks."
    else:
        coverage_verdict = "✅ Good coverage. Sufficient for high-volume data downlink."

    return {
        "contact_per_pass_min":  contact_per_pass_min,
        "passes_per_day":        passes_per_day,
        "total_contact_min_day": total_contact_min,
        "coverage_verdict":      coverage_verdict,
    }


# ─────────────────────────────────────────────────────────────
# 7. RADIATION DOSAGE
# ─────────────────────────────────────────────────────────────
def calculate_radiation_dose(altitude_km: float,
                              inclination_deg: float = 51.6,
                              mission_duration_days: float = 365) -> dict:
    if altitude_km < 400:
        base_dose_rad_day = 5.0
    elif altitude_km < 600:
        base_dose_rad_day = 10.0
    elif altitude_km < 800:
        base_dose_rad_day = 20.0
    elif altitude_km < 1000:
        base_dose_rad_day = 50.0
    else:
        base_dose_rad_day = 150.0

    if inclination_deg > 70:
        inclination_factor = 1.8
    elif inclination_deg > 50:
        inclination_factor = 1.3
    else:
        inclination_factor = 1.0

    dose_rad_day    = base_dose_rad_day * inclination_factor
    total_dose_krad = (dose_rad_day * mission_duration_days) / 1000

    if total_dose_krad < 5:
        shielding_rec = "✅ Commercial-off-the-shelf (COTS) components are sufficient."
        risk_level    = "Low"
    elif total_dose_krad < 20:
        shielding_rec = "⚠️ Use radiation-tolerant components. Add spot shielding on sensitive ICs."
        risk_level    = "Medium"
    elif total_dose_krad < 100:
        shielding_rec = "🔴 Radiation-hardened (RadHard) components required. Increase Al shielding to 5mm."
        risk_level    = "High"
    else:
        shielding_rec = "🔴 Extreme radiation environment. Mission architecture must be redesigned."
        risk_level    = "Critical"

    return {
        "total_dose_krad":           round(total_dose_krad, 2),
        "dose_rate_rad_day":         round(dose_rad_day, 1),
        "radiation_risk_level":      risk_level,
        "shielding_recommendation":  shielding_rec,
    }


# ─────────────────────────────────────────────────────────────
# 8. THERMAL ANALYSIS
# ─────────────────────────────────────────────────────────────
def calculate_thermal(altitude_km: float,
                       absorptivity: float = 0.9,
                       emissivity: float = 0.8,
                       surface_area_m2: float = 0.06) -> dict:
    SIGMA      = 5.670374419e-8
    SOLAR_FLUX = 1361.0
    DEEP_SPACE = 3.0

    a_cross = surface_area_m2 / 6

    t_sun_k = ((absorptivity * SOLAR_FLUX * a_cross) /
               (emissivity * SIGMA * surface_area_m2)) ** 0.25
    t_sun_c = round(t_sun_k - 273.15, 1)

    tau_min   = 20.0
    orb       = calculate_orbital_mechanics(altitude_km)
    t_ecl_min = 0.368 * orb["orbital_period_min"]

    t_eclipse_k = (DEEP_SPACE**4 + (t_sun_k**4 - DEEP_SPACE**4) *
                   math.exp(-t_ecl_min / tau_min)) ** 0.25
    t_eclipse_c = round(t_eclipse_k - 273.15, 1)
    delta_t     = round(t_sun_c - t_eclipse_c, 1)

    if delta_t > 100:
        thermal_verdict = "🔴 Extreme thermal cycling. Active thermal control (heaters/heat pipes) required."
    elif delta_t > 60:
        thermal_verdict = "⚠️ Significant thermal swing. Use thermal blankets (MLI) and careful component placement."
    else:
        thermal_verdict = "✅ Manageable thermal environment. Passive control (coatings, MLI) likely sufficient."

    return {
        "temp_sunlight_c":  t_sun_c,
        "temp_eclipse_c":   t_eclipse_c,
        "temp_delta_c":     delta_t,
        "thermal_verdict":  thermal_verdict,
    }


# ─────────────────────────────────────────────────────────────
# CONVENIENCE WRAPPER — runs all eight engines at once
# ─────────────────────────────────────────────────────────────
def run_all_engines(altitude_km, dry_mass_kg, delta_v_ms, isp_seconds,
                    frequency_mhz, power_sunlight_w, power_eclipse_w,
                    inclination_deg=51.6, mission_duration_days=365) -> dict:
    orbital   = calculate_orbital_mechanics(altitude_km)
    prop      = calculate_propellant_mass(dry_mass_kg, delta_v_ms, isp_seconds)
    comms     = calculate_fspl(altitude_km, frequency_mhz)
    power     = calculate_solar_power(power_sunlight_w, power_eclipse_w, orbital["orbital_period_min"])
    drag      = calculate_atmospheric_drag(altitude_km, dry_mass_kg)
    coverage  = calculate_ground_coverage(altitude_km)
    radiation = calculate_radiation_dose(altitude_km, inclination_deg, mission_duration_days)
    thermal   = calculate_thermal(altitude_km)
    return {**orbital, **prop, **comms, **power, **drag, **coverage, **radiation, **thermal}