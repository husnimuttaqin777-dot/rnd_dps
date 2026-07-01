import pandas as pd
import numpy as np

# ─── CONFIG ───────────────────────────────────────────────────────────────────
INPUT_FILE  = "isobath_batam_rnd.csv"
OUTPUT_FILE = "isobath_batam_rnd_xy.csv"
XY_RANGE    = 1000          # output range: -XY_RANGE to +XY_RANGE
# ──────────────────────────────────────────────────────────────────────────────

df = pd.read_csv(INPUT_FILE)

# Hitung titik tengah area
lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
lat_center = (lat_min + lat_max) / 2
lon_center = (lon_min + lon_max) / 2

# Konversi derajat ke meter (dengan koreksi kosinus untuk longitude)
lat_m_per_deg = 111320
lon_m_per_deg = 111320 * np.cos(np.radians(lat_center))

# Offset meter relatif terhadap pusat
df['x_m'] = (df['Longitude'] - lon_center) * lon_m_per_deg
df['y_m'] = (df['Latitude']  - lat_center) * lat_m_per_deg

# Scale ke range -XY_RANGE..+XY_RANGE (aspek rasio terjaga)
max_extent_m = max(
    (lon_max - lon_min) * lon_m_per_deg,
    (lat_max - lat_min) * lat_m_per_deg
) / 2

scale = XY_RANGE / max_extent_m          # px/m
meters_per_pixel = 1 / scale             # m/px

df['x'] = (df['x_m'] * scale).round().astype(int)
df['y'] = (df['y_m'] * scale).round().astype(int)
df['depth'] = -df['Depth']

# Simpan output
out = df[['x', 'y', 'depth']]
out.to_csv(OUTPUT_FILE, index=False)

print(f"Center       : {lat_center:.6f}°N, {lon_center:.6f}°E")
print(f"Scale        : {scale:.6f} px/m")
print(f"Meter/pixel  : {meters_per_pixel:.4f} m/px")
print(f"X range      : {df['x'].min()} to {df['x'].max()}")
print(f"Y range      : {df['y'].min()} to {df['y'].max()}")
print(f"Total rows   : {len(out)}")
print(f"Output saved : {OUTPUT_FILE}")