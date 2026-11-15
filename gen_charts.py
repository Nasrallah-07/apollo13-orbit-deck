"""Generate static chart exports for Apollo 13 Fire Risk Simulation"""
import json, numpy as np, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib import gridspec

BASE = r'c:\Users\Nasrallah\Downloads\chat-812c8388-89f0-4c7c-88f6-7e872379485d'
JSON_PATH = os.path.join(BASE, 'apollo13_fire_risk_simulation.json')

print("Loading data...")
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    sim_data = json.load(f)

points      = sim_data['simulation_data']
key_events  = sim_data['key_events']
phase_stats = sim_data['phase_statistics']
N = len(points)

MET    = np.array([p['met_hours']                         for p in points])
RPN    = np.array([p['fire_risk']['risk_priority_number'] for p in points])
SEV    = np.array([p['fire_risk']['severity']             for p in points])
LIK    = np.array([p['fire_risk']['likelihood']           for p in points])
O2_PSI = np.array([p['sensor_readings']['o2_tank2_pressure_psi'] for p in points])
O2_PCT = np.array([p['sensor_readings']['cabin_o2_percentage']   for p in points])
TEMP_F = np.array([p['sensor_readings']['sm_bay4_temperature_F'] for p in points])
PHASES = [p['mission_phase']             for p in points]
COLORS = [p['fire_risk']['risk_color']   for p in points]

COLOR_MAP = {'GREEN':'#00C853','YELLOW':'#FFD600','ORANGE':'#FF6D00','RED':'#D50000'}
PHASE_COLORS = {
    'Pre-Launch':'#78909C','Launch':'#FF5722','Earth_Orbit':'#29B6F6',
    'TLI_Burn':'#FFA726','Translunar_Coast':'#42A5F5','O2_Tank_Explosion':'#D50000',
    'Emergency_Response':'#FF1744','Lifeboat_Coast':'#7E57C2','Lunar_Flyby':'#26C6DA',
    'Return_Coast':'#66BB6A','CM_Power_Up':'#FFA726','Reentry':'#FF7043','Splashdown':'#26A69A',
}
EXPL_MET = MET[int(np.argmax(RPN))]

# ═══════════════════════════════════════════
#  CHART 1: Mission Timeline (4 subplots)
# ═══════════════════════════════════════════
print("Generating Chart 1: Mission Timeline...")
fig1, axes = plt.subplots(4,1,figsize=(16,11),sharex=True,
                          gridspec_kw={'hspace':0.08,'height_ratios':[3,2,2,2]})
fig1.patch.set_facecolor('#0A0A1A')
for ax in axes:
    ax.set_facecolor('#0D1B2A')
    ax.tick_params(colors='#AAAACC',labelsize=8)
    for sp in ax.spines.values(): sp.set_color('#223366')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

ax0 = axes[0]
for i in range(N-1):
    ax0.fill_between([MET[i],MET[i+1]],[RPN[i],RPN[i+1]],[0,0],
                     color=COLOR_MAP[COLORS[i]],alpha=0.35)
ax0.plot(MET,RPN,color='white',linewidth=0.8,alpha=0.9)
for ev in key_events:
    ax0.axvline(x=ev['met_hours'],color='#FFFFFF',linewidth=0.4,linestyle='--',alpha=0.3)
ax0.axvline(x=EXPL_MET,color='#FF1744',linewidth=2.5,zorder=10)
ax0.annotate('💥 O2 TANK\nEXPLOSION\nMET 55:54',
             xy=(EXPL_MET,20),xytext=(EXPL_MET+5,17.5),
             color='#FF1744',fontsize=8,fontweight='bold',
             arrowprops=dict(arrowstyle='->',color='#FF1744',lw=1.5))
ax0.axhspan(16,20,alpha=0.08,color='#D50000')
ax0.axhspan(10,16,alpha=0.08,color='#FF6D00')
ax0.axhspan(5,10,alpha=0.08,color='#FFD600')
ax0.axhspan(0,5,alpha=0.08,color='#00C853')
for ypos,lbl,col in [(18,'🔴 RED — CRITICAL','#FF4444'),(12.5,'🟠 ORANGE — HIGH','#FF8800'),
                      (7,'🟡 YELLOW — MED','#FFD600'),(2,'🟢 GREEN — LOW','#00C853')]:
    ax0.text(142,ypos,lbl,color=col,fontsize=6.5,ha='right',va='center',alpha=0.85)
