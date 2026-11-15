import json
import math
import random

random.seed(42)

TOTAL_MET_HOURS = 142.9
N_POINTS = 6000

def severity_label(s):
    return {1:'Negligible', 2:'Marginal', 3:'Critical', 4:'Catastrophic'}[s]

def likelihood_label(l):
    return {1:'Improbable', 2:'Remote', 3:'Occasional', 4:'Probable', 5:'Frequent'}[l]

def risk_color(rpn):
    if rpn <= 4:    return 'GREEN'
    elif rpn <= 9:  return 'YELLOW'
    elif rpn <= 15: return 'ORANGE'
    else:           return 'RED'

def risk_label(rpn):
    if rpn <= 4:    return 'Low'
    elif rpn <= 9:  return 'Medium'
    elif rpn <= 15: return 'High'
    else:           return 'Critical'

phases = [
    {'name': 'Pre-Launch',         'start': 0,     'end': 0.5,  'phase_code': 'PL'},
    {'name': 'Launch',             'start': 0.5,   'end': 2.5,  'phase_code': 'LA'},
    {'name': 'Earth_Orbit',        'start': 2.5,   'end': 3.5,  'phase_code': 'EO'},
    {'name': 'TLI_Burn',           'start': 3.5,   'end': 4.0,  'phase_code': 'TLI'},
    {'name': 'Translunar_Coast',   'start': 4.0,   'end': 55.9, 'phase_code': 'TLC'},
    {'name': 'O2_Tank_Explosion',  'start': 55.9,  'end': 56.1, 'phase_code': 'EXP'},
    {'name': 'Emergency_Response', 'start': 56.1,  'end': 61.0, 'phase_code': 'EMG'},
    {'name': 'Lifeboat_Coast',     'start': 61.0,  'end': 105.0,'phase_code': 'LBC'},
    {'name': 'Lunar_Flyby',        'start': 105.0, 'end': 110.0,'phase_code': 'LFB'},
    {'name': 'Return_Coast',       'start': 110.0, 'end': 138.0,'phase_code': 'RC'},
    {'name': 'CM_Power_Up',        'start': 138.0, 'end': 141.0,'phase_code': 'CPU'},
    {'name': 'Reentry',            'start': 141.0, 'end': 142.5,'phase_code': 'RE'},
    {'name': 'Splashdown',         'start': 142.5, 'end': 142.9,'phase_code': 'SD'},
]

def get_phase(met):
    for p in phases:
        if p['start'] <= met <= p['end']:
            return p['name'], p['phase_code']
    return 'Unknown', 'UNK'

fire_hazard_types = [
    'ELECTRICAL_ARC',
    'OXYGEN_ENRICHED_COMBUSTION',
    'CRYOGENIC_FUEL_LEAK',
    'THERMAL_RUNAWAY',
    'PYROTECHNIC_IGNITION',
    'HYPERGOLIC_PROPELLANT_REACTION',
    'WIRING_INSULATION_BURN',
    'PRESSURE_VESSEL_RUPTURE_FIRE',
]

stir_times = [10.5, 23.1, 38.7, 55.5, 55.85]

