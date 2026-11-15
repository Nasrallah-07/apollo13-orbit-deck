import json
import os

BASE = r'c:\Users\Nasrallah\Downloads\chat-812c8388-89f0-4c7c-88f6-7e872379485d'
SRC_JSON = os.path.join(BASE, 'apollo13_fire_risk_simulation.json')
OUT_JSON_1 = os.path.join(BASE, 'apollo13_numeric_telemetry-1.json')
OUT_JSON_2 = os.path.join(BASE, 'apollo13_numeric_telemetry.json')

with open(SRC_JSON, 'r', encoding='utf-8') as f:
    full_data = json.load(f)

# Encoding mappings for categorical values to pure numbers
phase_map = {
    'Pre-Launch': 1,
    'Launch': 2,
    'Earth_Orbit': 3,
    'TLI_Burn': 4,
    'Translunar_Coast': 5,
    'O2_Tank_Explosion': 6,
    'Emergency_Response': 7,
    'Lifeboat_Coast': 8,
    'Lunar_Flyby': 9,
    'Return_Coast': 10,
    'CM_Power_Up': 11,
    'Reentry': 12,
    'Splashdown': 13
}

fire_hazard_map = {
    'ELECTRICAL_ARC': 1,
    'OXYGEN_ENRICHED_COMBUSTION': 2,
    'CRYOGENIC_FUEL_LEAK': 3,
    'THERMAL_RUNAWAY': 4,
    'PYROTECHNIC_IGNITION': 5,
    'HYPERGOLIC_PROPELLANT_REACTION': 6,
    'WIRING_INSULATION_BURN': 7,
    'PRESSURE_VESSEL_RUPTURE_FIRE': 8
}

risk_level_map = {
    'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4,
    'GREEN': 1, 'YELLOW': 2, 'ORANGE': 3, 'RED': 4
}

numeric_points = []
for p in full_data['simulation_data']:
    pt_id = p['data_point_id']
    met_h = p['met_hours']
    met_m = p['met_minutes']
    phase_id = phase_map.get(p['mission_phase'], 0)
    
    fr = p['fire_risk']
    sev = fr['severity']          # 1..4
    lik = fr['likelihood']        # 1..5
    rpn = fr['risk_priority_number'] # 1..20
    rlvl = risk_level_map.get(fr['risk_level'], 1) # 1..4
    f_type = fire_hazard_map.get(fr['fire_hazard_type'], 1) # 1..8
    
    sr = p['sensor_readings']
    o2_psi = sr['o2_tank2_pressure_psi']
    o2_pct = sr['cabin_o2_percentage']
    temp_f = sr['sm_bay4_temperature_F']
    is_alert = 1 if sr.get('is_explosion_event', False) else 0
    
    numeric_points.append({
        'id': pt_id,
        'met_h': met_h,
        'met_min': met_m,
        'phase': phase_id,
        'sev': sev,
        'lik': lik,
        'rpn': rpn,
        'risk_lvl': rlvl,
        'hazard_type': f_type,
        'o2_psi': o2_psi,
        'o2_pct': o2_pct,
        'temp_f': temp_f,
        'is_alert': is_alert
    })

output_doc = {
    'mission_id': 13,
    'total_points': len(numeric_points),
    'duration_hours': full_data['metadata']['total_met_hours'],
    'encoding_dictionaries': {
        'phase': {str(v): k for k, v in phase_map.items()},
        'hazard_type': {str(v): k for k, v in fire_hazard_map.items()},
        'risk_lvl': {
            '1': 'Low (Green)',
            '2': 'Medium (Yellow)',
            '3': 'High (Orange)',
            '4': 'Critical (Red)'
        }
    },
    'columns': [
        'id',
        'met_h (Mission Elapsed Time in hours)',
        'met_min (Mission Elapsed Time in minutes)',
        'phase (1..13)',
        'sev (Severity: 1=Negligible, 2=Marginal, 3=Critical, 4=Catastrophic)',
        'lik (Likelihood: 1=Improbable, 2=Remote, 3=Occasional, 4=Probable, 5=Frequent)',
        'rpn (Risk Priority Number: 1..20)',
        'risk_lvl (Risk Level code: 1..4)',
        'hazard_type (Hazard code: 1..8)',
        'o2_psi (Cryo O2 Tank 2 Pressure in psi)',
        'o2_pct (Cabin Oxygen Percentage)',
        'temp_f (Service Module Bay 4 Temperature in deg F)',
        'is_alert (Explosion event flag: 0=normal, 1=critical alert)'
    ],
    'data': numeric_points
}

for out_path in [OUT_JSON_1, OUT_JSON_2]:
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_doc, f, separators=(',', ':'))
    print(f"Generated {len(numeric_points)} records to {out_path} ({round(os.path.getsize(out_path)/1024, 1)} KB)")