ax0.set_ylim(0,22)
ax0.set_ylabel('Risk Priority\nNumber (RPN)',color='#AAAACC',fontsize=9)
ax0.set_title('🚀  APOLLO 13 — NASA FIRE RISK MATRIX SIMULATION  |  2000 Data Points  |  MET: 0–142.9h',
              color='white',fontsize=13,fontweight='bold',pad=10)

ax1 = axes[1]
ax1.plot(MET,SEV,color='#FF5252',linewidth=1,label='Severity (1–4)')
ax1.plot(MET,LIK,color='#FFAB40',linewidth=1,linestyle='--',label='Likelihood (1–5)')
ax1.set_ylim(0,6)
ax1.set_ylabel('Sev / Lik',color='#AAAACC',fontsize=9)
ax1.legend(loc='upper right',fontsize=7,facecolor='#0D1B2A',labelcolor='white',framealpha=0.6)
ax1.axvline(x=EXPL_MET,color='#FF1744',linewidth=1.5,alpha=0.7)

ax2 = axes[2]
ax2.fill_between(MET,O2_PSI,alpha=0.35,color='#29B6F6')
ax2.plot(MET,O2_PSI,color='#29B6F6',linewidth=1)
ax2.set_ylabel('O₂ Tank Pressure\n(PSI)',color='#AAAACC',fontsize=9)
ax2.axvline(x=EXPL_MET,color='#FF1744',linewidth=1.5,alpha=0.7)
ax2.annotate('Tank drops\nto 0 PSI',xy=(EXPL_MET+0.5,0),xytext=(EXPL_MET+6,400),
             color='#29B6F6',fontsize=7,arrowprops=dict(arrowstyle='->',color='#29B6F6',lw=1))

ax3 = axes[3]
ax3.fill_between(MET,O2_PCT,18,alpha=0.4,color='#A5D6A7',where=(O2_PCT>=18))
ax3.fill_between(MET,O2_PCT,18,alpha=0.4,color='#EF9A9A',where=(O2_PCT<18))
ax3.plot(MET,O2_PCT,color='#81C784',linewidth=1)
ax3.axhline(y=19.5,color='#FFEB3B',linewidth=0.8,linestyle='--',alpha=0.7,label='Safe min 19.5%')
ax3.set_ylabel('Cabin O₂ (%)',color='#AAAACC',fontsize=9)
ax3.set_xlabel('Mission Elapsed Time (hours)',color='#AAAACC',fontsize=9)
ax3.set_xlim(MET[0],MET[-1])
ax3.legend(loc='lower right',fontsize=7,facecolor='#0D1B2A',labelcolor='white',framealpha=0.6)
ax3.axvline(x=EXPL_MET,color='#FF1744',linewidth=1.5,alpha=0.7)

# Phase labels on ax3
prev_ph=PHASES[0]; start_i=0
for i in range(1,N):
    if PHASES[i]!=prev_ph or i==N-1:
        pcolor=PHASE_COLORS.get(prev_ph,'#888888')
        mid=(MET[start_i]+MET[i])/2
        if (MET[i]-MET[start_i])>2.5:
            ax3.text(mid,18.08,prev_ph.replace('_',' '),fontsize=5,color=pcolor,
                     ha='center',alpha=0.8,rotation=20)
        prev_ph=PHASES[i]; start_i=i

plt.tight_layout()
out1=os.path.join(BASE,'apollo13_timeline.png')
fig1.savefig(out1,dpi=150,bbox_inches='tight',facecolor='#0A0A1A')
print(f"   Saved: {out1}")
plt.close(fig1)

# ═══════════════════════════════════════════
#  CHART 2: Risk Matrix + Bar Chart
# ═══════════════════════════════════════════
print("Generating Chart 2: Risk Matrix...")
fig2,(ax_mat,ax_bar)=plt.subplots(1,2,figsize=(14,7))
fig2.patch.set_facecolor('#0A0A1A')
for ax in [ax_mat,ax_bar]:
    ax.set_facecolor('#0D1B2A')
    for sp in ax.spines.values(): sp.set_color('#223366')
    ax.tick_params(colors='white',labelsize=8)

cell_cmap={1:'#00C853',2:'#FFD600',3:'#FF6D00',4:'#D50000'}
for lik_i,lik in enumerate([5,4,3,2,1]):
    for sev_i,sev in enumerate([1,2,3,4]):
        rpn=lik*sev
        zone=1 if rpn<=4 else(2 if rpn<=9 else(3 if rpn<=15 else 4))
        col=cell_cmap[zone]
        rect=mpatches.FancyBboxPatch((sev_i+0.05,lik_i+0.05),0.9,0.9,
             boxstyle='round,pad=0.05',facecolor=col,edgecolor='#0A0A1A',linewidth=2,alpha=0.85)
        ax_mat.add_patch(rect)
        ax_mat.text(sev_i+0.5,lik_i+0.5,str(int(rpn)),ha='center',va='center',
                    fontsize=14,fontweight='bold',color='white',
                    path_effects=[pe.withStroke(linewidth=2,foreground='black')])

