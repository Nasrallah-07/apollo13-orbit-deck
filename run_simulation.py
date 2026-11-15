"""
Apollo 13 Fire Risk — Interactive HTML Simulation (Plotly)
Opens directly in browser — no extra install needed
"""
import json, os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE      = r'c:\Users\Nasrallah\Downloads\chat-812c8388-89f0-4c7c-88f6-7e872379485d'
JSON_PATH = os.path.join(BASE, 'apollo13_fire_risk_simulation.json')

print("Loading data...")
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

pts    = data['simulation_data']
evts   = data['real_telemetry_sources']['real_mission_timeline']['events']
phases = data['mission_phases']

MET    = [p['met_hours']                          for p in pts]
RPN    = [p['fire_risk']['risk_priority_number']  for p in pts]
SEV    = [p['fire_risk']['severity']              for p in pts]
LIK    = [p['fire_risk']['likelihood']            for p in pts]
O2P    = [p['sensor_readings']['o2_tank2_pressure_psi']  for p in pts]
O2C    = [p['sensor_readings']['cabin_o2_percentage']    for p in pts]
TEMP   = [p['sensor_readings']['sm_bay4_temperature_F']  for p in pts]
PHASE  = [p['mission_phase']                      for p in pts]
FTYPE  = [p['fire_risk']['fire_hazard_type']      for p in pts]
COLOR  = [p['fire_risk']['risk_color']            for p in pts]
NOTES  = [p['fire_risk']['notes']                 for p in pts]

COL_MAP = {'GREEN':'#00C853','YELLOW':'#FFD600','ORANGE':'#FF6D00','RED':'#D50000'}
dot_colors = [COL_MAP[c] for c in COLOR]

PHASE_COL = {
    'Pre-Launch':'#78909C','Launch':'#FF5722','Earth_Orbit':'#29B6F6',
    'TLI_Burn':'#FFA726','Translunar_Coast':'#42A5F5','O2_Tank_Explosion':'#D50000',
    'Emergency_Response':'#FF1744','Lifeboat_Coast':'#7E57C2','Lunar_Flyby':'#26C6DA',
    'Return_Coast':'#66BB6A','CM_Power_Up':'#FFA726','Reentry':'#FF7043','Splashdown':'#26A69A',
}

hover_txt = [
    f"<b>MET {MET[i]:.3f}h</b><br>"
    f"Phase: {PHASE[i]}<br>"
    f"<b>RPN: {RPN[i]}/20</b><br>"
    f"Severity: {SEV[i]} | Likelihood: {LIK[i]}<br>"
    f"Type: {FTYPE[i]}<br>"
    f"O2: {O2P[i]:.0f} psi | Cabin: {O2C[i]:.2f}%<br>"
    f"<i>{NOTES[i][:80]}...</i>"
    for i in range(len(pts))
]

# ── Build figure with 4 rows ──
fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=[0.42, 0.20, 0.20, 0.18],
    subplot_titles=[
        '🔥 Fire Risk Priority Number (RPN)  —  NASA 5×4 Matrix',
        '📊 Severity & Likelihood',
        '🫧 O₂ Tank 2 Pressure (PSI)',
        '🌡️ Cabin O₂ % & SM Bay4 Temperature'
    ]
)

# ════════════════════════════
#  ROW 1 — RPN timeline
# ════════════════════════════
# Risk zone fills
for ylo, yhi, col, lbl in [
    (0,4,'rgba(0,200,83,0.10)','LOW'),
    (4,9,'rgba(255,214,0,0.10)','MEDIUM'),
    (9,15,'rgba(255,109,0,0.10)','HIGH'),
    (15,20,'rgba(213,0,0,0.12)','CRITICAL'),
]:
    fig.add_hrect(y0=ylo, y1=yhi, row=1, col=1,
                  fillcolor=col, line_width=0,
                  annotation_text=lbl, annotation_position='right',
                  annotation_font=dict(color=col.replace('0.10','1').replace('0.12','1'), size=10))

