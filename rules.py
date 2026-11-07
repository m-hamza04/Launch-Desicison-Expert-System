"""
rules.py  -  Knowledge base + inference engine
Launch Go/No-Go Expert System

Every rule has the form:   IF <condition on facts> THEN <HOLD or SCRUB>
If no rule fires the decision is GO.
Thresholds are simplified and inspired by public launch commit criteria
(educational use only).
"""

# ---------------------------------------------------------------------------
# 1. FACTS  (working memory)  -  default values describe a "Perfect Day"
# ---------------------------------------------------------------------------
DEFAULTS = {
    # Weather
    "wind_speed": 12,            # knots
    "wind_gust": 18,             # knots
    "wind_shear_severe": False,
    "lightning_distance": 50,    # nautical miles (50 = none nearby)
    "thunderstorm": False,
    "cloud_ceiling": 12000,      # feet
    "visibility": 10.0,          # miles
    "temperature": 24,           # degrees C
    "rain": False,
    "tropical_warning": False,
    "sea_state": 2,              # 0-9 scale (recovery area)
    "solar_storm": False,
    # Propulsion and fuel
    "fuel_leak": False,
    "tank_pressure": 225,        # psi
    "propellant_temp": -183,     # degrees C
    "oxidizer_loaded": True,
    "chilldown_done": True,
    "valve_fault": False,
    "helium_pressure": 3800,     # psi
    "ignition_sensor_fault": False,
    "fuel_level": 100,           # percent
    # Vehicle systems
    "telemetry_ok": True,
    "guidance_fault": False,
    "avionics_ok": True,
    "battery": 100,              # percent
    "fts_armed": True,           # flight termination system
    "structural_anomaly": False,
    "nav_aligned": True,
    "payload_ready": True,
    "software_mismatch": False,
    "backup_computer_synced": True,
    # Range safety
    "boat_in_zone": False,
    "aircraft_in_zone": False,
    "radar_ok": True,
    "range_comms_ok": True,
    "termination_link_ok": True,
    "drone_detected": False,
    "downrange_ship_traffic": False,
    "rso_go": True,              # range safety officer
    "recovery_ship_ready": True,
    # Ground systems
    "ground_power_ok": True,
    "control_comms_ok": True,
    "fire_suppression_ok": True,
    "deluge_ok": True,
    "personnel_clear": True,
    "hazard_gas": False,
    "backup_power_ok": True,
    "staffing_complete": True,
    "umbilical_fault": False,
    # Launch window
    "minutes_to_close": 45,      # minutes until window closes
    "clock_fault": False,
    "orbital_error": 0.1,        # degrees
    "holds_used": 0,
    "total_hold_minutes": 0,
}

