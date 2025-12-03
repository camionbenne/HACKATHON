import pandas as pd
import numpy as np

# -----------------------------------------------------
# 1) Charger les données (TON FICHIER FINAL)
# -----------------------------------------------------
csv_path = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_wgs_with_social.csv"
df = pd.read_csv(csv_path)

# -----------------------------------------------------
# 2) Définition des classes LCZ (officielles)
# -----------------------------------------------------
LCZ_MAP = {
    1: "Compact high-rise",
    2: "Compact mid-rise",
    3: "Compact low-rise",
    4: "Open high-rise",
    5: "Open mid-rise",
    6: "Open low-rise",
    7: "Large low-rise",
    8: "Sparsely built",
    9: "Dense trees",
    10: "Scattered trees",
    11: "Bush / scrub",
    12: "Low plants",
    13: "Bare soil or sand",
    14: "Bare rock or paved",
    15: "Water"
}

BUILT_COLS = [
    "Compact high-rise",
    "Compact mid-rise",
    "Compact low-rise",
    "Open high-rise",
    "Open mid-rise",
    "Open low-rise",
    "Large low-rise",
    "Sparsely built",
]

LAND_COLS = [
    "Dense trees",
    "Scattered trees",
    "Bush / scrub",
    "Low plants",
    "Bare soil or sand",
    "Bare rock or paved",
    "Water",
]

# -----------------------------------------------------
# 3) Construire les colonnes score_built et score_land
# -----------------------------------------------------
df["score_built"] = 0.0
df["score_land"] = 0.0

for lcz_id, name in LCZ_MAP.items():
    colname = f"prop_lcz_{lcz_id}"
    if colname not in df.columns:
        continue

    if name in BUILT_COLS:
        df["score_built"] += df[colname]

    if name in LAND_COLS:
        df["score_land"] += df[colname]

# -----------------------------------------------------
# 4) Normalisation helper
# -----------------------------------------------------
def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

# -----------------------------------------------------
# 5) Normaliser toutes les composantes
# -----------------------------------------------------
df["built_norm"] = normalize(df["score_built"])
df["land_norm"] = normalize(df["score_land"])

df["dist_fresh_norm"] = normalize(
    (df["dist_green_m_mean"] + df["dist_water_m_mean"]) / 2
)

df["dist_sensitive_norm"] = normalize(
    (df["dist_hospital_m_mean"] + df["dist_school_m_mean"]) / 2
)

# Social variables
df["elderly_norm"] = normalize(df["prop_elderly"])
df["low_income_norm"] = normalize(df["prop_low_income"])

# -----------------------------------------------------
# 6) Formule de vulnérabilité (modulable)
# -----------------------------------------------------
df["vulnerability_index"] = (
    0.25 * df["built_norm"] +
    0.15 * df["land_norm"] +
    0.20 * df["dist_fresh_norm"] +
    0.20 * df["dist_sensitive_norm"] +
    0.10 * df["elderly_norm"] +
    0.10 * df["low_income_norm"]
)

df["vulnerability_index"] = normalize(df["vulnerability_index"])

# -----------------------------------------------------
# 7) Sauvegarde du fichier final
# -----------------------------------------------------
output = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_with_vuln.csv"
df.to_csv(output, index=False)

print("✔ Fichier exporté :", output)
print(df[["tile_id", "vulnerability_index"]].head())