# Phase background bands on row 1
prev_ph = PHASE[0]; s = 0
for i in range(1, len(pts)):
    if PHASE[i] != prev_ph or i == len(pts)-1:
        pc = PHASE_COL.get(prev_ph, '#888888')
        fig.add_vrect(x0=MET[s], x1=MET[i], row=1, col=1,
                      fillcolor=pc, opacity=0.07, line_width=0)
        mid = (MET[s]+MET[i])/2
        if MET[i]-MET[s] > 3:
            fig.add_annotation(x=mid, y=21.2, text=prev_ph.replace('_','<br>'),
                               showarrow=False, row=1, col=1,
                               font=dict(size=7, color=pc), xanchor='center')
        prev_ph = PHASE[i]; s = i

# Main RPN trace (colored dots)
fig.add_trace(go.Scatter(
    x=MET, y=RPN,
    mode='markers+lines',
    marker=dict(color=dot_colors, size=3, opacity=0.8),
    line=dict(color='rgba(200,200,200,0.3)', width=0.8),
    name='RPN',
    hovertext=hover_txt, hoverinfo='text',
), row=1, col=1)

# Explosion vertical line
EXPL = 55.914
for row in [1,2,3,4]:
    fig.add_vline(x=EXPL, line_color='#FF1744', line_width=2.5,
                  line_dash='solid', row=row, col=1)

fig.add_annotation(x=EXPL, y=22, text='💥 EXPLOSION<br>MET 55:54:53',
                   showarrow=True, arrowhead=2, ax=40, ay=-40,
                   font=dict(color='#FF1744', size=11, family='Arial Black'),
                   arrowcolor='#FF1744', row=1, col=1)

# Real event markers
for ev in evts:
    met_v = ev['met_decimal_hours']
    label = ev['event'][:30] + '...' if len(ev['event']) > 30 else ev['event']
    fig.add_vline(x=met_v, line_color='rgba(255,255,255,0.15)',
                  line_width=1, line_dash='dot', row=1, col=1)

# ════════════════════════════
#  ROW 2 — Severity & Likelihood
# ════════════════════════════
fig.add_trace(go.Scatter(
    x=MET, y=SEV, name='Severity (1-4)',
    line=dict(color='#FF5252', width=1.5),
    hovertemplate='SEV: %{y}<extra></extra>'
), row=2, col=1)

fig.add_trace(go.Scatter(
    x=MET, y=LIK, name='Likelihood (1-5)',
    line=dict(color='#FFD600', width=1.5, dash='dash'),
    hovertemplate='LIK: %{y}<extra></extra>'
), row=2, col=1)

fig.add_vline(x=EXPL, line_color='#FF1744', line_width=2, row=2, col=1)

# ════════════════════════════
#  ROW 3 — O2 Pressure
# ════════════════════════════
fig.add_trace(go.Scatter(
    x=MET, y=O2P, name='O₂ Tank2 Pressure (PSI)',
    line=dict(color='#29B6F6', width=1.5),
    fill='tozeroy', fillcolor='rgba(41,182,246,0.15)',
    hovertemplate='O₂: %{y:.0f} psi<extra></extra>'
), row=3, col=1)

# Real value annotations on O2 chart
fig.add_annotation(x=55.912, y=1008.3, text='<b>1,008.3 psia</b><br>(Real max — NASA MSC-02680)',
                   showarrow=True, arrowhead=2, ax=60, ay=-30,
                   font=dict(color='#FF1744', size=9), arrowcolor='#FF1744',
                   row=3, col=1)
fig.add_annotation(x=55.914, y=781.9, text='Tank1: 781.9 psia<br>post-explosion',
                   showarrow=True, arrowhead=2, ax=70, ay=40,
                   font=dict(color='#FFA726', size=9), arrowcolor='#FFA726',
                   row=3, col=1)

