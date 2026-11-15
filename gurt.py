import json
import sys
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.utils.class_weight import compute_sample_weight

JSON_PATH = sys.argv[1] if len(sys.argv) > 1 else "apollo13_fire_risk_simulation.json"

# Set True to also give the model severity/likelihood. RPN = severity * likelihood,
# so the zone becomes trivially predictable and the model learns almost nothing.
INCLUDE_LEAKY_FEATURES = False

ZONES = [("GREEN", 1, 4), ("YELLOW", 5, 9), ("ORANGE", 10, 15), ("RED", 16, 20)]
ZONE_ORDER = [z[0] for z in ZONES]


def rpn_to_zone(rpn):
    for name, lo, hi in ZONES:
        if lo <= rpn <= hi:
            return name
    return "RED" if rpn > 20 else "GREEN"


def find_data_array(obj, min_len=100):
    """Recursively find the largest list of dicts (the simulated time series)."""
    best = None
    if isinstance(obj, dict):
        for v in obj.values():
            cand = find_data_array(v, min_len)
            if cand is not None and (best is None or len(cand) > len(best)):
                best = cand
    elif isinstance(obj, list):
        if len(obj) >= min_len and all(isinstance(x, dict) for x in obj[:10]):
            best = obj
        else:
            for v in obj:
                cand = find_data_array(v, min_len)
                if cand is not None and (best is None or len(cand) > len(best)):
                    best = cand
    return best


def pick_col(df, candidates, contains=None):
    lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower:
            return lower[cand]
    if contains:
        for c in df.columns:
            if any(s in c.lower() for s in contains):
                return c
    return None


# ---------------------------------------------------------------- load
with open(JSON_PATH, "r") as f:
    raw = json.load(f)

records = find_data_array(raw)
if records is None:
    raise ValueError(
        "Could not find the simulated data array (expected ~2000 dict records). "
        "Make sure the full JSON, including the data points array, is provided."
    )

df = pd.json_normalize(records)  # flattens nested sensor readings, e.g. sensors.o2_pressure
print(f"Loaded {len(df)} data points, columns: {list(df.columns)}")

mission_phases = raw.get("mission_phases", []) if isinstance(raw, dict) else []

# ---------------------------------------------------------------- columns
met_col = pick_col(df, ["met_hours", "met", "mission_elapsed_time"], contains=["met"])
rpn_col = pick_col(df, ["rpn", "risk_priority_number", "risk_score"], contains=["rpn"])
zone_col = pick_col(df, ["risk_zone", "zone", "risk_level", "risk_category"],
                    contains=["zone", "risk_level", "risk_cat"])
sev_col = pick_col(df, ["severity", "severity_level"], contains=["severity"])
lik_col = pick_col(df, ["likelihood", "likelihood_level"], contains=["likelihood"])
type_col = pick_col(df, ["fire_type", "fire_hazard_type", "hazard_type"],
                    contains=["fire_type", "hazard"])
phase_col = pick_col(df, ["phase", "mission_phase", "phase_name"], contains=["phase"])

# ---------------------------------------------------------------- target
if zone_col is not None:
    y_raw = df[zone_col].astype(str).str.upper()
elif rpn_col is not None:
    y_raw = df[rpn_col].astype(float).round().astype(int).map(rpn_to_zone)
elif sev_col is not None and lik_col is not None:
    y_raw = (df[sev_col] * df[lik_col]).astype(int).map(rpn_to_zone)
else:
    raise ValueError("No risk zone / RPN / severity+likelihood columns found to build a target.")

# keep zones in natural order so class indices are ordinal (GREEN < YELLOW < ORANGE < RED)
present = [z for z in ZONE_ORDER if z in set(y_raw)]
le = LabelEncoder().fit(present)
y = le.transform(y_raw)
print("Class distribution:\n", y_raw.value_counts().reindex(present))

# ---------------------------------------------------------------- features
drop_cols = {c for c in [zone_col, rpn_col] if c}
if not INCLUDE_LEAKY_FEATURES:
    drop_cols |= {c for c in [sev_col, lik_col] if c}
X = df.drop(columns=list(drop_cols))

# derive mission phase from MET when not already a column
if phase_col is None and met_col is not None and mission_phases:
    def phase_of(t):
        for p in mission_phases:
            if p["start"] <= t < p["end"]:
                return p["phase_code"]
        return mission_phases[-1]["phase_code"]
    X["phase_code"] = df[met_col].astype(float).apply(phase_of)

# time-derived features
if met_col is not None:
    t = df[met_col].astype(float)
    X["met_frac"] = t / t.max()
    X["met_delta"] = t.diff().fillna(0)

# drop non-informative columns (ids, timestamps as strings)
for c in list(X.columns):
    if "id" == c.lower() or c.lower().endswith("_id") or "timestamp" in c.lower():
        X = X.drop(columns=c)

# encode categoricals natively for XGBoost; coerce everything else to numeric
for c in X.columns:
    if X[c].dtype == object or str(X[c].dtype).startswith("string") or X[c].dtype == bool:
        if X[c].nunique() <= 50:
            X[c] = X[c].astype("category")
        else:
            X[c] = pd.to_numeric(X[c], errors="coerce")

print(f"Features used: {list(X.columns)}")

# ---------------------------------------------------------------- split
strat = y if np.min(np.bincount(y)) >= 2 else None
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=strat
)
X_tr, X_val, y_tr, y_val = train_test_split(
    X_train, y_train, test_size=0.15, random_state=42,
    stratify=y_train if np.min(np.bincount(y_train)) >= 2 else None,
)

# rare classes (RED) are heavily outnumbered, so weight them up
w_tr = compute_sample_weight("balanced", y_tr)

# ---------------------------------------------------------------- model
n_classes = len(le.classes_)
params = dict(
    n_estimators=600,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.85,
    colsample_bytree=0.85,
    min_child_weight=1,
    reg_lambda=1.0,
    tree_method="hist",
    enable_categorical=True,
    early_stopping_rounds=30,
    random_state=42,
    n_jobs=-1,
)
if n_classes > 2:
    model = xgb.XGBClassifier(objective="multi:softprob", num_class=n_classes,
                              eval_metric="mlogloss", **params)
else:
    model = xgb.XGBClassifier(objective="binary:logistic", eval_metric="logloss", **params)

model.fit(X_tr, y_tr, sample_weight=w_tr, eval_set=[(X_val, y_val)], verbose=False)
print(f"Best iteration: {model.best_iteration}")

# ---------------------------------------------------------------- evaluate
pred = model.predict(X_test)
print(f"\nTest accuracy: {accuracy_score(y_test, pred):.4f}\n")
print(classification_report(y_test, pred, labels=range(n_classes),
                            target_names=le.classes_, zero_division=0))
print("Confusion matrix (rows = true, cols = predicted):")
print(pd.DataFrame(confusion_matrix(y_test, pred, labels=range(n_classes)),
                   index=le.classes_, columns=le.classes_))

# ---------------------------------------------------------------- importance
imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nTop feature importances:")
print(imp.head(15))

# ---------------------------------------------------------------- save
model.save_model("apollo13_fire_risk_xgb.json")
print("\nSaved model to apollo13_fire_risk_xgb.json")