dot_positions={}
for p in points:
    ph=p['mission_phase']; sev=p['fire_risk']['severity']; lik=p['fire_risk']['likelihood']
    if ph not in dot_positions: dot_positions[ph]=(sev,lik)

for ph,(sev,lik) in dot_positions.items():
    lik_i=[5,4,3,2,1].index(lik); sev_i=[1,2,3,4].index(sev)
    xcell=sev_i+0.5; ycell=lik_i+0.5
    ax_mat.scatter(xcell,ycell,s=300,zorder=10,color=PHASE_COLORS.get(ph,'#FFFFFF'),
                   edgecolors='white',linewidths=1.5,alpha=0.9)
    ax_mat.annotate(ph.replace('_','\n')[:12],xy=(xcell,ycell),
                    xytext=(xcell+0.1,ycell+0.18),fontsize=5,color='white',
                    path_effects=[pe.withStroke(linewidth=1,foreground='black')])

ax_mat.set_xlim(0,4); ax_mat.set_ylim(0,5)
ax_mat.set_xticks([0.5,1.5,2.5,3.5])
ax_mat.set_xticklabels(['Negligible\n(1)','Marginal\n(2)','Critical\n(3)','Catastrophic\n(4)'],color='white',fontsize=9)
ax_mat.set_yticks([0.5,1.5,2.5,3.5,4.5])
ax_mat.set_yticklabels(['Improbable','Remote','Occasional','Probable','Frequent'],color='white',fontsize=9)
ax_mat.set_xlabel('SEVERITY →',color='#AAAACC',fontsize=11,fontweight='bold')
ax_mat.set_ylabel('← LIKELIHOOD',color='#AAAACC',fontsize=11,fontweight='bold')
ax_mat.set_title('NASA 5×4 Fire Risk Matrix\n(colored dots = Apollo 13 mission phases)',color='white',fontsize=11,fontweight='bold')
legend_patches=[mpatches.Patch(color='#00C853',label='GREEN — Low (1-4)'),
                mpatches.Patch(color='#FFD600',label='YELLOW — Medium (5-9)'),
                mpatches.Patch(color='#FF6D00',label='ORANGE — High (10-15)'),
                mpatches.Patch(color='#D50000',label='RED — Critical (16-20)')]
ax_mat.legend(handles=legend_patches,loc='lower right',fontsize=7,facecolor='#0D1B2A',
              labelcolor='white',framealpha=0.8)

phases_ordered=['Pre-Launch','Launch','Earth_Orbit','TLI_Burn','Translunar_Coast',
                'O2_Tank_Explosion','Emergency_Response','Lifeboat_Coast',
                'Lunar_Flyby','Return_Coast','CM_Power_Up','Reentry','Splashdown']
ps_map={ps['phase']:ps for ps in phase_stats}
ph_names=[ph.replace('_','\n') for ph in phases_ordered if ph in ps_map]
ph_avg  =[ps_map[ph]['avg_rpn'] for ph in phases_ordered if ph in ps_map]
ph_max  =[ps_map[ph]['max_rpn'] for ph in phases_ordered if ph in ps_map]
bar_cols=[COLOR_MAP['GREEN' if v<=4 else 'YELLOW' if v<=9 else 'ORANGE' if v<=15 else 'RED'] for v in ph_avg]

bars=ax_bar.barh(ph_names,ph_avg,color=bar_cols,alpha=0.85,height=0.6)
ax_bar.barh(ph_names,ph_max,color='white',alpha=0.1,height=0.6,label='Max RPN (ghost)')
for bar,val in zip(bars,ph_avg):
    ax_bar.text(val+0.2,bar.get_y()+bar.get_height()/2,f'{val:.1f}',va='center',color='white',fontsize=8)
ax_bar.axvline(x=16,color='#D50000',linewidth=1.2,linestyle='--',alpha=0.8,label='Critical (16)')
ax_bar.axvline(x=10,color='#FF6D00',linewidth=1,linestyle='--',alpha=0.5,label='High (10)')
ax_bar.set_xlabel('Average RPN',color='#AAAACC',fontsize=10)
ax_bar.set_title('Avg Fire Risk (RPN) per Mission Phase\n(Apollo 13)',color='white',fontsize=11,fontweight='bold')
ax_bar.set_xlim(0,22)
ax_bar.legend(fontsize=7,facecolor='#0D1B2A',labelcolor='white',framealpha=0.6)