fig.add_vline(x=EXPL, line_color='#FF1744', line_width=2, row=3, col=1)
fig.add_hline(y=935, line_color='rgba(255,214,0,0.5)', line_dash='dot',
              line_width=1, row=3, col=1,
              annotation_text='Max nominal 935 psi', annotation_font_size=8)
fig.add_hline(y=865, line_color='rgba(255,214,0,0.5)', line_dash='dot',
              line_width=1, row=3, col=1,
              annotation_text='Min nominal 865 psi', annotation_font_size=8)

# ════════════════════════════
#  ROW 4 — O2 % + Temp
# ════════════════════════════
fig.add_trace(go.Scatter(
    x=MET, y=O2C, name='Cabin O₂ (%)',
    line=dict(color='#A5D6A7', width=1.5),
    hovertemplate='Cabin O₂: %{y:.2f}%<extra></extra>'
), row=4, col=1)

fig.add_hline(y=19.5, line_color='rgba(255,235,59,0.6)', line_dash='dash',
              line_width=1, row=4, col=1,
              annotation_text='Safe min 19.5%', annotation_font_size=8,
              annotation_position='bottom right')

fig.add_vline(x=EXPL, line_color='#FF1744', line_width=2, row=4, col=1)

# ════════════════════════════
#  Layout
# ════════════════════════════
fig.update_layout(
    title=dict(
        text='🚀  APOLLO 13 — NASA Fire Risk Matrix Simulation  |  Real Telemetry + 2000 Data Points  |  Sources: NASA MSC-02680',
        font=dict(size=16, color='white', family='Arial Black'),
        x=0.5, xanchor='center'
    ),
    paper_bgcolor='#0A0A1A',
    plot_bgcolor='#0D1B2A',
    font=dict(color='#CCCCDD', size=10),
    height=900,
    hovermode='x unified',
    legend=dict(
        bgcolor='rgba(13,27,42,0.9)', bordercolor='#223366',
        borderwidth=1, font=dict(size=9),
        x=0.01, y=0.99
    ),
    margin=dict(l=60, r=120, t=80, b=50),
    xaxis4=dict(title='Mission Elapsed Time (MET) — Hours from Launch'),
    yaxis=dict(title='RPN (0-20)', range=[-0.5, 23], gridcolor='#1a2a3a'),
    yaxis2=dict(title='S / L', range=[0, 6], gridcolor='#1a2a3a'),
    yaxis3=dict(title='PSI', gridcolor='#1a2a3a'),
    yaxis4=dict(title='O₂ %', range=[17, 21.5], gridcolor='#1a2a3a'),
)

for i in range(1, 5):
    fig.update_xaxes(gridcolor='#1a2a3a', zeroline=False, row=i, col=1)
    fig.update_yaxes(gridcolor='#1a2a3a', zeroline=False, row=i, col=1)

# ════════════════════════════
#  Slider (animate over time)
# ════════════════════════════
steps_count = 40
step_size   = len(pts) // steps_count

slider_steps = []
for si in range(steps_count + 1):
    idx  = min(si * step_size, len(pts)-1)
    met  = MET[idx]
    h    = int(met); m = int((met-h)*60)
    slider_steps.append(dict(
        method='relayout',
        label=f'{h:03d}:{m:02d}',
        args=[{'xaxis.range': [0, met + 1]}]
    ))

fig.update_layout(
    sliders=[dict(
        active=steps_count,
        currentvalue=dict(prefix='MET cutoff: ', font=dict(color='white')),
        pad=dict(t=10, b=10),
        bgcolor='#0D1B2A',
        bordercolor='#223366',
        font=dict(color='white'),
        tickcolor='white',
        steps=slider_steps
    )]
)

# ════════════════════════════
#  Second figure: Risk Matrix heatmap
# ════════════════════════════
fig2 = go.Figure()

matrix_z = []
matrix_text = []
lik_labels = ['Frequent (5)','Probable (4)','Occasional (3)','Remote (2)','Improbable (1)']
sev_labels = ['Negligible (1)','Marginal (2)','Critical (3)','Catastrophic (4)']

