"""
app.py  -  Streamlit UI
Launch Go/No-Go Expert System

Run locally:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from rules import DEFAULTS, PRESETS, RULES, run_inference

st.set_page_config(page_title="Launch Go/No-Go Expert System", page_icon="🚀", layout="wide")

# ---------------------------------------------------------------------------
# Session state: every fact lives in st.session_state under its own key
# ---------------------------------------------------------------------------
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def apply_preset(name):
    """Reset all facts to defaults, then apply the preset's changes."""
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    for key, value in PRESETS[name].items():
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# Sidebar: presets and project info
# ---------------------------------------------------------------------------
st.sidebar.title("Scenario Presets")
for preset_name in PRESETS:
    st.sidebar.button(preset_name, on_click=apply_preset, args=(preset_name,), width="stretch")

st.sidebar.markdown("---")
st.sidebar.caption(
    "Rule-based expert system. Knowledge base: "
    f"{len(RULES)} IF-THEN rules. Thresholds are simplified and inspired by "
    "public launch commit criteria (educational use only)."
)

# ---------------------------------------------------------------------------
# Inference: read current facts and run the engine
# ---------------------------------------------------------------------------
facts = {key: st.session_state[key] for key in DEFAULTS}
decision, fired = run_inference(facts)
scrub_count = sum(1 for r in fired if r["Result"] == "SCRUB")
hold_count = sum(1 for r in fired if r["Result"] == "HOLD")

# ---------------------------------------------------------------------------
# Header and decision banner
# ---------------------------------------------------------------------------
st.title("🚀 Launch Go/No-Go Expert System")
st.caption("Set the conditions below. The inference engine checks every rule and gives the launch decision.")

if decision == "GO":
    st.success("## ✅ GO FOR LAUNCH\nAll rules passed. No hold or scrub conditions.")
elif decision == "HOLD":
    st.warning("## ⏸️ HOLD\nCountdown stopped. Conditions may improve, resolve the issues below.")
else:
    st.error("## 🛑 SCRUB\nLaunch cancelled for this attempt. A critical rule fired.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Rules checked", len(RULES))
m2.metric("Rules fired", len(fired))
m3.metric("SCRUB rules", scrub_count)
m4.metric("HOLD rules", hold_count)

minutes = st.session_state["minutes_to_close"]
if decision == "GO":
    st.info(f"⏱️ T-minus clock running. Launch window closes in {minutes} min.")
else:
    st.info(f"⏱️ Clock held. Launch window closes in {minutes} min.")

st.subheader("Explanation: why this decision?")
if fired:
    st.dataframe(pd.DataFrame(fired), width="stretch", hide_index=True)
else:
    st.write("No rule fired, so every check passed.")

# ---------------------------------------------------------------------------
# Input tabs (one tab per category)
# ---------------------------------------------------------------------------
st.subheader("Mission Conditions")
tabs = st.tabs(["Weather", "Propulsion", "Vehicle", "Range Safety", "Ground", "Launch Window", "Knowledge Base"])

# ----- Weather -----
with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Wind speed (kt)", 0, 60, key="wind_speed")
        st.slider("Wind gusts (kt)", 0, 70, key="wind_gust")
        st.slider("Lightning distance (nm, 50 = none)", 0, 50, key="lightning_distance")
        st.slider("Cloud ceiling (ft)", 0, 20000, step=500, key="cloud_ceiling")
        st.slider("Visibility (miles)", 0.0, 15.0, step=0.5, key="visibility")
        st.slider("Temperature (C)", -10, 50, key="temperature")
        st.slider("Sea state in recovery area (0-9)", 0, 9, key="sea_state")
    with c2:
        st.checkbox("Severe upper-level wind shear", key="wind_shear_severe")
        st.checkbox("Thunderstorm in launch area", key="thunderstorm")
        st.checkbox("Rain at launch site", key="rain")
        st.checkbox("Tropical storm / hurricane warning", key="tropical_warning")
        st.checkbox("Severe solar / geomagnetic storm", key="solar_storm")

