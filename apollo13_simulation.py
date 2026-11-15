"""
╔══════════════════════════════════════════════════════════════╗
║       NASA Apollo 13 — Fire Risk Matrix Simulation          ║
║       Based on: NASA-STD-8719.13 / NPR 8715.3C             ║
║       Mission: April 11-17, 1970                           ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import time
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch, FancyArrow
import matplotlib.patheffects as pe

# ─────────────────────────────────────────────
#  LOAD JSON DATA
# ─────────────────────────────────────────────
JSON_PATH = os.path.join(os.path.dirname(__file__), 'apollo13_fire_risk_simulation.json')

print("🚀 Loading Apollo 13 Fire Risk Simulation Data...")
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    sim_data = json.load(f)

points       = sim_data['simulation_data']
key_events   = sim_data['key_events']
phase_stats  = sim_data['phase_statistics']

N = len(points)
print(f"   ✓ {N} data points loaded")
print(f"   ✓ Mission duration: {sim_data['metadata']['total_met_hours']} hours\n")

# Arrays for fast plotting
MET      = np.array([p['met_hours']                          for p in points])
RPN      = np.array([p['fire_risk']['risk_priority_number']  for p in points])
SEV      = np.array([p['fire_risk']['severity']              for p in points])
LIK      = np.array([p['fire_risk']['likelihood']            for p in points])
O2_PSI   = np.array([p['sensor_readings']['o2_tank2_pressure_psi']  for p in points])
O2_PCT   = np.array([p['sensor_readings']['cabin_o2_percentage']     for p in points])
TEMP_F   = np.array([p['sensor_readings']['sm_bay4_temperature_F']   for p in points])
PHASES   = [p['mission_phase']                               for p in points]
FT       = [p['fire_risk']['fire_hazard_type']               for p in points]
COLORS   = [p['fire_risk']['risk_color']                     for p in points]

COLOR_MAP = {'GREEN': '#00C853', 'YELLOW': '#FFD600', 'ORANGE': '#FF6D00', 'RED': '#D50000'}
PHASE_COLORS = {
    'Pre-Launch':         '#78909C',
    'Launch':             '#FF5722',
    'Earth_Orbit':        '#29B6F6',
    'TLI_Burn':           '#FFA726',
    'Translunar_Coast':   '#42A5F5',
    'O2_Tank_Explosion':  '#D50000',
    'Emergency_Response': '#FF1744',
    'Lifeboat_Coast':     '#7E57C2',
    'Lunar_Flyby':        '#26C6DA',
    'Return_Coast':       '#66BB6A',
    'CM_Power_Up':        '#FFA726',
    'Reentry':            '#FF7043',
    'Splashdown':         '#26A69A',
}

# Explosion index
EXPL_IDX = int(np.argmax(RPN))
EXPL_MET = MET[EXPL_IDX]

# ─────────────────────────────────────────────
#  STEP 1 — Full Timeline Overview (static)
# ─────────────────────────────────────────────
print("=" * 60)
print("  STEP 1/3 — Full Mission Timeline Overview")
print("=" * 60)

fig1, axes = plt.subplots(4, 1, figsize=(16, 11), sharex=True,
                          gridspec_kw={'hspace': 0.08, 'height_ratios': [3, 2, 2, 2]})
fig1.patch.set_facecolor('#0A0A1A')
for ax in axes:
    ax.set_facecolor('#0D1B2A')
    ax.tick_params(colors='#AAAACC', labelsize=8)
    ax.spines['bottom'].set_color('#223366')
    ax.spines['left'].set_color('#223366')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# ── ax0: RPN timeline ──
ax0 = axes[0]
# Color segments
for i in range(len(COLORS) - 1):
    ax0.fill_between([MET[i], MET[i+1]], [RPN[i], RPN[i+1]], [0, 0],
                     color=COLOR_MAP[COLORS[i]], alpha=0.35)
ax0.plot(MET, RPN, color='white', linewidth=0.8, alpha=0.9)

# Key event lines
for ev in key_events:
    met_ev = ev['met_hours']
    ax0.axvline(x=met_ev, color='#FFFFFF', linewidth=0.4, linestyle='--', alpha=0.3)

# Explosion marker
ax0.axvline(x=EXPL_MET, color='#FF1744', linewidth=2.5, linestyle='-', zorder=10)
ax0.annotate('💥 EXPLOSION\nMET 55:54',
             xy=(EXPL_MET, 20), xytext=(EXPL_MET + 4, 18),
             color='#FF1744', fontsize=8, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#FF1744', lw=1.5))

# Risk zones background
ax0.axhspan(16, 20, alpha=0.08, color='#D50000')
ax0.axhspan(10, 16, alpha=0.08, color='#FF6D00')
ax0.axhspan( 5, 10, alpha=0.08, color='#FFD600')
ax0.axhspan( 0,  5, alpha=0.08, color='#00C853')

# Zone labels
for ypos, lbl, col in [(18, 'RED — CRITICAL', '#FF4444'),
                        (12.5,'ORANGE — HIGH',  '#FF8800'),
                        ( 7,  'YELLOW — MED',   '#FFD600'),
                        ( 2,  'GREEN — LOW',    '#00C853')]:
    ax0.text(142, ypos, lbl, color=col, fontsize=6.5,
             ha='right', va='center', alpha=0.85)

ax0.set_ylim(0, 21)
ax0.set_ylabel('Risk Priority\nNumber (RPN)', color='#AAAACC', fontsize=9)
ax0.set_title('🚀  APOLLO 13 — NASA FIRE RISK MATRIX SIMULATION', color='white',
              fontsize=14, fontweight='bold', pad=12)

# ── ax1: Severity & Likelihood ──
ax1 = axes[1]
ax1.plot(MET, SEV, color='#FF5252', linewidth=1,   label='Severity (1–4)')
ax1.plot(MET, LIK, color='#FFAB40', linewidth=1, linestyle='--', label='Likelihood (1–5)')
ax1.set_ylim(0, 6)
ax1.set_ylabel('S / L', color='#AAAACC', fontsize=9)
ax1.legend(loc='upper right', fontsize=7, facecolor='#0D1B2A',
           labelcolor='white', framealpha=0.6)
ax1.axvline(x=EXPL_MET, color='#FF1744', linewidth=1.5, linestyle='-', alpha=0.7)

# ── ax2: O2 Pressure ──
ax2 = axes[2]
ax2.fill_between(MET, O2_PSI, alpha=0.4, color='#29B6F6')
ax2.plot(MET, O2_PSI, color='#29B6F6', linewidth=1)
ax2.set_ylabel('O₂ Pressure\n(PSI)', color='#AAAACC', fontsize=9)
ax2.axvline(x=EXPL_MET, color='#FF1744', linewidth=1.5, linestyle='-', alpha=0.7)
ax2.annotate('Tank drops\nto 0 PSI',
             xy=(EXPL_MET, 0), xytext=(EXPL_MET + 5, 400),
             color='#29B6F6', fontsize=7,
             arrowprops=dict(arrowstyle='->', color='#29B6F6', lw=1))

# ── ax3: Cabin O2 % ──
ax3 = axes[3]
ax3.fill_between(MET, O2_PCT, 18, alpha=0.4, color='#A5D6A7', where=(O2_PCT >= 18))
ax3.fill_between(MET, O2_PCT, 18, alpha=0.4, color='#EF9A9A', where=(O2_PCT < 18))
ax3.plot(MET, O2_PCT, color='#81C784', linewidth=1)
ax3.axhline(y=19.5, color='#FFEB3B', linewidth=0.8, linestyle='--', alpha=0.7,
            label='Safe min 19.5%')
ax3.set_ylabel('Cabin O₂\n(%)', color='#AAAACC', fontsize=9)
ax3.set_xlabel('Mission Elapsed Time (hours)', color='#AAAACC', fontsize=9)
ax3.set_xlim(MET[0], MET[-1])
ax3.legend(loc='lower right', fontsize=7, facecolor='#0D1B2A',
           labelcolor='white', framealpha=0.6)
ax3.axvline(x=EXPL_MET, color='#FF1744', linewidth=1.5, linestyle='-', alpha=0.7)

# Phase band on ax3
prev_ph = PHASES[0]
start_i = 0
for i in range(1, N):
    if PHASES[i] != prev_ph or i == N - 1:
        pcolor = PHASE_COLORS.get(prev_ph, '#888888')
        ax0.axvspan(MET[start_i], MET[i], ymin=0, ymax=0.03,
                    color=pcolor, alpha=0.9)
        mid = (MET[start_i] + MET[i]) / 2
        label = prev_ph.replace('_', '\n')
        if (MET[i] - MET[start_i]) > 2:
            ax3.text(mid, 18.1, prev_ph.replace('_', ' '),
                     fontsize=5.5, color=pcolor, ha='center', alpha=0.8, rotation=25)
        prev_ph = PHASES[i]
        start_i = i

plt.tight_layout()
fig1.savefig(os.path.join(os.path.dirname(__file__), 'apollo13_timeline.png'),
             dpi=150, bbox_inches='tight', facecolor='#0A0A1A')
print("   ✓ Saved: apollo13_timeline.png")
plt.show(block=False)
plt.pause(1)

# ─────────────────────────────────────────────
#  STEP 2 — NASA Risk Matrix Heatmap + Phase Dots
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 2/3 — NASA Risk Matrix Heatmap + Mission Path")
print("=" * 60)

fig2, (ax_mat, ax_bar) = plt.subplots(1, 2, figsize=(14, 7))
fig2.patch.set_facecolor('#0A0A1A')

# Draw 5×4 matrix grid
matrix_colors = np.array([
    [1, 2, 3, 4],   # Freq=5
    [1, 2, 3, 4],
    [1, 2, 3, 4],
    [1, 2, 2, 3],
    [1, 1, 1, 2],   # Improbable=1
], dtype=float)

# actual RPN values
rpn_grid = np.zeros((5, 4))
for lik_i, lik in enumerate([5, 4, 3, 2, 1]):
    for sev_i, sev in enumerate([1, 2, 3, 4]):
        rpn_grid[lik_i, sev_i] = lik * sev

ax_mat.set_facecolor('#0D1B2A')
cell_color_map = {1: '#00C853', 2: '#FFD600', 3: '#FF6D00', 4: '#D50000'}

for lik_i, lik in enumerate([5, 4, 3, 2, 1]):
    for sev_i, sev in enumerate([1, 2, 3, 4]):
        rpn = lik * sev
        zone = 1 if rpn <= 4 else (2 if rpn <= 9 else (3 if rpn <= 15 else 4))
        col  = cell_color_map[zone]
        rect = mpatches.FancyBboxPatch(
            (sev_i + 0.05, lik_i + 0.05), 0.9, 0.9,
            boxstyle='round,pad=0.05',
            facecolor=col, edgecolor='#0A0A1A', linewidth=2, alpha=0.85
        )
        ax_mat.add_patch(rect)
        ax_mat.text(sev_i + 0.5, lik_i + 0.5, str(int(rpn)),
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color='white',
                    path_effects=[pe.withStroke(linewidth=2, foreground='black')])

# Phase dots on matrix
phase_summary_map = {ps['phase']: ps for ps in phase_stats}
dot_positions = {}
dot_met_map   = {}

for i, p in enumerate(points):
    ph  = p['mission_phase']
    sev = p['fire_risk']['severity']
    lik = p['fire_risk']['likelihood']
    if ph not in dot_positions:
        dot_positions[ph] = (sev, lik)

for ph, (sev, lik) in dot_positions.items():
    lik_i = [5, 4, 3, 2, 1].index(lik)
    sev_i = [1, 2, 3, 4].index(sev)
    xcell = sev_i + 0.5
    ycell = lik_i + 0.5
    ax_mat.scatter(xcell, ycell, s=350, zorder=10,
                   color=PHASE_COLORS.get(ph, '#FFFFFF'),
                   edgecolors='white', linewidths=1.5, alpha=0.9)
    short = ph.replace('_', '\n')[:12]
    ax_mat.annotate(short, xy=(xcell, ycell),
                    xytext=(xcell + 0.15, ycell + 0.2),
                    fontsize=5.5, color='white', alpha=0.9,
                    path_effects=[pe.withStroke(linewidth=1, foreground='black')])

ax_mat.set_xlim(0, 4); ax_mat.set_ylim(0, 5)
ax_mat.set_xticks([0.5, 1.5, 2.5, 3.5])
ax_mat.set_xticklabels(['Negligible\n(1)', 'Marginal\n(2)', 'Critical\n(3)', 'Catastrophic\n(4)'],
                        color='white', fontsize=9)
ax_mat.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5])
ax_mat.set_yticklabels(['Improbable', 'Remote', 'Occasional', 'Probable', 'Frequent'],
                        color='white', fontsize=9)
ax_mat.set_xlabel('SEVERITY →', color='#AAAACC', fontsize=11, fontweight='bold')
ax_mat.set_ylabel('← LIKELIHOOD', color='#AAAACC', fontsize=11, fontweight='bold')
ax_mat.set_title('NASA 5×4 Fire Risk Matrix\n(dots = Apollo 13 phases)',
                  color='white', fontsize=11, fontweight='bold')
ax_mat.set_facecolor('#0D1B2A')
ax_mat.tick_params(colors='white')
for sp in ax_mat.spines.values():
    sp.set_color('#223366')

legend_patches = [
    mpatches.Patch(color='#00C853', label='GREEN — Low (1-4)'),
    mpatches.Patch(color='#FFD600', label='YELLOW — Medium (5-9)'),
    mpatches.Patch(color='#FF6D00', label='ORANGE — High (10-15)'),
    mpatches.Patch(color='#D50000', label='RED — Critical (16-20)'),
]
ax_mat.legend(handles=legend_patches, loc='lower right', fontsize=7,
              facecolor='#0D1B2A', labelcolor='white', framealpha=0.8)

# ── Bar chart: avg RPN per phase ──
ax_bar.set_facecolor('#0D1B2A')
phases_sorted = sorted(phase_stats, key=lambda x: list(PHASE_COLORS.keys()).index(x['phase'])
                        if x['phase'] in PHASE_COLORS else 99)
ph_names  = [ps['phase'].replace('_', '\n') for ps in phases_sorted]
ph_avgrpn = [ps['avg_rpn'] for ps in phases_sorted]
ph_maxrpn = [ps['max_rpn'] for ps in phases_sorted]
bar_cols   = [COLOR_MAP[('GREEN' if v <= 4 else 'YELLOW' if v <= 9 else 'ORANGE' if v <= 15 else 'RED')]
              for v in ph_avgrpn]

bars = ax_bar.barh(ph_names, ph_avgrpn, color=bar_cols, alpha=0.85, height=0.6)
ax_bar.barh(ph_names, ph_maxrpn, color='white', alpha=0.15, height=0.6, label='Max RPN')
for bar, val in zip(bars, ph_avgrpn):
    ax_bar.text(val + 0.2, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', color='white', fontsize=8)

ax_bar.axvline(x=16, color='#D50000', linewidth=1, linestyle='--', alpha=0.7, label='Critical threshold')
ax_bar.axvline(x=10, color='#FF6D00', linewidth=1, linestyle='--', alpha=0.5)
ax_bar.set_xlabel('Average RPN', color='#AAAACC', fontsize=10)
ax_bar.set_title('Average Fire Risk (RPN)\nper Mission Phase', color='white', fontsize=11, fontweight='bold')
ax_bar.tick_params(colors='white', labelsize=8)
ax_bar.set_xlim(0, 22)
ax_bar.set_facecolor('#0D1B2A')
for sp in ax_bar.spines.values():
    sp.set_color('#223366')
ax_bar.legend(fontsize=7, facecolor='#0D1B2A', labelcolor='white', framealpha=0.6)

plt.tight_layout()
fig2.savefig(os.path.join(os.path.dirname(__file__), 'apollo13_risk_matrix.png'),
             dpi=150, bbox_inches='tight', facecolor='#0A0A1A')
print("   ✓ Saved: apollo13_risk_matrix.png")
plt.show(block=False)
plt.pause(1)

# ─────────────────────────────────────────────
#  STEP 3 — Live Animation: Real-time playback
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 3/3 — LIVE ANIMATION (Apollo 13 real-time replay)")
print("  Press Ctrl+C to stop early")
print("=" * 60)

ANIM_STEP  = 15   # advance N data points per frame
INTERVAL   = 60   # ms between frames

fig3 = plt.figure(figsize=(16, 9), facecolor='#0A0A1A')
gs   = gridspec.GridSpec(3, 3, figure=fig3, hspace=0.4, wspace=0.35,
                          left=0.07, right=0.97, top=0.90, bottom=0.07)

ax_rpn   = fig3.add_subplot(gs[0, :2])   # RPN timeline (top wide)
ax_gauge = fig3.add_subplot(gs[1:, 2])    # risk gauge (right tall)
ax_o2p   = fig3.add_subplot(gs[1, 0])    # O2 pressure
ax_o2c   = fig3.add_subplot(gs[1, 1])    # Cabin O2%
ax_temp  = fig3.add_subplot(gs[2, 0])    # Temperature
ax_info  = fig3.add_subplot(gs[2, 1])    # Info panel

for ax in [ax_rpn, ax_o2p, ax_o2c, ax_temp, ax_info, ax_gauge]:
    ax.set_facecolor('#0D1B2A')
    for sp in ax.spines.values():
        sp.set_color('#223366')
    ax.tick_params(colors='#AAAACC', labelsize=7)

fig3.patch.set_facecolor('#0A0A1A')

# Static: draw full RPN in gray
ax_rpn.plot(MET, RPN, color='#333366', linewidth=0.6, alpha=0.6)
ax_rpn.set_xlim(MET[0], MET[-1])
ax_rpn.set_ylim(-0.5, 22)
ax_rpn.set_ylabel('RPN', color='#AAAACC', fontsize=8)
ax_rpn.set_xlabel('MET (hours)', color='#AAAACC', fontsize=8)
ax_rpn.axvline(x=EXPL_MET, color='#FF1744', linewidth=1.5, linestyle='--', alpha=0.5)
ax_rpn.text(EXPL_MET + 0.5, 20.5, '💥', fontsize=10)
for ev in key_events:
    ax_rpn.axvline(x=ev['met_hours'], color='#FFFFFF', linewidth=0.3, alpha=0.2)

# Risk zones
ax_rpn.axhspan(16, 21, alpha=0.06, color='#D50000')
ax_rpn.axhspan(10, 16, alpha=0.06, color='#FF6D00')
ax_rpn.axhspan( 5, 10, alpha=0.06, color='#FFD600')
ax_rpn.axhspan( 0,  5, alpha=0.06, color='#00C853')

title_text = ax_rpn.set_title('🚀 APOLLO 13 — LIVE FIRE RISK SIMULATION  |  MET: 0:00:00',
                                color='white', fontsize=11, fontweight='bold')

# Live elements
live_line,   = ax_rpn.plot([], [], color='#00E5FF', linewidth=1.5, zorder=5)
live_dot,    = ax_rpn.plot([], [], 'o', color='white', markersize=7, zorder=10)

# O2 Pressure plot
ax_o2p.set_xlim(MET[0], MET[-1]); ax_o2p.set_ylim(-50, 1000)
ax_o2p.set_title('O₂ Tank Pressure (PSI)', color='#29B6F6', fontsize=8)
o2p_line,   = ax_o2p.plot([], [], color='#29B6F6', linewidth=1)
o2p_fill    = ax_o2p.fill_between([], [], alpha=0.3, color='#29B6F6')

# Cabin O2%
ax_o2c.set_xlim(MET[0], MET[-1]); ax_o2c.set_ylim(17.5, 21.5)
ax_o2c.set_title('Cabin O₂ (%)', color='#A5D6A7', fontsize=8)
ax_o2c.axhline(y=19.5, color='#FFEB3B', linewidth=0.8, linestyle='--', alpha=0.7)
o2c_line,   = ax_o2c.plot([], [], color='#A5D6A7', linewidth=1)

# Temperature
ax_temp.set_xlim(MET[0], MET[-1]); ax_temp.set_ylim(0, 5500)
ax_temp.set_title('SM Bay4 Temp (°F)', color='#FF7043', fontsize=8)
temp_line,  = ax_temp.plot([], [], color='#FF7043', linewidth=1)

# Info panel (text)
ax_info.axis('off')
info_text   = ax_info.text(0.05, 0.95, '', transform=ax_info.transAxes,
                            color='white', fontsize=8, va='top', fontfamily='monospace',
                            bbox=dict(boxstyle='round', facecolor='#0D1B2A', alpha=0.8))

# Gauge (vertical bar)
ax_gauge.set_xlim(0, 1); ax_gauge.set_ylim(0, 20)
ax_gauge.set_title('RISK GAUGE', color='white', fontsize=9, fontweight='bold')
ax_gauge.set_xticks([]); ax_gauge.set_yticks([4, 9, 15, 20])
ax_gauge.set_yticklabels(['LOW', 'MED', 'HIGH', 'CRIT'], color='white', fontsize=7)

# Gauge background zones
for ylo, yhi, col in [(0, 4, '#00C853'), (4, 9, '#FFD600'), (9, 15, '#FF6D00'), (15, 20, '#D50000')]:
    ax_gauge.barh([ylo + (yhi-ylo)/2], [1], height=yhi-ylo, left=0,
                  color=col, alpha=0.25, align='center')
gauge_bar    = ax_gauge.barh([0], [0.8], height=0, left=0.1,
                              color='#00C853', alpha=0.95, align='center')[0]
gauge_label  = ax_gauge.text(0.5, 1, 'RPN\n--', ha='center', va='center',
                              color='white', fontsize=16, fontweight='bold',
                              transform=ax_gauge.transAxes)

frame_idx = [0]  # mutable for closure

def animate(frame):
    idx = min(frame_idx[0], N - 1)
    frame_idx[0] = min(frame_idx[0] + ANIM_STEP, N - 1)

    p     = points[idx]
    met   = MET[idx]
    rpn   = RPN[idx]
    sev   = SEV[idx]
    lik   = LIK[idx]
    o2p   = O2_PSI[idx]
    o2c   = O2_PCT[idx]
    tmp   = TEMP_F[idx]
    phase = PHASES[idx]
    ft    = FT[idx]
    col   = COLORS[idx]
    rgba  = COLOR_MAP[col]

    # MET → HH:MM
    h = int(met); m = int((met - h) * 60)
    met_str = f'{h:03d}:{m:02d}'

    # Title
    title_text.set_text(f'🚀 APOLLO 13 — FIRE RISK SIMULATION  |  MET: {met_str}  |  Phase: {phase}')

    # Live RPN line
    live_line.set_data(MET[:idx+1], RPN[:idx+1])
    live_line.set_color(rgba)
    live_dot.set_data([met], [rpn])
    live_dot.set_color(rgba)

    # O2 pressure
    o2p_line.set_data(MET[:idx+1], O2_PSI[:idx+1])

    # O2 cabin
    o2c_line.set_data(MET[:idx+1], O2_PCT[:idx+1])

    # Temperature
    temp_line.set_data(MET[:idx+1], TEMP_F[:idx+1])

    # Gauge
    gauge_bar.set_height(rpn)
    gauge_bar.set_y(0)
    gauge_bar.set_color(rgba)
    gauge_label.set_text(f'RPN\n{rpn}')
    gauge_label.set_color(rgba)

    # Info text
    risk_sym = {'GREEN': '🟢', 'YELLOW': '🟡', 'ORANGE': '🟠', 'RED': '🔴'}
    sev_lbl  = p['fire_risk']['severity_label']
    lik_lbl  = p['fire_risk']['likelihood_label']
    rlvl     = p['fire_risk']['risk_level']
    notes_sh = p['fire_risk']['notes'][:60] + '...' if len(p['fire_risk']['notes']) > 60 else p['fire_risk']['notes']

    info = (
        f"{risk_sym.get(col,'?')} {col} — {rlvl}\n"
        f"{'─'*30}\n"
        f"MET        : {met_str}\n"
        f"Phase      : {phase}\n"
        f"Hazard     : {ft}\n"
        f"RPN        : {rpn}/20\n"
        f"Severity   : {sev} ({sev_lbl})\n"
        f"Likelihood : {lik} ({lik_lbl})\n"
        f"O₂ Tank    : {o2p:.0f} PSI\n"
        f"Cabin O₂   : {o2c:.2f}%\n"
        f"Temp       : {tmp:.0f} °F\n"
        f"{'─'*30}\n"
        f"{notes_sh}"
    )
    info_text.set_text(info)

    if idx >= N - 1:
        ani.event_source.stop()
        ax_rpn.set_title('✅ SIMULATION COMPLETE — Apollo 13 Returned Safely',
                          color='#00C853', fontsize=12, fontweight='bold')

    return live_line, live_dot, o2p_line, o2c_line, temp_line, gauge_bar, gauge_label, info_text, title_text

ani = FuncAnimation(fig3, animate, frames=N // ANIM_STEP + 1,
                    interval=INTERVAL, blit=False, repeat=False)

fig3.savefig(os.path.join(os.path.dirname(__file__), 'apollo13_animation_frame.png'),
             dpi=120, bbox_inches='tight', facecolor='#0A0A1A')
print("   ✓ Starting live animation window...")
print("   ✓ Close window to exit\n")

plt.show()
print("\n✅ Simulation finished. Output files:")
print("   - apollo13_timeline.png")
print("   - apollo13_risk_matrix.png")
print("   - apollo13_animation_frame.png")