def simulate_fire_risk(met):
    phase_name, phase_code = get_phase(met)
    noise = random.uniform(-0.3, 0.3)

    if met < 0.5:
        sev = 2; lik = 2
        ft = 'ELECTRICAL_ARC'
        notes = 'Ground support systems active, standard pre-launch check'

    elif met < 2.5:
        t = (met - 0.5) / 2.0
        sev = 4 if t < 0.3 else 3
        lik = max(1, min(5, int(3 + 2*math.exp(-3*t) + noise)))
        ft = 'PYROTECHNIC_IGNITION' if t < 0.5 else 'THERMAL_RUNAWAY'
        notes = 'Max-Q region, ascent phase t+' + str(round(t*2, 1)) + 'h'

    elif met < 4.0:
        sev = 3; lik = 2
        ft = 'HYPERGOLIC_PROPELLANT_REACTION'
        notes = 'TLI burn - engine ignition window'

    elif met < 55.9:
        t = (met - 4.0) / (55.9 - 4.0)
        o2_risk = 1.0 + 2.5 * (t**2)
        sev = max(1, min(4, int(2 + o2_risk * 0.5 + noise * 0.5)))
        lik = max(1, min(5, int(1 + o2_risk + noise * 0.3)))
        ft = 'OXYGEN_ENRICHED_COMBUSTION' if t > 0.6 else 'WIRING_INSULATION_BURN'
        near_stir = any(abs(met - st) < 0.3 for st in stir_times)
        if near_stir:
            lik = min(5, lik + 1)
            notes = 'O2 cryo stir procedure - agitation of tank contents'
        else:
            notes = 'Translunar coast - O2 tank pressure monitoring t=' + str(round(t, 3))

    elif met < 56.1:
        sev = 4; lik = 5
        ft = 'OXYGEN_ENRICHED_COMBUSTION'
        notes = 'CRITICAL INCIDENT: O2 Tank No.2 explosion - Teflon insulation ignition in pure O2 environment. MET 55:54:53. SM Bay 4 destroyed.'

    elif met < 61.0:
        t = (met - 56.1) / (61.0 - 56.1)
        sev = 4
        lik = max(1, min(5, int(5 - 3*t + noise)))
        ft = 'CRYOGENIC_FUEL_LEAK' if t < 0.5 else 'PRESSURE_VESSEL_RUPTURE_FIRE'
        notes = 'Emergency response - LM lifeboat activation. Post-explosion +' + str(round((met-56.1)*60, 1)) + 'min'

    elif met < 105.0:
        t = (met - 61.0) / (105.0 - 61.0)
        sev = max(2, min(4, int(3 + math.sin(t*math.pi) * 0.5 + noise * 0.3)))
        lik = max(1, min(4, int(2 + t + noise * 0.5)))
        ft = 'ELECTRICAL_ARC'
        notes = 'LM lifeboat coast - power conservation mode, ' + str(round(100*(1-t), 1)) + '% mission elapsed'

    elif met < 110.0:
        sev = 3; lik = 2
        ft = 'PYROTECHNIC_IGNITION'
        notes = 'PC+2 burn - trajectory correction near Moon'

    elif met < 138.0:
        t = (met - 110.0) / (138.0 - 110.0)
        sev = max(1, min(3, int(2 + math.sin(t*math.pi*2)*0.5 + noise*0.3)))
        lik = max(1, min(3, int(2 + noise*0.5)))
        ft = 'ELECTRICAL_ARC'
        notes = 'Return coast - power budget critical, ' + str(round(t*100, 1)) + '% return elapsed'

    elif met < 141.0:
        sev = 3; lik = 3
        ft = 'ELECTRICAL_ARC'
        notes = 'Command Module powered up on emergency protocol - LM abort'

    elif met < 142.5:
        t = (met - 141.0) / 1.5
        sev = 4
        lik = max(1, min(4, int(3 - 2*t + noise*0.5)))
        ft = 'THERMAL_RUNAWAY'
        notes = 'Reentry heating phase - max surface temp 5000F, ' + str(round(t*100, 1)) + '% complete'

    else:
        sev = 1; lik = 1
        ft = 'ELECTRICAL_ARC'
        notes = 'Splashdown - April 17, 1970 18:07:41 UTC. MISSION COMPLETE.'

    sev = max(1, min(4, sev))
    lik = max(1, min(5, lik))
    return sev, lik, ft, notes, phase_name, phase_code

met_times = [i * TOTAL_MET_HOURS / (N_POINTS - 1) for i in range(N_POINTS)]

simulation_data = []
for idx, met in enumerate(met_times):
    sev, lik, ft, notes, phase_name, phase_code = simulate_fire_risk(met)
    rpn = sev * lik

    if met < 55.9:
        o2_pressure = 900 - 2*met + random.uniform(-5, 5)
        if met > 50:
            o2_pressure += (met - 50) * 15
    elif met < 56.1:
        o2_pressure = max(0, 900 - (met - 55.9) * 9000 + random.uniform(-10, 10))
    else:
        o2_pressure = max(0, 850 - (met - 56.1) * 10 + random.uniform(-5, 5))

    if met < 56.0:
        o2_pct = 20.9 + random.uniform(-0.1, 0.1)
    elif met < 60.0:
        o2_pct = max(18.0, 20.9 - (met - 56.0) * 0.5 + random.uniform(-0.2, 0.2))
    else:
        o2_pct = 18.5 + random.uniform(-0.3, 0.3)

    if met < 2.5:
        temp = 450 + random.uniform(-20, 20)
    elif met > 141.0 and met < 142.5:
        t = (met - 141.0) / 1.5
        temp = 300 + t * 4700 + random.uniform(-50, 50)
    else:
        temp = 68 + random.uniform(-5, 5)

    point = {
        'data_point_id': idx + 1,
        'met_hours': round(met, 4),
        'met_minutes': round(met * 60, 2),
        'mission_phase': phase_name,
        'phase_code': phase_code,
        'fire_risk': {
            'severity': sev,
            'severity_label': severity_label(sev),
            'likelihood': lik,
            'likelihood_label': likelihood_label(lik),
            'risk_priority_number': rpn,
            'risk_level': risk_label(rpn),
            'risk_color': risk_color(rpn),
            'fire_hazard_type': ft,
            'notes': notes
        },
        'sensor_readings': {
            'o2_tank2_pressure_psi': round(max(0, o2_pressure), 2),
            'cabin_o2_percentage': round(min(21.0, o2_pct), 3),
            'sm_bay4_temperature_F': round(temp, 1),
            'is_explosion_event': (met >= 55.87 and met <= 56.0),
        }
    }
    simulation_data.append(point)

