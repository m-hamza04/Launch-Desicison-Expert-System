import streamlit as st

from rules import check_launch, TOTAL_RULES

st.set_page_config(page_title="Launch Go/No-Go Expert System", page_icon="🚀", layout="wide")

st.title("🚀 Launch Go/No-Go Expert System")
st.caption("Set the conditions on the left. The expert system checks every rule and gives the decision on the right.")

facts = {}   # dictionary that will hold every input value

left, right = st.columns([3, 2])

# ============================================================
# LEFT SIDE: INPUTS (one tab per category)
# ============================================================
with left:
    st.subheader("Mission Conditions")
    t_weather, t_fuel, t_vehicle, t_range, t_ground, t_window = st.tabs(
        ["Weather", "Propulsion", "Vehicle", "Range Safety", "Ground", "Launch Window"]
    )

    # ---------------- Weather ----------------
    with t_weather:
        facts["wind_speed"] = st.slider("Wind speed (kt)", 0, 60, 12)
        facts["wind_gust"] = st.slider("Wind gusts (kt)", 0, 70, 18)
        facts["lightning_distance"] = st.slider("Lightning distance (nm, 50 = none)", 0, 50, 50)
        facts["cloud_ceiling"] = st.slider("Cloud ceiling (ft)", 0, 20000, 12000, step=500)
        facts["visibility"] = st.slider("Visibility (miles)", 0.0, 15.0, 10.0, step=0.5)
        facts["temperature"] = st.slider("Temperature (C)", -10, 50, 24)
        facts["sea_state"] = st.slider("Sea state in recovery area (0-9)", 0, 9, 2)
        facts["wind_shear_severe"] = st.checkbox("Severe upper-level wind shear")
        facts["thunderstorm"] = st.checkbox("Thunderstorm in launch area")
        facts["rain"] = st.checkbox("Rain at launch site")
        facts["tropical_warning"] = st.checkbox("Tropical storm / hurricane warning")
        facts["solar_storm"] = st.checkbox("Severe solar / geomagnetic storm")

    # ---------------- Propulsion ----------------
    with t_fuel:
        facts["tank_pressure"] = st.slider("Tank pressure (psi)", 100, 300, 225)
        facts["propellant_temp"] = st.slider("Propellant temperature (C)", -200, -150, -183)
        facts["helium_pressure"] = st.slider("Helium pressure (psi)", 1000, 4500, 3800, step=100)
        facts["fuel_level"] = st.slider("Fuel level (%)", 50, 100, 100)
        facts["fuel_leak"] = st.checkbox("Fuel leak detected")
        facts["valve_fault"] = st.checkbox("Main valve fault")
        facts["ignition_sensor_fault"] = st.checkbox("Ignition sensor fault")
        facts["oxidizer_loaded"] = st.checkbox("Oxidizer loading complete", value=True)
        facts["chilldown_done"] = st.checkbox("Engine chilldown complete", value=True)

    # ---------------- Vehicle ----------------
    with t_vehicle:
        facts["battery"] = st.slider("Battery charge (%)", 50, 100, 100)
        facts["guidance_fault"] = st.checkbox("Guidance computer fault")
        facts["structural_anomaly"] = st.checkbox("Structural sensor anomaly")
        facts["software_mismatch"] = st.checkbox("Flight software version mismatch")
        facts["telemetry_ok"] = st.checkbox("Telemetry OK", value=True)
        facts["avionics_ok"] = st.checkbox("Avionics self-check passed", value=True)
        facts["fts_armed"] = st.checkbox("Flight termination system armed", value=True)
        facts["nav_aligned"] = st.checkbox("Navigation aligned", value=True)
        facts["payload_ready"] = st.checkbox("Payload ready", value=True)
        facts["backup_computer_synced"] = st.checkbox("Backup flight computer synced", value=True)

    # ---------------- Range Safety ----------------
    with t_range:
        facts["boat_in_zone"] = st.checkbox("Boat in danger zone")
        facts["aircraft_in_zone"] = st.checkbox("Aircraft in restricted airspace")
        facts["drone_detected"] = st.checkbox("Drone detected near pad")
        facts["downrange_ship_traffic"] = st.checkbox("Ship traffic downrange")
        facts["radar_ok"] = st.checkbox("Tracking radar online", value=True)
        facts["range_comms_ok"] = st.checkbox("Range communications online", value=True)
        facts["termination_link_ok"] = st.checkbox("Termination command link OK", value=True)
        facts["rso_go"] = st.checkbox("Range safety officer says GO", value=True)
        facts["recovery_ship_ready"] = st.checkbox("Recovery ship in position", value=True)

    # ---------------- Ground ----------------
    with t_ground:
        facts["hazard_gas"] = st.checkbox("Hazardous gas detected on pad")
        facts["umbilical_fault"] = st.checkbox("Umbilical retract fault")
        facts["ground_power_ok"] = st.checkbox("Ground power OK", value=True)
        facts["control_comms_ok"] = st.checkbox("Control center comms OK", value=True)
        facts["fire_suppression_ok"] = st.checkbox("Fire suppression OK", value=True)
        facts["deluge_ok"] = st.checkbox("Pad water deluge OK", value=True)
        facts["personnel_clear"] = st.checkbox("Pad area clear of personnel", value=True)
        facts["backup_power_ok"] = st.checkbox("Backup power available", value=True)
        facts["staffing_complete"] = st.checkbox("Launch team staffing complete", value=True)

    # ---------------- Launch Window ----------------
    with t_window:
        facts["minutes_to_close"] = st.slider("Minutes until window closes", 0, 180, 45)
        facts["orbital_error"] = st.slider("Orbital alignment error (deg)", 0.0, 2.0, 0.1, step=0.1)
        facts["holds_used"] = st.slider("Holds used so far", 0, 6, 0)
        facts["total_hold_minutes"] = st.slider("Total hold time so far (min)", 0, 90, 0)
        facts["clock_fault"] = st.checkbox("Countdown clock fault")

# ============================================================
# Run the expert system (rules.py) on the collected facts
# ============================================================
decision, scrub_reasons, hold_reasons = check_launch(facts)

# ============================================================
# RIGHT SIDE: DECISION + EXPLANATION
# ============================================================
with right:
    st.subheader("Launch Decision")

    if decision == "GO":
        st.success("## ✅ GO FOR LAUNCH\nAll rules passed.")
    elif decision == "HOLD":
        st.warning("## ⏸️ HOLD\nCountdown stopped. Fix the issues below.")
    else:
        st.error("## 🛑 SCRUB\nLaunch cancelled. A critical rule fired.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Rules checked", TOTAL_RULES)
    c2.metric("SCRUB rules fired", len(scrub_reasons))
    c3.metric("HOLD rules fired", len(hold_reasons))

    st.subheader("Why this decision?")

    if len(scrub_reasons) == 0 and len(hold_reasons) == 0:
        st.write("No rule fired, so every check passed.")

    if len(scrub_reasons) > 0:
        st.markdown("**SCRUB reasons (critical):**")
        for reason in scrub_reasons:
            st.write("🛑 " + reason)

    if len(hold_reasons) > 0:
        st.markdown("**HOLD reasons:**")
        for reason in hold_reasons:
            st.write("⏸️ " + reason)