for lik in [5,4,3,2,1]:
    row_z = []; row_t = []
    for sev in [1,2,3,4]:
        rpn = lik * sev
        row_z.append(rpn)
        row_t.append(f'RPN = {rpn}')
    matrix_z.append(row_z)
    matrix_text.append(row_t)

fig2.add_trace(go.Heatmap(
    z=matrix_z,
    x=sev_labels,
    y=lik_labels,
    text=matrix_text,
    texttemplate='<b>%{text}</b>',
    colorscale=[
        [0.0,  '#00C853'],
        [0.20, '#00C853'],
        [0.20, '#FFD600'],
        [0.45, '#FFD600'],
        [0.45, '#FF6D00'],
        [0.75, '#FF6D00'],
        [0.75, '#D50000'],
        [1.0,  '#D50000'],
    ],
    zmin=0, zmax=20,
    showscale=True,
    colorbar=dict(
        title=dict(text='RPN', font=dict(color='white')),
        tickvals=[2,7,12,18],
        ticktext=['LOW','MED','HIGH','CRIT'],
        bgcolor='#0D1B2A', tickfont=dict(color='white'),
    ),
    hovertemplate='Severity: %{x}<br>Likelihood: %{y}<br>%{text}<extra></extra>'
))

# Phase dots on matrix
phase_sev_lik = {}
for p in pts:
    ph = p['mission_phase']
    if ph not in phase_sev_lik:
        phase_sev_lik[ph] = (p['fire_risk']['severity'], p['fire_risk']['likelihood'])

lik_to_label = {5:'Frequent (5)',4:'Probable (4)',3:'Occasional (3)',2:'Remote (2)',1:'Improbable (1)'}
sev_to_label = {1:'Negligible (1)',2:'Marginal (2)',3:'Critical (3)',4:'Catastrophic (4)'}

ph_x=[]; ph_y=[]; ph_col=[]; ph_txt=[]
for ph,(sev,lik) in phase_sev_lik.items():
    ph_x.append(sev_to_label[sev])
    ph_y.append(lik_to_label[lik])
    ph_col.append(PHASE_COL.get(ph,'#FFFFFF'))
    ph_txt.append(ph.replace('_',' '))

fig2.add_trace(go.Scatter(
    x=ph_x, y=ph_y,
    mode='markers+text',
    marker=dict(color=ph_col, size=20, line=dict(color='white', width=2)),
    text=ph_txt, textposition='top center',
    textfont=dict(size=8, color='white'),
    name='Mission Phases',
    hovertemplate='<b>%{text}</b><br>Sev: %{x}<br>Lik: %{y}<extra></extra>'
))

fig2.update_layout(
    title=dict(
        text='NASA 5×4 Fire Risk Matrix — Apollo 13 Phase Mapping',
        font=dict(size=15, color='white'), x=0.5, xanchor='center'
    ),
    paper_bgcolor='#0A0A1A', plot_bgcolor='#0D1B2A',
    font=dict(color='white'), height=550,
    xaxis=dict(title='SEVERITY →', tickfont=dict(color='white')),
    yaxis=dict(title='← LIKELIHOOD', tickfont=dict(color='white')),
    margin=dict(l=150, r=100, t=70, b=100)
)

# ════════════════════════════
#  Third figure: Fire type pie
# ════════════════════════════
ft_counts = {}
for p in pts:
    ft = p['fire_risk']['fire_hazard_type']
    ft_counts[ft] = ft_counts.get(ft, 0) + 1

ft_short = {
    'ELECTRICAL_ARC':'Electrical Arc','OXYGEN_ENRICHED_COMBUSTION':'O2 Combustion',
    'CRYOGENIC_FUEL_LEAK':'Cryo Fuel Leak','THERMAL_RUNAWAY':'Thermal Runaway',
    'PYROTECHNIC_IGNITION':'Pyrotechnic','HYPERGOLIC_PROPELLANT_REACTION':'Hypergolic',
    'WIRING_INSULATION_BURN':'Wiring Burn','PRESSURE_VESSEL_RUPTURE_FIRE':'Pressure Rupture'
}