# ----- Propulsion -----
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Tank pressure (psi)", 100, 300, key="tank_pressure")
        st.slider("Propellant temperature (C)", -200, -150, key="propellant_temp")
        st.slider("Helium pressure (psi)", 1000, 4500, step=100, key="helium_pressure")
        st.slider("Fuel level (%)", 50, 100, key="fuel_level")
    with c2:
        st.checkbox("Fuel leak detected", key="fuel_leak")
        st.checkbox("Main valve fault", key="valve_fault")
        st.checkbox("Ignition sensor fault", key="ignition_sensor_fault")
        st.checkbox("Oxidizer loading complete", key="oxidizer_loaded")
        st.checkbox("Engine chilldown complete", key="chilldown_done")

# ----- Vehicle -----
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Battery charge (%)", 50, 100, key="battery")
        st.checkbox("Guidance computer fault", key="guidance_fault")
        st.checkbox("Structural sensor anomaly", key="structural_anomaly")
        st.checkbox("Flight software version mismatch", key="software_mismatch")
    with c2:
        st.checkbox("Telemetry OK", key="telemetry_ok")
        st.checkbox("Avionics self-check passed", key="avionics_ok")
        st.checkbox("Flight termination system armed", key="fts_armed")
        st.checkbox("Navigation aligned", key="nav_aligned")
        st.checkbox("Payload ready", key="payload_ready")
        st.checkbox("Backup flight computer synced", key="backup_computer_synced")

# ----- Range Safety -----
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        st.checkbox("Boat in danger zone", key="boat_in_zone")
        st.checkbox("Aircraft in restricted airspace", key="aircraft_in_zone")
        st.checkbox("Drone detected near pad", key="drone_detected")
        st.checkbox("Ship traffic downrange", key="downrange_ship_traffic")
    with c2:
        st.checkbox("Tracking radar online", key="radar_ok")
        st.checkbox("Range communications online", key="range_comms_ok")
        st.checkbox("Termination command link OK", key="termination_link_ok")
        st.checkbox("Range safety officer says GO", key="rso_go")
        st.checkbox("Recovery ship in position", key="recovery_ship_ready")

# ----- Ground -----
with tabs[4]:
    c1, c2 = st.columns(2)
    with c1:
        st.checkbox("Ground power OK", key="ground_power_ok")
        st.checkbox("Control center comms OK", key="control_comms_ok")
        st.checkbox("Fire suppression OK", key="fire_suppression_ok")
        st.checkbox("Pad water deluge OK", key="deluge_ok")
        st.checkbox("Pad area clear of personnel", key="personnel_clear")
    with c2:
        st.checkbox("Backup power available", key="backup_power_ok")
        st.checkbox("Launch team staffing complete", key="staffing_complete")
        st.checkbox("Hazardous gas detected on pad", key="hazard_gas")
        st.checkbox("Umbilical retract fault", key="umbilical_fault")

# ----- Launch Window -----
with tabs[5]:
    c1, c2 = st.columns(2)
    with c1:
        st.slider("Minutes until window closes", 0, 180, key="minutes_to_close")
        st.slider("Orbital alignment error (deg)", 0.0, 2.0, step=0.1, key="orbital_error")
        st.slider("Holds used so far", 0, 6, key="holds_used")
        st.slider("Total hold time so far (min)", 0, 90, key="total_hold_minutes")
    with c2:
        st.checkbox("Countdown clock fault", key="clock_fault")

# ----- Knowledge Base -----
with tabs[6]:
    st.write(f"The knowledge base contains **{len(RULES)} rules** in IF-THEN form.")
    kb = pd.DataFrame(
        [{"ID": r[0], "Category": r[1], "IF (condition)": r[2], "THEN": r[3]} for r in RULES]
    )
    st.dataframe(kb, width="stretch", hide_index=True)