plt.tight_layout()
out2=os.path.join(BASE,'apollo13_risk_matrix.png')
fig2.savefig(out2,dpi=150,bbox_inches='tight',facecolor='#0A0A1A')
print(f"   Saved: {out2}")
plt.close(fig2)

# ═══════════════════════════════════════════
#  CHART 3: Fire Type Distribution (Pie + Stacked)
# ═══════════════════════════════════════════
print("Generating Chart 3: Fire Type Distribution...")
fig3,axes3=plt.subplots(1,2,figsize=(14,7))
fig3.patch.set_facecolor('#0A0A1A')

ft_counts={}
for p in points:
    ft=p['fire_risk']['fire_hazard_type']
    ft_counts[ft]=ft_counts.get(ft,0)+1

ft_short={'ELECTRICAL_ARC':'Electrical Arc',
           'OXYGEN_ENRICHED_COMBUSTION':'O2 Combustion',
           'CRYOGENIC_FUEL_LEAK':'Cryo Fuel Leak',
           'THERMAL_RUNAWAY':'Thermal Runaway',
           'PYROTECHNIC_IGNITION':'Pyrotechnic',
           'HYPERGOLIC_PROPELLANT_REACTION':'Hypergolic',
           'WIRING_INSULATION_BURN':'Wiring Burn',
           'PRESSURE_VESSEL_RUPTURE_FIRE':'Pressure Rupture'}

ft_colors=['#29B6F6','#D50000','#00BFA5','#FF6D00','#FF5722','#AB47BC','#FFD600','#EC407A']
labels=[ft_short.get(k,k) for k in ft_counts.keys()]
sizes=list(ft_counts.values())

ax_pie=axes3[0]
ax_pie.set_facecolor('#0D1B2A')
wedges,texts,autotexts=ax_pie.pie(sizes,labels=labels,colors=ft_colors[:len(sizes)],
    autopct='%1.1f%%',pctdistance=0.75,
    textprops={'color':'white','fontsize':8},
    wedgeprops={'edgecolor':'#0A0A1A','linewidth':1.5})
for at in autotexts: at.set_fontsize(7)
ax_pie.set_title('Fire Hazard Type Distribution\n(all 2000 data points)',
                  color='white',fontsize=11,fontweight='bold')

# Stacked bar per phase
ax_stk=axes3[1]
ax_stk.set_facecolor('#0D1B2A')
all_ft=list(ft_short.keys())
phase_ft_counts={ph:{ft:0 for ft in all_ft} for ph in phases_ordered}
for p in points:
    ph=p['mission_phase']; ft=p['fire_risk']['fire_hazard_type']
    if ph in phase_ft_counts: phase_ft_counts[ph][ft]+=1

ph_labels_short=[ph.replace('_','\n') for ph in phases_ordered if ph in phase_ft_counts]
x=np.arange(len(ph_labels_short))
bottom=np.zeros(len(ph_labels_short))
for fi,ft in enumerate(all_ft):
    vals=np.array([phase_ft_counts[ph][ft] for ph in phases_ordered if ph in phase_ft_counts],dtype=float)
    ax_stk.bar(x,vals,bottom=bottom,color=ft_colors[fi],label=ft_short[ft],alpha=0.9,width=0.7)
    bottom+=vals

ax_stk.set_xticks(x)
ax_stk.set_xticklabels(ph_labels_short,color='white',fontsize=6,rotation=0)
ax_stk.set_ylabel('Data Points',color='#AAAACC',fontsize=9)
ax_stk.set_title('Fire Type Count per Mission Phase',color='white',fontsize=11,fontweight='bold')
ax_stk.legend(loc='upper right',fontsize=5.5,facecolor='#0D1B2A',
               labelcolor='white',framealpha=0.6,ncol=2)
for sp in ax_stk.spines.values(): sp.set_color('#223366')
ax_stk.tick_params(colors='white')

plt.tight_layout()
out3=os.path.join(BASE,'apollo13_fire_types.png')
fig3.savefig(out3,dpi=150,bbox_inches='tight',facecolor='#0A0A1A')
print(f"   Saved: {out3}")
plt.close(fig3)

print("\n✅ ALL 3 CHARTS GENERATED:")
print(f"   1. {out1}")
print(f"   2. {out2}")
print(f"   3. {out3}")
print("\nTo run the LIVE ANIMATION, open: apollo13_simulation.py")