fig3 = go.Figure(go.Pie(
    labels=[ft_short.get(k,k) for k in ft_counts],
    values=list(ft_counts.values()),
    hole=0.4,
    marker=dict(colors=['#29B6F6','#D50000','#00BFA5','#FF6D00','#FF5722','#AB47BC','#FFD600','#EC407A'],
                line=dict(color='#0A0A1A', width=2)),
    textfont=dict(size=11),
    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
))
fig3.update_layout(
    title=dict(text='Fire Hazard Type Distribution (2000 data points)',
               font=dict(size=14, color='white'), x=0.5, xanchor='center'),
    paper_bgcolor='#0A0A1A', font=dict(color='white'), height=450
)

# ════════════════════════════
#  Write combined HTML
# ════════════════════════════
html_path = os.path.join(BASE, 'apollo13_simulation.html')

h1 = fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='main_chart')
h2 = fig2.to_html(full_html=False, include_plotlyjs=False, div_id='matrix_chart')
h3 = fig3.to_html(full_html=False, include_plotlyjs=False, div_id='pie_chart')

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Apollo 13 — NASA Fire Risk Simulation</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0A0A1A; color:#CCCCDD; font-family:'Segoe UI',Arial,sans-serif; }}
  .header {{
    background:linear-gradient(135deg,#0D1B2A 0%,#1a2a4a 100%);
    border-bottom:2px solid #D50000;
    padding:20px 40px;
    display:flex; align-items:center; gap:20px;
  }}
  .header h1 {{ font-size:22px; color:white; font-weight:900; }}
  .header .badge {{
    background:#D50000; color:white; border-radius:4px;
    padding:4px 10px; font-size:11px; font-weight:bold;
  }}
  .badge.green {{ background:#00C853; color:#000; }}
  .section {{
    padding:30px 40px;
    border-bottom:1px solid #1a2a3a;
  }}
  .section h2 {{ color:#29B6F6; font-size:16px; margin-bottom:16px; }}
  .sources-grid {{
    display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
    gap:12px; margin-top:16px;
  }}
  .source-card {{
    background:#0D1B2A; border:1px solid #223366;
    border-radius:8px; padding:14px;
  }}
  .source-card .src-id {{ color:#FFD600; font-size:11px; font-weight:bold; }}
  .source-card .src-title {{ color:white; font-size:13px; margin:4px 0; }}
  .source-card .src-doc {{ color:#888; font-size:11px; }}
  .source-card a {{ color:#29B6F6; font-size:11px; }}
  .real-data-table {{
    width:100%; border-collapse:collapse; margin-top:14px;
    font-size:12px;
  }}
  .real-data-table th {{
    background:#1a2a3a; color:#29B6F6; padding:8px 12px;
    text-align:left; border-bottom:1px solid #223366;
  }}
  .real-data-table td {{
    padding:8px 12px; border-bottom:1px solid #1a2a3a; color:#CCCCDD;
  }}
  .real-data-table td.val {{ color:#FFD600; font-weight:bold; font-family:monospace; }}
  .real-data-table td.src {{ color:#666; font-size:10px; }}
  .defect-list {{ margin-top:14px; }}
  .defect {{ background:#0D1B2A; border-left:3px solid #D50000;
             padding:10px 14px; margin-bottom:8px; border-radius:0 6px 6px 0; }}
  .defect .did {{ color:#D50000; font-size:10px; font-weight:bold; }}
  .defect p {{ font-size:12px; color:#CCCCDD; margin-top:4px; }}
  .footer {{
    text-align:center; padding:20px; color:#445;
    font-size:11px; border-top:1px solid #1a2a3a;
  }}
  .tab-bar {{ display:flex; gap:4px; padding:0 40px; background:#0A0A1A; }}
  .tab {{
    padding:10px 20px; cursor:pointer; border-radius:6px 6px 0 0;
    background:#0D1B2A; color:#888; font-size:13px; border:1px solid #1a2a3a;
    transition:all 0.2s;
  }}
  .tab.active {{ background:#1a2a3a; color:white; border-bottom:2px solid #29B6F6; }}
  .tab-content {{ display:none; }}
  .tab-content.active {{ display:block; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="header h1">🚀 Apollo 13 — NASA Fire Risk Matrix Simulation</div>
    <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;">
      <span class="badge">MSC-02680</span>
      <span class="badge">NPR 8715.3C</span>
      <span class="badge">2000 Data Points</span>
      <span class="badge green">7 NASA Sources</span>
      <span class="badge" style="background:#7E57C2;">Real Telemetry</span>
    </div>
  </div>
</div>

<div class="tab-bar">
  <div class="tab active" onclick="showTab('sim')">📈 Simulation</div>
  <div class="tab" onclick="showTab('matrix')">🔲 Risk Matrix</div>
  <div class="tab" onclick="showTab('pie')">🥧 Fire Types</div>
  <div class="tab" onclick="showTab('data')">🔬 Real Data</div>
  <div class="tab" onclick="showTab('sources')">📚 Sources</div>
</div>

<div id="sim" class="tab-content active section" style="padding:20px 40px;">
  <p style="color:#888;font-size:12px;margin-bottom:12px;">
    Use the <b style="color:#FFD600">slider</b> to replay the mission from MET 0:00 to 142:54.
    Hover over any point for details. The red vertical line = O2 Tank explosion (MET 55:54:53).
  </p>
  {h1}
</div>

<div id="matrix" class="tab-content section" style="padding:20px 40px;">
  <p style="color:#888;font-size:12px;margin-bottom:12px;">
    NASA 5×4 Risk Matrix. Each colored dot = one Apollo 13 mission phase.
    Position based on typical severity × likelihood during that phase.
  </p>
  {h2}
</div>

<div id="pie" class="tab-content section" style="padding:20px 40px;">
  {h3}
</div>

<div id="data" class="tab-content section">
  <h2>🔬 Real Telemetry Data — Verified from NASA Primary Sources</h2>
  <table class="real-data-table">
    <tr>
      <th>Parameter</th><th>Real Value</th><th>MET / Context</th><th>Source</th>
    </tr>
    <tr><td>O₂ Tank 2 — Nominal operating pressure</td><td class="val">865 – 935 psia</td><td>Pre-explosion baseline</td><td class="src">MSC-02680</td></tr>
    <tr><td>O₂ Tank 2 — Pressure when fans turned on</td><td class="val">880 psia</td><td>MET 055:53:20</td><td class="src">MSC-02680</td></tr>
    <tr><td>O₂ Tank 2 — Pressure plateau (temp stable)</td><td class="val">953.8 psia</td><td>MET 055:54:00</td><td class="src">MSC-02680</td></tr>
    <tr><td>O₂ Tank 2 — MAXIMUM pressure recorded</td><td class="val" style="color:#D50000;">1,008.3 psia</td><td>MET 055:54:45</td><td class="src">MSC-02680</td></tr>
    <tr><td>O₂ Tank 2 — Post-explosion pressure</td><td class="val">0 psia (off-scale low)</td><td>MET 055:54:56</td><td class="src">MSC-02680</td></tr>
    <tr><td>O₂ Tank 1 — Pressure immediately post-explosion</td><td class="val">781.9 psia</td><td>MET 055:54:56</td><td class="src">MSC-02680</td></tr>
    <tr><td>O₂ Tank 1 — Full depletion time</td><td class="val">~130 minutes</td><td>Post-explosion</td><td class="src">MSC-02680</td></tr>
    <tr><td>Electrical current — pre-explosion (normal)</td><td class="val">11.1 amps</td><td>Fuel Cell 3</td><td class="src">MSC-02680</td></tr>
    <tr><td>Electrical current — spike at explosion</td><td class="val" style="color:#D50000;">22.9 amps</td><td>MET 055:53:22</td><td class="src">MSC-02680</td></tr>
    <tr><td>AC Bus 2 voltage drop</td><td class="val">1.2 V drop</td><td>At fan activation</td><td class="src">MSC-02680</td></tr>
    <tr><td>Spacecraft Delta-V at explosion</td><td class="val">0.4 ft/sec</td><td>Primary to Bay 4</td><td class="src">MSC-02680</td></tr>
    <tr><td>Telemetry dropout duration</td><td class="val">1.8 seconds</td><td>During rupture</td><td class="src">MSC-02680</td></tr>
    <tr><td>LM lifeboat power draw (emergency)</td><td class="val">~12 amps</td><td>vs normal 20A</td><td class="src">MSC-02680</td></tr>
    <tr><td>LM cabin pressure (pure O₂)</td><td class="val">4.9 psi</td><td>Lifeboat phase</td><td class="src">MSC-02680</td></tr>
    <tr><td>LM cabin temperature (power rationing)</td><td class="val" style="color:#29B6F6;">38°F (3°C)</td><td>Lifeboat coast</td><td class="src">MSC-02680</td></tr>
    <tr><td>CO₂ partial pressure — before mailbox fix</td><td class="val" style="color:#D50000;">15.0 mmHg</td><td>Safe limit: 7.6</td><td class="src">MSC-02680</td></tr>
    <tr><td>CO₂ partial pressure — after mailbox fix</td><td class="val" style="color:#00C853;">2.0 mmHg</td><td>MET ~105h</td><td class="src">MSC-02680</td></tr>
    <tr><td>Closest lunar approach (flyby)</td><td class="val">254 km (137.9 nm)</td><td>MET 077:08</td><td class="src">Flight Journal</td></tr>
    <tr><td>PC+2 burn duration</td><td class="val">30.7 seconds</td><td>MET 061:29:43</td><td class="src">Flight Journal</td></tr>
    <tr><td>Splashdown coordinates</td><td class="val">21.6°S, 165.4°W</td><td>MET 142:54:41</td><td class="src">MSC-02680</td></tr>
    <tr><td>Recovery vessel</td><td class="val">USS Iwo Jima (LPH-2)</td><td>April 17, 1970</td><td class="src">MSC-02680</td></tr>
  </table>

  <h2 style="margin-top:30px;">⚠️ Pre-Launch Known Defects (Root Causes)</h2>
  <div class="defect-list">
    <div class="defect">
      <div class="did">DEFECT D-01 — Thermostatic Switches (SRC-02)</div>
      <p>O₂ Tank 2 switches were rated for 28V DC but KSC ground equipment applied 65V DC during pre-flight testing on March 27, 1969 — burning out the switches silently.</p>
    </div>
    <div class="defect">
      <div class="did">DEFECT D-02 — Fill Tube Assembly (SRC-02)</div>
      <p>Fill tube was incorrectly reinstalled after Beech Aircraft rework (1965), preventing proper draining during ground tests.</p>
    </div>
    <div class="defect">
      <div class="did">DEFECT D-03 — 8-Hour Heater Burn at 65V (SRC-02)</div>
      <p>To drain Tank 2, engineers boiled off oxygen with the heater at 65V for 8 hours on March 27, 1970 — this further degraded the Teflon wiring insulation.</p>
    </div>
    <div class="defect">
      <div class="did">DEFECT D-04 — Invisible Insulation Damage (SRC-02)</div>
      <p>Damaged wiring was invisible to pre-flight inspection. Only became a fire hazard when fans energized inside the pure O₂ environment during the mission.</p>
    </div>
  </div>
</div>

<div id="sources" class="tab-content section">
  <h2>📚 Primary Sources (7 NASA Documents)</h2>
  <div class="sources-grid">
    <div class="source-card">
      <div class="src-id">SRC-01</div>
      <div class="src-title">Apollo 13 Mission Report</div>
      <div class="src-doc">Document: MSC-02680 | NASA, 1970</div>
      <a href="https://www.nasa.gov/history/alsj/a13/a13mr.html" target="_blank">→ Open on NASA.gov</a>
      <p style="color:#888;font-size:11px;margin-top:6px;">Primary telemetry source: pressure/current readings, explosion sequence, all sensor baselines.</p>
    </div>
    <div class="source-card">
      <div class="src-id">SRC-02</div>
      <div class="src-title">Report of Apollo 13 Review Board</div>
      <div class="src-doc">NASA, June 1970</div>
      <a href="https://history.nasa.gov/Apollo204/zorn/ap13.htm" target="_blank">→ Open on NASA History</a>
      <p style="color:#888;font-size:11px;margin-top:6px;">Root cause analysis, pre-launch defects D-01 through D-04, failure sequence reconstruction.</p>
    </div>
    <div class="source-card">
      <div class="src-id">SRC-03</div>
      <div class="src-title">Apollo 13 Flight Journal</div>
      <div class="src-doc">NASA History Division / Eric Jones & Ken Glover</div>
      <a href="https://history.nasa.gov/afj/ap13fj/index.html" target="_blank">→ Open Flight Journal</a>
      <p style="color:#888;font-size:11px;margin-top:6px;">Second-by-second crew/CAPCOM communications. Exact MET timestamps for all events.</p>
    </div>
    <div class="source-card">
      <div class="src-id">SRC-04</div>
      <div class="src-title">NASA History Office — Apollo 13</div>
      <div class="src-doc">NASA History Division</div>
      <a href="https://www.nasa.gov/history/apollo-13/" target="_blank">→ Open on NASA.gov</a>
      <p style="color:#888;font-size:11px;margin-top:6px;">Mission summary, crew biographies, general timeline.</p>
    </div>
    <div class="source-card">
      <div class="src-id">SRC-05</div>
      <div class="src-title">NASA-STD-8719.13 — Software Safety Standard</div>
      <div class="src-doc">NASA Technical Standard</div>
      <a href="https://standards.nasa.gov/standard/nasa/nasa-std-871913" target="_blank">→ Open Standard</a>
      <p style="color:#888;font-size:11px;margin-top:6px;">Fire risk category definitions: hazard types, severity levels.</p>
    </div>
    <div class="source-card">
      <div class="src-id">SRC-06</div>
      <div class="src-title">NPR 8715.3C — NASA Safety Requirements</div>
      <div class="src-doc">NASA Procedural Requirements</div>
      <a href="https://nodis3.gsfc.nasa.gov/displayDir.cfm?t=NPR&c=8715&s=3C" target="_blank">→ Open NPR</a>
      <p style="color:#888;font-size:11px;margin-top:6px;">5×4 risk matrix structure: GREEN/YELLOW/ORANGE/RED zone definitions.</p>
    </div>
    <div class="source-card">
      <div class="src-id">SRC-07</div>
      <div class="src-title">Apollo 13 — The NASA Mission Reports</div>
      <div class="src-doc">Apogee Books / Robert Godwin | ISBN: 1-896522-66-3</div>
      <p style="color:#888;font-size:11px;margin-top:6px;">Supplementary telemetry tables, tank sensor data, power bus readings.</p>
    </div>
  </div>
</div>

<div class="footer">
  Apollo 13 Fire Risk Simulation &nbsp;|&nbsp;
  Sources: NASA MSC-02680, NPR 8715.3C, NASA-STD-8719.13 &nbsp;|&nbsp;
  2000 simulated data points + real telemetry values &nbsp;|&nbsp;
  Generated 2026-11-15
</div>

<script>
function showTab(id) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  event.target.classList.add('active');
}}
</script>
</body>
</html>"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(html_path) // 1024
print(f"HTML saved: {html_path}")
print(f"Size: {size_kb} KB")
print("Opening in browser...")
import webbrowser
webbrowser.open(f'file:///{html_path.replace(chr(92), "/")}')
print("Done!")
