"""
Apollo 13 Fire Risk Prediction API
FastAPI backend that serves the trained XGBoost model
Powered by NASA MSC-02680 Telemetry Dataset: apollo13_numeric_telemetry-1.json
Runs locally: uvicorn api_server:app --reload --port 8787
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
import xgboost as xgb
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "apollo13_fire_risk_xgb.json")
DATA_PATH = os.path.join(BASE, "apollo13_numeric_telemetry-1.json")
if not os.path.exists(DATA_PATH):
    # fallback if -1 not present
    DATA_PATH = os.path.join(BASE, "apollo13_numeric_telemetry.json")

app = FastAPI(
    title="Apollo 13 Fire Risk Prediction API",
    description="NASA-based XGBoost fire risk classifier trained on Apollo 13 telemetry data (apollo13_numeric_telemetry-1.json)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset metadata and categories
PHASES_CAT = list(range(1, 14))
HAZARDS_CAT = list(range(1, 9))
DATA_POINTS_COUNT = 6000

if os.path.exists(DATA_PATH):
    try:
        with open(DATA_PATH, "r") as f:
            raw_meta = json.load(f)
        if isinstance(raw_meta, dict) and "data" in raw_meta:
            df_init = pd.DataFrame(raw_meta["data"])
            PHASES_CAT = sorted(df_init["phase"].unique().tolist())
            HAZARDS_CAT = sorted(df_init["hazard_type"].unique().tolist())
            DATA_POINTS_COUNT = len(df_init)
    except Exception as e:
        print(f"Warning loading metadata from {DATA_PATH}: {e}")

# Load model at startup with categorical support
model = xgb.XGBClassifier(enable_categorical=True)
model.load_model(MODEL_PATH)

LEVEL_NAMES = {0: "GREEN", 1: "YELLOW", 2: "ORANGE", 3: "RED"}
RISK_COLORS = {
    "GREEN":  {"hex": "#00C853", "rpn_range": "1-4",  "action": "Monitor — Low Risk"},
    "YELLOW": {"hex": "#FFD600", "rpn_range": "5-9",  "action": "Review Required"},
    "ORANGE": {"hex": "#FF6D00", "rpn_range": "10-15","action": "Mitigation Required"},
    "RED":    {"hex": "#D50000", "rpn_range": "16-20","action": "CRITICAL — Mission Hold"},
}
PHASE_NAMES = {
    1: "Pre-Launch", 2: "Launch", 3: "Earth Orbit", 4: "TLI Burn",
    5: "Translunar Coast", 6: "O2 Tank Explosion", 7: "Emergency Response",
    8: "Lifeboat Coast", 9: "Lunar Flyby", 10: "Return Coast",
    11: "CM Power Up", 12: "Reentry", 13: "Splashdown"
}
HAZARD_NAMES = {
    1: "Electrical Arc", 2: "O2 Enriched Combustion", 3: "Cryogenic Fuel Leak",
    4: "Thermal Runaway", 5: "Pyrotechnic Ignition", 6: "Hypergolic Propellant",
    7: "Wiring Insulation Burn", 8: "Pressure Vessel Rupture"
}


def compute_flame_physics(phase: int, o2_pct: float, o2_psi: float, temp_f: float, hazard_type: int, is_alert: int):
    """
    Rigorous Thermodynamics & Fluid Mechanics Combustion Model
    Based on Burke-Schumann diffusion, Roper's buoyancy relations,
    Spalding transfer number, and NASA Microgravity Combustion Research (FLEX/ACME).
    """
    import math

    # 1. Environmental & Acceleration Parameters
    # g_eff (m/s^2) based on flight mechanics:
    gravity_map = {
        1: 9.81, 2: 34.3, 3: 0.0, 4: 14.7, 5: 0.0, 6: 0.0,
        7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 49.0, 13: 9.81
    }
    g_acc = gravity_map.get(phase, 0.0)
    g_level = g_acc / 9.81
    is_zero_g = (g_acc == 0.0)

    # Ambient thermodynamics
    p_bar = (o2_psi * 0.0689476) + 1.013 # gauge psi to absolute bar
    t_inf_k = (temp_f - 32.0) * (5.0 / 9.0) + 273.15
    y_o2 = max(0.05, min(1.0, o2_pct / 100.0))

    # 2. First Law Enthalpy Balance: Adiabatic & Effective Flame Temperature
    # NASA SP-8067 wire insulation (PTFE/Teflon / Polyimide) standard values:
    delta_hc = 42.0e6  # J/kg net heat of combustion
    cp_gas = 1150.0    # J/kg.K mean specific heat
    s_stoich = 3.6     # stoichiometric oxygen-fuel mass ratio

    # Adiabatic Flame Temperature (T_ad)
    t_ad_k = t_inf_k + (y_o2 * delta_hc) / (cp_gas * s_stoich * 2.6)
    if is_alert == 1 and o2_psi >= 900:
        t_ad_k *= 1.25  # High pressure O2 jet boost

    # Radiative Heat Loss (0G vs 1G):
    # In 0G, absence of buoyant convection traps radiative emission around the core:
    rad_loss_factor = 0.82 if is_zero_g else 0.91
    t_flame_k = max(650.0, min(3300.0, t_ad_k * rad_loss_factor))
    t_flame_f = (t_flame_k - 273.15) * 1.8 + 32.0

    # 3. Fluid Mechanics: Grashof Number (Gr)
    # Gr = (g * beta * delta_T * L^3) / nu^2
    beta = 1.0 / t_inf_k
    nu = 1.5e-5 * (1.0 / max(0.5, p_bar)) # kinematic viscosity
    l_char = 0.02 # 2 cm characteristic dimension
    delta_t = max(5.0, t_flame_k - t_inf_k)
    gr = (g_acc * beta * delta_t * (l_char ** 3)) / (nu ** 2) if not is_zero_g else 0.0

    # 4. Flame Morphology: Aspect Ratio (AR = Height / Width)
    # Burke-Schumann: at Gr = 0, spherically symmetric (AR = 1.00)
    # Roper's buoyant relation: AR scales with Gr^0.25
    if is_zero_g:
        aspect_ratio = 1.00
    else:
        aspect_ratio = round(max(1.15, min(4.5, 1.0 + 0.38 * (gr ** 0.25) / 10.0)), 2)

    # 5. Diffusion Flame Radius / Standoff Distance (mm)
    # Spalding d^2-law: r_f scales with sqrt(D * tau_res)
    # In 0G, absence of buoyant draft expands the reaction boundary outward by ~2x
    base_r = 18.5 if is_zero_g else 8.5
    r_flame_mm = round(base_r * math.sqrt(y_o2 / 0.21) * math.pow(max(0.5, p_bar), -0.15), 1)

    # 6. Radiative Spectral Physics (Wien's Law & Chemiluminescence)
    lambda_peak_nm = round(2.898e6 / t_flame_k, 0)

    # Classify Shape
    if is_alert == 1 and o2_psi >= 950:
        shape_type = "jet"
        shape_ar = "Explosive Radial Jet (High-Pressure O2)"
        shape_en = "Radial Pressure Jet / Blast"
        shape_desc = f"High oxygen pressure ({o2_psi:.0f} psi) generates a turbulent jet exceeding diffusion speed, with wide radial radiative dispersion."
    elif is_zero_g:
        shape_type = "spherical"
        shape_ar = "Spherical Flame Ball (0G Microgravity - Fickian Diffusion)"
        shape_en = f"Spherical Diffusion Ball (AR = {aspect_ratio:.2f}, Gr = 0.0)"
        shape_desc = "Microgravity (G=0): Complete absence of Archimedes buoyancy (Grashof Number = 0). O2 transport is governed strictly by Fick's Law of molecular diffusion isotropically across 360°, producing a symmetric spherical flame ball with Aspect Ratio AR=1.00."
    elif g_level >= 2.0:
        shape_type = "torch"
        shape_ar = f"Hyper-Buoyant Elongated Torch ({g_level:.1f}G)"
        shape_en = f"Hyper-Buoyant Torch (AR = {aspect_ratio:.2f}, Gr = {gr:.1e})"
        shape_desc = f"High rocket acceleration ({g_level:.1f}G) raises Grashof number (Gr = {gr:.1e}), vigorously pulling hot gases upward into a slender hyper-buoyant torch."
    else:
        shape_type = "teardrop"
        shape_ar = f"Standard 1G Teardrop Flame (Natural Convection)"
        shape_en = f"Buoyant Teardrop (AR = {aspect_ratio:.2f}, Gr = {gr:.1e})"
        shape_desc = f"Standard gravity (1G): Natural Archimedean buoyancy (Gr = {gr:.1e}) lifts hot combustion gases vertically, forming the classic teardrop geometry (AR={aspect_ratio:.2f})."

    # Classify Color & Radiation
    if o2_pct >= 21.5 or (o2_psi >= 900 and hazard_type in [2, 6, 8]):
        color_name_ar = "Electric Blue-White Incandescent"
        color_name_en = f"Incandescent White / Cyan (T={t_flame_k:.0f}K)"
        outer_color = "#00F0FF"
        core_color = "#FFFFFF"
        glow_color = "rgba(0, 240, 255, 0.85)"
        soot_desc = f"Planck continuum at {t_flame_k:.0f}K ({t_flame_f:.0f}°F). Complete stoichiometric oxidation with zero soot generation."
        regime = "Hyper-Oxidized Incandescent Continuum"
    elif o2_pct < 18.0 or temp_f < 200:
        color_name_ar = "Smoldering Red / Cool Flame"
        color_name_en = f"Dim Crimson / Cool Flame (T={t_flame_k:.0f}K)"
        outer_color = "#FF1744"
        core_color = "#B71C1C"
        glow_color = "rgba(255, 23, 68, 0.5)"
        soot_desc = f"Cool flame regime at {t_flame_k:.0f}K. Severe oxygen starvation limits complete combustion, generating heavy soot."
        regime = "Low-O2 Quenched Smolder"
    elif is_zero_g:
        color_name_ar = "Pale Blue / Cyan Chemiluminescence"
        color_name_en = f"Pale Blue Chemiluminescence (λ = 431.4nm CH*)"
        outer_color = "#00D4FF"
        core_color = "#0091EA"
        glow_color = "rgba(0, 212, 255, 0.75)"
        soot_desc = "Chemiluminescent emission: Zero soot formation, clean radiative emission from excited CH* (431.4 nm) and C2* (516.5 nm) free radicals."
        regime = "Radical Diffusion Chemiluminescence"
    else:
        color_name_ar = "Golden Yellow-Orange (Soot Incandescence)"
        color_name_en = f"Luminous Yellow-Orange (T={t_flame_k:.0f}K)"
        outer_color = "#FF9100"
        core_color = "#FFD600"
        glow_color = "rgba(255, 145, 0, 0.75)"
        soot_desc = f"Carbonaceous soot incandescence (blackbody radiation) peaking at wavelength {lambda_peak_nm:.0f}nm."
        regime = "Buoyant Soot Incandescence"

    return {
        "gravity_g": round(g_level, 2),
        "gravity_mps2": round(g_acc, 2),
        "is_microgravity": is_zero_g,
        "grashof_number": f"{gr:.2e}",
        "aspect_ratio": aspect_ratio,
        "flame_temp_k": round(t_flame_k, 0),
        "flame_temp_f": round(t_flame_f, 0),
        "flame_radius_mm": r_flame_mm,
        "peak_wavelength_nm": lambda_peak_nm,
        "shape_type": shape_type,
        "shape_title": shape_ar,
        "shape_title_en": shape_en,
        "shape_desc": shape_desc,
        "color_title": color_name_ar,
        "color_title_en": color_name_en,
        "outer_color": outer_color,
        "core_color": core_color,
        "glow_color": glow_color,
        "soot_desc": soot_desc,
        "regime": regime,
        "transport_mechanism": "Fick's Molecular Diffusion (No Buoyancy)" if is_zero_g else "Navier-Stokes Buoyant Convection"
    }


class TelemetryInput(BaseModel):
    met_h:        float = Field(..., ge=0,   le=200,  description="Mission Elapsed Time (hours)")
    phase:        int   = Field(..., ge=1,   le=13,   description="Mission phase code (1=Pre-Launch ... 13=Splashdown)")
    hazard_type:  int   = Field(..., ge=1,   le=8,    description="Fire hazard type code (1-8)")
    o2_psi:       float = Field(..., ge=0,   le=1200, description="O2 Tank 2 pressure (psi)")
    o2_pct:       float = Field(..., ge=0,   le=25,   description="Cabin O2 percentage")
    temp_f:       float = Field(..., ge=-50, le=6000, description="SM Bay 4 temperature (°F)")
    is_alert:     int   = Field(0,   ge=0,   le=1,    description="Alert flag (0=normal, 1=event)")
    # Optional engineered features (auto-computed if not provided)
    met_frac:        float | None = None
    o2_psi_delta:    float | None = None
    o2_pct_delta:    float | None = None
    temp_f_delta:    float | None = None
    o2_psi_roll5:    float | None = None
    temp_f_roll5:    float | None = None
    o2_psi_x_pct:    float | None = None


@app.get("/")
@app.get("/orbit-deck.html")
@app.get("/orbit-deck")
def get_orbit_deck():
    return FileResponse(os.path.join(BASE, "orbit-deck.html"))


@app.get("/status")
@app.get("/api/status")
def status_info():
    return {
        "status": "online",
        "model": "Apollo13-XGBoost-FireRisk",
        "database": os.path.basename(DATA_PATH),
        "total_records": DATA_POINTS_COUNT,
        "accuracy": "~95%"
    }


@app.get("/apollo13_simulation.html")
@app.get("/simulation")
def get_simulation_page():
    return FileResponse(os.path.join(BASE, "apollo13_simulation.html"))


@app.get("/apollo13_ai_predictor.html")
@app.get("/predictor")
def get_predictor_page():
    return FileResponse(os.path.join(BASE, "apollo13_ai_predictor.html"))


@app.get("/database")
def get_database_info():
    """Returns database summary and sample records from apollo13_numeric_telemetry-1.json"""
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=404, detail="Database file not found")
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return {
        "filename": os.path.basename(DATA_PATH),
        "mission_id": data.get("mission_id", 13),
        "total_points": data.get("total_points", DATA_POINTS_COUNT),
        "duration_hours": data.get("duration_hours", 142.9),
        "columns": data.get("columns", []),
        "sample": data.get("data", [])[:5]
    }


@app.post("/predict")
def predict(inp: TelemetryInput):
    # Auto-compute engineered features if not provided
    met_frac      = inp.met_frac      if inp.met_frac      is not None else inp.met_h / 142.9
    o2_psi_delta  = inp.o2_psi_delta  if inp.o2_psi_delta  is not None else 0.0
    o2_pct_delta  = inp.o2_pct_delta  if inp.o2_pct_delta  is not None else 0.0
    temp_f_delta  = inp.temp_f_delta  if inp.temp_f_delta  is not None else 0.0
    o2_psi_roll5  = inp.o2_psi_roll5  if inp.o2_psi_roll5  is not None else inp.o2_psi
    temp_f_roll5  = inp.temp_f_roll5  if inp.temp_f_roll5  is not None else inp.temp_f
    o2_psi_x_pct  = inp.o2_psi_x_pct if inp.o2_psi_x_pct  is not None else inp.o2_psi * inp.o2_pct

    # Create DataFrame with exact column names and categorical types required by XGBoost
    feature_vector = pd.DataFrame({
        "met_h":        [float(inp.met_h)],
        "phase":        pd.Categorical([int(inp.phase)], categories=PHASES_CAT),
        "hazard_type":  pd.Categorical([int(inp.hazard_type)], categories=HAZARDS_CAT),
        "o2_psi":       [float(inp.o2_psi)],
        "o2_pct":       [float(inp.o2_pct)],
        "temp_f":       [float(inp.temp_f)],
        "is_alert":     [int(inp.is_alert)],
        "met_frac":     [float(met_frac)],
        "o2_psi_delta": [float(o2_psi_delta)],
        "o2_pct_delta": [float(o2_pct_delta)],
        "temp_f_delta": [float(temp_f_delta)],
        "o2_psi_roll5": [float(o2_psi_roll5)],
        "temp_f_roll5": [float(temp_f_roll5)],
        "o2_psi_x_pct": [float(o2_psi_x_pct)],
    })

    pred_idx   = int(model.predict(feature_vector)[0])
    proba      = model.predict_proba(feature_vector)[0].tolist()
    risk_label = LEVEL_NAMES.get(pred_idx, "UNKNOWN")
    risk_info  = RISK_COLORS.get(risk_label, {})

    flame_info = compute_flame_physics(
        phase=int(inp.phase),
        o2_pct=float(inp.o2_pct),
        o2_psi=float(inp.o2_psi),
        temp_f=float(inp.temp_f),
        hazard_type=int(inp.hazard_type),
        is_alert=int(inp.is_alert)
    )

    return {
        "prediction": {
            "risk_level":   risk_label,
            "class_index":  pred_idx,
            "confidence":   round(max(proba) * 100, 2),
            "color_hex":    risk_info.get("hex", "#888"),
            "rpn_range":    risk_info.get("rpn_range", "?"),
            "action":       risk_info.get("action", "")
        },
        "flame_physics": flame_info,
        "probabilities": {
            LEVEL_NAMES[i]: round(p * 100, 2) for i, p in enumerate(proba)
        },
        "input_decoded": {
            "phase_name":   PHASE_NAMES.get(inp.phase, "Unknown"),
            "hazard_name":  HAZARD_NAMES.get(inp.hazard_type, "Unknown"),
            "met_hhmm":     f"{int(inp.met_h):03d}:{int((inp.met_h % 1)*60):02d}"
        },
        "model_info": {
            "name":         "XGBoostClassifier",
            "database":     os.path.basename(DATA_PATH),
            "trained_on":   "Apollo 13 NASA MSC-02680 Telemetry (6000 points)",
            "accuracy":     "~95%",
            "features":     14
        }
    }


@app.get("/schema")
def schema():
    return {
        "database": os.path.basename(DATA_PATH),
        "phases": PHASE_NAMES,
        "hazard_types": HAZARD_NAMES,
        "risk_levels": RISK_COLORS,
        "feature_importances": {
            "phase": 0.4219,
            "o2_psi": 0.2041,
            "met_h": 0.1850,
            "o2_psi_roll5": 0.0416,
            "o2_psi_x_pct": 0.0413
        }
    }


@app.get("/{filename:path}")
def get_static_file(filename: str):
    p = os.path.join(BASE, filename)
    if os.path.isfile(p):
        return FileResponse(p)
    raise HTTPException(status_code=404, detail=f"File {filename} not found")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8787))
    uvicorn.run("api_server:app", host="0.0.0.0", port=port)