# ---------------------------------------------------------------------------
# 2. KNOWLEDGE BASE  -  (id, category, description, result, condition)
# ---------------------------------------------------------------------------
RULES = [
    # ---------------- Weather (13) ----------------
    ("W1", "Weather", "Wind speed above 30 kt", "HOLD", lambda f: f["wind_speed"] > 30),
    ("W2", "Weather", "Wind gusts above 35 kt", "HOLD", lambda f: f["wind_gust"] > 35),
    ("W3", "Weather", "Severe upper-level wind shear", "SCRUB", lambda f: f["wind_shear_severe"]),
    ("W4", "Weather", "Lightning within 10 nm", "HOLD", lambda f: f["lightning_distance"] < 10),
    ("W5", "Weather", "Thunderstorm in launch area", "HOLD", lambda f: f["thunderstorm"]),
    ("W6", "Weather", "Cloud ceiling below 6,000 ft", "HOLD", lambda f: f["cloud_ceiling"] < 6000),
    ("W7", "Weather", "Visibility below 4 miles", "HOLD", lambda f: f["visibility"] < 4),
    ("W8", "Weather", "Temperature below 2 C", "HOLD", lambda f: f["temperature"] < 2),
    ("W9", "Weather", "Temperature above 35 C", "HOLD", lambda f: f["temperature"] > 35),
    ("W10", "Weather", "Rain at launch site", "HOLD", lambda f: f["rain"]),
    ("W11", "Weather", "Tropical storm / hurricane warning", "SCRUB", lambda f: f["tropical_warning"]),
    ("W12", "Weather", "Sea state above 5 in recovery area", "HOLD", lambda f: f["sea_state"] > 5),
    ("W13", "Weather", "Severe solar / geomagnetic storm", "HOLD", lambda f: f["solar_storm"]),

    # ---------------- Propulsion and fuel (9) ----------------
    ("P1", "Propulsion", "Fuel leak detected", "SCRUB", lambda f: f["fuel_leak"]),
    ("P2", "Propulsion", "Tank pressure outside 210-240 psi", "HOLD",
     lambda f: not (210 <= f["tank_pressure"] <= 240)),
    ("P3", "Propulsion", "Propellant temperature outside -186 to -180 C", "HOLD",
     lambda f: not (-186 <= f["propellant_temp"] <= -180)),
    ("P4", "Propulsion", "Oxidizer loading incomplete", "HOLD", lambda f: not f["oxidizer_loaded"]),
    ("P5", "Propulsion", "Engine chilldown incomplete", "HOLD", lambda f: not f["chilldown_done"]),
    ("P6", "Propulsion", "Main valve fault", "SCRUB", lambda f: f["valve_fault"]),
    ("P7", "Propulsion", "Helium pressurant below 3,000 psi", "HOLD", lambda f: f["helium_pressure"] < 3000),
    ("P8", "Propulsion", "Ignition sensor fault", "SCRUB", lambda f: f["ignition_sensor_fault"]),
    ("P9", "Propulsion", "Fuel level below 98 percent", "HOLD", lambda f: f["fuel_level"] < 98),

    # ---------------- Vehicle systems (10) ----------------
    ("V1", "Vehicle", "Telemetry lost", "HOLD", lambda f: not f["telemetry_ok"]),
    ("V2", "Vehicle", "Guidance computer fault", "SCRUB", lambda f: f["guidance_fault"]),
    ("V3", "Vehicle", "Avionics self-check failed", "HOLD", lambda f: not f["avionics_ok"]),
    ("V4", "Vehicle", "Battery charge below 90 percent", "HOLD", lambda f: f["battery"] < 90),
    ("V5", "Vehicle", "Flight termination system not armed", "SCRUB", lambda f: not f["fts_armed"]),
    ("V6", "Vehicle", "Structural sensor anomaly", "SCRUB", lambda f: f["structural_anomaly"]),
    ("V7", "Vehicle", "Navigation alignment incomplete", "HOLD", lambda f: not f["nav_aligned"]),
    ("V8", "Vehicle", "Payload not ready", "HOLD", lambda f: not f["payload_ready"]),
    ("V9", "Vehicle", "Flight software version mismatch", "SCRUB", lambda f: f["software_mismatch"]),
    ("V10", "Vehicle", "Backup flight computer not synced", "HOLD", lambda f: not f["backup_computer_synced"]),

    # ---------------- Range safety (9) ----------------
    ("R1", "Range Safety", "Boat in danger zone", "HOLD", lambda f: f["boat_in_zone"]),
    ("R2", "Range Safety", "Aircraft in restricted airspace", "HOLD", lambda f: f["aircraft_in_zone"]),
    ("R3", "Range Safety", "Tracking radar down", "HOLD", lambda f: not f["radar_ok"]),
    ("R4", "Range Safety", "Range communications down", "HOLD", lambda f: not f["range_comms_ok"]),
    ("R5", "Range Safety", "Termination command link failed", "SCRUB", lambda f: not f["termination_link_ok"]),
    ("R6", "Range Safety", "Drone detected near pad", "HOLD", lambda f: f["drone_detected"]),
    ("R7", "Range Safety", "Ship traffic downrange", "HOLD", lambda f: f["downrange_ship_traffic"]),
    ("R8", "Range Safety", "Range safety officer says No-Go", "HOLD", lambda f: not f["rso_go"]),
    ("R9", "Range Safety", "Recovery ship not in position", "HOLD", lambda f: not f["recovery_ship_ready"]),

    # ---------------- Ground systems (9) ----------------
    ("G1", "Ground", "Ground power failure", "HOLD", lambda f: not f["ground_power_ok"]),
    ("G2", "Ground", "Control center comms down", "HOLD", lambda f: not f["control_comms_ok"]),
    ("G3", "Ground", "Fire suppression fault", "HOLD", lambda f: not f["fire_suppression_ok"]),
    ("G4", "Ground", "Pad water deluge fault", "HOLD", lambda f: not f["deluge_ok"]),
    ("G5", "Ground", "Personnel still in pad area", "HOLD", lambda f: not f["personnel_clear"]),
    ("G6", "Ground", "Hazardous gas detected on pad", "SCRUB", lambda f: f["hazard_gas"]),
    ("G7", "Ground", "Backup power unavailable", "HOLD", lambda f: not f["backup_power_ok"]),
    ("G8", "Ground", "Launch team staffing incomplete", "HOLD", lambda f: not f["staffing_complete"]),
    ("G9", "Ground", "Umbilical retract fault", "SCRUB", lambda f: f["umbilical_fault"]),

    # ---------------- Launch window (6) ----------------
    ("L2", "Launch Window", "Countdown clock fault", "HOLD", lambda f: f["clock_fault"]),
    ("L3", "Launch Window", "Orbital alignment error above 0.5 deg", "HOLD", lambda f: f["orbital_error"] > 0.5),
    ("L4", "Launch Window", "Launch window already closed", "SCRUB", lambda f: f["minutes_to_close"] <= 0),
    ("L5", "Launch Window", "More than 3 holds already used", "SCRUB", lambda f: f["holds_used"] > 3),
    ("L6", "Launch Window", "Total hold time above 30 min", "SCRUB", lambda f: f["total_hold_minutes"] > 30),
    # L1 is a compound rule: it needs to know whether any HOLD has fired,
    # so it is placed last (the engine fills in "hold_active" before each rule).
    ("L1", "Launch Window", "Window closing in under 2 min while a HOLD is active", "SCRUB",
     lambda f: 0 < f["minutes_to_close"] < 2 and f["hold_active"]),
]