nasa_risk_matrix = {
    'matrix_type': '5x4_NASA_Standard',
    'version': 'NPR_8715.3C',
    'severity_scale': [
        {'level': 1, 'label': 'Negligible',    'description': 'No injury, negligible system damage'},
        {'level': 2, 'label': 'Marginal',       'description': 'Minor injury, minor system damage'},
        {'level': 3, 'label': 'Critical',       'description': 'Severe injury, major system damage, mission abort'},
        {'level': 4, 'label': 'Catastrophic',   'description': 'Loss of life or spacecraft'},
    ],
    'likelihood_scale': [
        {'level': 1, 'label': 'Improbable',  'probability': '<0.1%'},
        {'level': 2, 'label': 'Remote',      'probability': '0.1%-1%'},
        {'level': 3, 'label': 'Occasional',  'probability': '1%-10%'},
        {'level': 4, 'label': 'Probable',    'probability': '10%-50%'},
        {'level': 5, 'label': 'Frequent',    'probability': '>50%'},
    ],
    'risk_zones': {
        'GREEN':  {'rpn_range': '1-4',  'action': 'Acceptable - Monitor'},
        'YELLOW': {'rpn_range': '5-9',  'action': 'Review Required'},
        'ORANGE': {'rpn_range': '10-15','action': 'Mitigation Required'},
        'RED':    {'rpn_range': '16-20','action': 'Unacceptable - Mission Hold'},
    }
}

key_events = [
    {'met_hours': 0.0,   'event': 'Launch - Saturn V ignition',              'fire_type': 'PYROTECHNIC_IGNITION'},
    {'met_hours': 0.17,  'event': 'Max-Q (maximum aerodynamic pressure)',    'fire_type': 'THERMAL_RUNAWAY'},
    {'met_hours': 2.5,   'event': 'Earth orbit insertion',                   'fire_type': 'HYPERGOLIC_PROPELLANT_REACTION'},
    {'met_hours': 3.5,   'event': 'TLI burn - Trans Lunar Injection',        'fire_type': 'HYPERGOLIC_PROPELLANT_REACTION'},
    {'met_hours': 10.5,  'event': 'First O2 tank cryo stir',                 'fire_type': 'WIRING_INSULATION_BURN'},
    {'met_hours': 23.1,  'event': 'Second O2 tank cryo stir',                'fire_type': 'WIRING_INSULATION_BURN'},
    {'met_hours': 38.7,  'event': 'Third O2 tank cryo stir',                 'fire_type': 'WIRING_INSULATION_BURN'},
    {'met_hours': 55.5,  'event': 'Pre-explosion: abnormal O2 pressure',     'fire_type': 'OXYGEN_ENRICHED_COMBUSTION'},
    {'met_hours': 55.92, 'event': 'EXPLOSION: O2 Tank No.2 rupture',        'fire_type': 'OXYGEN_ENRICHED_COMBUSTION'},
    {'met_hours': 56.1,  'event': 'LM Aquarius activated as lifeboat',       'fire_type': 'CRYOGENIC_FUEL_LEAK'},
    {'met_hours': 61.0,  'event': 'PC+2 burn - trajectory correction',       'fire_type': 'HYPERGOLIC_PROPELLANT_REACTION'},
    {'met_hours': 105.0, 'event': 'Lunar flyby at 254km altitude',           'fire_type': 'PYROTECHNIC_IGNITION'},
    {'met_hours': 138.0, 'event': 'CM Odyssey powered up - emergency proc',  'fire_type': 'ELECTRICAL_ARC'},
    {'met_hours': 141.3, 'event': 'LM Aquarius jettisoned',                  'fire_type': 'PYROTECHNIC_IGNITION'},
    {'met_hours': 141.5, 'event': 'Reentry begins - 400,000 ft altitude',    'fire_type': 'THERMAL_RUNAWAY'},
    {'met_hours': 142.9, 'event': 'Splashdown - South Pacific Ocean',        'fire_type': None},
]

