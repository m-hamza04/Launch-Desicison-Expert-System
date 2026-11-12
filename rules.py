"""
rules.py  -  The "brain" of the Launch Go/No-Go Expert System.

Every rule is a plain IF statement:
    IF <condition is true> THEN add a reason to the HOLD list or the SCRUB list.

Final decision:
    any SCRUB reason  -> SCRUB
    else any HOLD     -> HOLD
    else              -> GO

Thresholds are simplified and inspired by public launch commit criteria
(educational use only).
"""

TOTAL_RULES = 56


def check_launch(f):
    """f is a dictionary of current facts, e.g. f["wind_speed"] = 12.
    Returns: decision, scrub_reasons, hold_reasons"""

    scrub = []   # reasons that CANCEL the launch
    hold = []    # reasons that PAUSE the countdown

    # ------------------------------------------------------------
    # WEATHER RULES (13)
    # ------------------------------------------------------------
    if f["wind_speed"] > 30:
        hold.append("W1: Wind speed above 30 kt")

    if f["wind_gust"] > 35:
        hold.append("W2: Wind gusts above 35 kt")

    if f["wind_shear_severe"]:
        scrub.append("W3: Severe upper-level wind shear")

    if f["lightning_distance"] < 10:
        hold.append("W4: Lightning within 10 nm")

    if f["thunderstorm"]:
        hold.append("W5: Thunderstorm in launch area")

    if f["cloud_ceiling"] < 6000:
        hold.append("W6: Cloud ceiling below 6,000 ft")

    if f["visibility"] < 4:
        hold.append("W7: Visibility below 4 miles")

    if f["temperature"] < 2:
        hold.append("W8: Temperature below 2 C")

    if f["temperature"] > 35:
        hold.append("W9: Temperature above 35 C")

    if f["rain"]:
        hold.append("W10: Rain at launch site")

    if f["tropical_warning"]:
        scrub.append("W11: Tropical storm / hurricane warning")

    if f["sea_state"] > 5:
        hold.append("W12: Sea state above 5 in recovery area")

    if f["solar_storm"]:
        hold.append("W13: Severe solar / geomagnetic storm")

    # ------------------------------------------------------------
    # PROPULSION AND FUEL RULES (9)
    # ------------------------------------------------------------
    if f["fuel_leak"]:
        scrub.append("P1: Fuel leak detected")

    if f["tank_pressure"] < 210 or f["tank_pressure"] > 240:
        hold.append("P2: Tank pressure outside 210-240 psi")

    if f["propellant_temp"] < -186 or f["propellant_temp"] > -180:
        hold.append("P3: Propellant temperature outside -186 to -180 C")

    if not f["oxidizer_loaded"]:
        hold.append("P4: Oxidizer loading incomplete")

    if not f["chilldown_done"]:
        hold.append("P5: Engine chilldown incomplete")

    if f["valve_fault"]:
        scrub.append("P6: Main valve fault")

    if f["helium_pressure"] < 3000:
        hold.append("P7: Helium pressurant below 3,000 psi")

    if f["ignition_sensor_fault"]:
        scrub.append("P8: Ignition sensor fault")

    if f["fuel_level"] < 98:
        hold.append("P9: Fuel level below 98 percent")

    # ------------------------------------------------------------
    # VEHICLE SYSTEMS RULES (10)
    # ------------------------------------------------------------
    if not f["telemetry_ok"]:
        hold.append("V1: Telemetry lost")

    if f["guidance_fault"]:
        scrub.append("V2: Guidance computer fault")

    if not f["avionics_ok"]:
        hold.append("V3: Avionics self-check failed")

    if f["battery"] < 90:
        hold.append("V4: Battery charge below 90 percent")

    if not f["fts_armed"]:
        scrub.append("V5: Flight termination system not armed")

    if f["structural_anomaly"]:
        scrub.append("V6: Structural sensor anomaly")

    if not f["nav_aligned"]:
        hold.append("V7: Navigation alignment incomplete")

    if not f["payload_ready"]:
        hold.append("V8: Payload not ready")

    if f["software_mismatch"]:
        scrub.append("V9: Flight software version mismatch")

    if not f["backup_computer_synced"]:
        hold.append("V10: Backup flight computer not synced")

    # ------------------------------------------------------------
    # RANGE SAFETY RULES (9)
    # ------------------------------------------------------------
    if f["boat_in_zone"]:
        hold.append("R1: Boat in danger zone")

    if f["aircraft_in_zone"]:
        hold.append("R2: Aircraft in restricted airspace")

    if not f["radar_ok"]:
        hold.append("R3: Tracking radar down")

    if not f["range_comms_ok"]:
        hold.append("R4: Range communications down")

    if not f["termination_link_ok"]:
        scrub.append("R5: Termination command link failed")

    if f["drone_detected"]:
        hold.append("R6: Drone detected near pad")

    if f["downrange_ship_traffic"]:
        hold.append("R7: Ship traffic downrange")

    if not f["rso_go"]:
        hold.append("R8: Range safety officer says No-Go")

    if not f["recovery_ship_ready"]:
        hold.append("R9: Recovery ship not in position")

    # ------------------------------------------------------------
    # GROUND SYSTEMS RULES (9)
    # ------------------------------------------------------------
    if not f["ground_power_ok"]:
        hold.append("G1: Ground power failure")

    if not f["control_comms_ok"]:
        hold.append("G2: Control center comms down")

    if not f["fire_suppression_ok"]:
        hold.append("G3: Fire suppression fault")

    if not f["deluge_ok"]:
        hold.append("G4: Pad water deluge fault")

    if not f["personnel_clear"]:
        hold.append("G5: Personnel still in pad area")

    if f["hazard_gas"]:
        scrub.append("G6: Hazardous gas detected on pad")

    if not f["backup_power_ok"]:
        hold.append("G7: Backup power unavailable")

    if not f["staffing_complete"]:
        hold.append("G8: Launch team staffing incomplete")

    if f["umbilical_fault"]:
        scrub.append("G9: Umbilical retract fault")

    # ------------------------------------------------------------
    # LAUNCH WINDOW RULES (6)
    # ------------------------------------------------------------
    if f["clock_fault"]:
        hold.append("L2: Countdown clock fault")

    if f["orbital_error"] > 0.5:
        hold.append("L3: Orbital alignment error above 0.5 deg")

    if f["minutes_to_close"] <= 0:
        scrub.append("L4: Launch window already closed")

    if f["holds_used"] > 3:
        scrub.append("L5: More than 3 holds already used")

    if f["total_hold_minutes"] > 30:
        scrub.append("L6: Total hold time above 30 min")

    # L1 is checked last because it needs to know if any HOLD is active
    if f["minutes_to_close"] > 0 and f["minutes_to_close"] < 2 and len(hold) > 0:
        scrub.append("L1: Window closing in under 2 min while a HOLD is active")

    # ------------------------------------------------------------
    # FINAL DECISION (SCRUB beats HOLD, HOLD beats GO)
    # ------------------------------------------------------------
    if len(scrub) > 0:
        decision = "SCRUB"
    elif len(hold) > 0:
        decision = "HOLD"
    else:
        decision = "GO"

    return decision, scrub, hold