# ---------------------------------------------------------------------------
# 3. INFERENCE ENGINE
# ---------------------------------------------------------------------------
def run_inference(facts):
    """Check every rule against the facts and return (decision, fired_rules)."""
    facts = dict(facts)
    fired = []

    for rule_id, category, description, result, condition in RULES:
        # working-memory fact used by compound rule L1
        facts["hold_active"] = any(r["Result"] == "HOLD" for r in fired)
        if condition(facts):
            fired.append({
                "ID": rule_id,
                "Category": category,
                "Condition": description,
                "Result": result,
            })

    scrub_rules = [r for r in fired if r["Result"] == "SCRUB"]
    hold_rules = [r for r in fired if r["Result"] == "HOLD"]

    # Conflict resolution: SCRUB beats HOLD, HOLD beats GO
    if scrub_rules:
        decision = "SCRUB"
    elif hold_rules:
        decision = "HOLD"
    else:
        decision = "GO"

    return decision, fired


# ---------------------------------------------------------------------------
# 4. PRESET SCENARIOS (only the facts that differ from DEFAULTS)
# ---------------------------------------------------------------------------
PRESETS = {
    "Perfect Day": {},
    "Thunderstorm": {
        "thunderstorm": True, "lightning_distance": 6, "wind_speed": 34,
        "cloud_ceiling": 3500, "rain": True,
    },
    "Fuel Leak": {"fuel_leak": True, "tank_pressure": 195},
    "Boat in Range Zone": {"boat_in_zone": True},
    "Closing Window": {"minutes_to_close": 1, "rso_go": False},
    "Total Chaos": {
        "wind_shear_severe": True, "lightning_distance": 4, "guidance_fault": True,
        "hazard_gas": True, "telemetry_ok": False, "radar_ok": False,
        "holds_used": 5, "minutes_to_close": 0,
    },
}