phase_stats = {}
for point in simulation_data:
    ph = point['mission_phase']
    if ph not in phase_stats:
        phase_stats[ph] = {'count': 0, 'sum_rpn': 0, 'max_rpn': 0, 'min_rpn': 20, 'fire_types': {}}
    rpn = point['fire_risk']['risk_priority_number']
    ft = point['fire_risk']['fire_hazard_type']
    phase_stats[ph]['count'] += 1
    phase_stats[ph]['sum_rpn'] += rpn
    phase_stats[ph]['max_rpn'] = max(phase_stats[ph]['max_rpn'], rpn)
    phase_stats[ph]['min_rpn'] = min(phase_stats[ph]['min_rpn'], rpn)
    phase_stats[ph]['fire_types'][ft] = phase_stats[ph]['fire_types'].get(ft, 0) + 1

phase_summary = []
for ph, stats in phase_stats.items():
    phase_summary.append({
        'phase': ph,
        'data_points': stats['count'],
        'avg_rpn': round(stats['sum_rpn'] / stats['count'], 2),
        'max_rpn': stats['max_rpn'],
        'min_rpn': stats['min_rpn'],
        'dominant_fire_type': max(stats['fire_types'], key=stats['fire_types'].get)
    })

output = {
    'metadata': {
        'title': 'NASA Fire Risk Matrix Simulation - Apollo 13',
        'mission': 'Apollo 13',
        'launch_date': '1970-04-11T19:13:00Z',
        'splashdown_date': '1970-04-17T18:07:41Z',
        'total_met_hours': TOTAL_MET_HOURS,
        'total_data_points': N_POINTS,
        'simulation_version': '1.0.0',
        'standard': 'NASA-STD-8719.13 / NPR 8715.3C',
        'generated_by': 'NASA Fire Risk Simulation Engine',
        'description': 'Simulated evolution of fire risk categories across Apollo 13 mission timeline based on NASA 5x4 Risk Matrix. Each data point samples fire hazard type, severity, likelihood, and sensor readings at a given mission elapsed time (MET).'
    },
    'nasa_fire_risk_matrix': nasa_risk_matrix,
    'mission_phases': phases,
    'key_events': key_events,
    'fire_hazard_type_descriptions': {
        'ELECTRICAL_ARC':                 'Electrical spark or arc causing ignition in spacecraft environment',
        'OXYGEN_ENRICHED_COMBUSTION':     'Fire in pure or enriched O2 atmosphere - extreme burn rate',
        'CRYOGENIC_FUEL_LEAK':            'Leaked cryogenic propellant contacting ignition source',
        'THERMAL_RUNAWAY':                'Uncontrolled heating causing cascading combustion',
        'PYROTECHNIC_IGNITION':           'Planned or unplanned activation of explosive ordnance',
        'HYPERGOLIC_PROPELLANT_REACTION': 'Self-igniting propellant leak (N2O4 / Aerozine-50)',
        'WIRING_INSULATION_BURN':         'Teflon or wiring insulation burning in O2 environment',
        'PRESSURE_VESSEL_RUPTURE_FIRE':   'Pressurized vessel failure followed by combustion',
    },
    'phase_statistics': phase_summary,
    'simulation_data': simulation_data
}

out_path = r'c:\Users\Nasrallah\Downloads\chat-812c8388-89f0-4c7c-88f6-7e872379485d\apollo13_fire_risk_simulation.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

file_size = len(json.dumps(output))
print("Done! Generated", N_POINTS, "data points")
print("File:", out_path)
print("File size:", round(file_size/1024, 1), "KB")
print("")
print("Phase Summary:")
for ps in phase_summary:
    print("  Phase:", ps['phase'], "| avg_RPN:", ps['avg_rpn'], "| max:", ps['max_rpn'], "| type:", ps['dominant_fire_type'])
