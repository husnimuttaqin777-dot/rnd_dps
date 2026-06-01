import requests
import numpy as np
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from shapely.geometry import Point, Polygon

# ── ZONE: boundary polygon (lat, lon pairs) ──────────────────────
# batam zone
#zone_lat = [1.155785, 1.157534, 1.156945, 1.151677, 1.143302, 1.138111, 1.148528,  1.150386]
#zone_lon = [103.893489, 103.894979, 103.897982, 103.914801, 103.920651, 103.917728, 103.909467, 103.89597]
zone_lat = [  1.164710,   1.145767,   1.135914, 1.148309]
zone_lon = [103.893515, 103.924360, 103.919063, 103.895587]

#dumai zone
#zone_lat = [  2.184700,2.198996 ,1.597706,  1.502657]
#zone_lon = [101.151556,101.769137 ,102.024259, 101.086208]

#mendol zone
#zone_lat = [  0.527778, 0.557133, 0.528286, 0.502838]
#zone_lon = [103.254513, 103.298757, 103.315467, 103.266529]


# ── HOW MANY POINTS inside the zone ──────────────────────────────
n_points = 20   # ← change this number
# ─────────────────────────────────────────────────────────────────


def generate_points_in_zone(zone_lat, zone_lon, n_points):
    """Fill a polygon zone with n_points using a grid, keeping only points inside."""
    polygon = Polygon(zip(zone_lon, zone_lat))  # shapely uses (lon, lat)

    # bounding box of the zone
    lat_min, lat_max = min(zone_lat), max(zone_lat)
    lon_min, lon_max = min(zone_lon), max(zone_lon)

    # build a grid dense enough to yield at least n_points inside
    # oversample by factor of 3 to account for points outside the polygon
    side = int(np.ceil(np.sqrt(n_points * 3)))
    lat_grid = np.linspace(lat_min, lat_max, side)
    lon_grid = np.linspace(lon_min, lon_max, side)

    inside = []
    for lat in lat_grid:
        for lon in lon_grid:
            if polygon.contains(Point(lon, lat)):
                inside.append((lat, lon))

    # if we got more than needed, subsample evenly
    if len(inside) > n_points:
        idx = np.round(np.linspace(0, len(inside) - 1, n_points)).astype(int)
        inside = [inside[i] for i in idx]

    print(f"Zone filled: {len(inside)} points generated (requested {n_points})")
    return inside


# ── Generate coords ───────────────────────────────────────────────
coords = generate_points_in_zone(zone_lat, zone_lon, n_points)
total  = len(coords)

# ── CSV cleanup ───────────────────────────────────────────────────
filename = "sea_current_now.csv"
if os.path.exists(filename):
    os.remove(filename)
    print("csv lama dihapus")
else:
    print("csv belum ada")


from datetime import datetime
import requests

def fetch(lat, lon):

    url = (
        f"https://marine-api.open-meteo.com/v1/marine?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=ocean_current_velocity,ocean_current_direction"
        f"&forecast_days=1"
        f"&timezone=Asia/Jakarta"
    )

    r = requests.get(url, timeout=5)

    data = r.json()

    hourly = data["hourly"]

    times = hourly["time"]

    current_time = datetime.now().strftime(
        "%Y-%m-%dT%H:00"
    )

    try:

        idx = times.index(current_time)

    except ValueError:

        idx = 0
        print(
            f"time {current_time} not found, fallback idx 0"
        )

    return {

        "latitude": lat,

        "longitude": lon,

        "time": times[idx],

        "sea_current_speed":
            hourly[
                "ocean_current_velocity"
            ][idx],

        "direction":
            hourly[
                "ocean_current_direction"
            ][idx],

    }


rows = []
done = 0

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(fetch, lat, lon): (lat, lon) for lat, lon in coords}
    for future in as_completed(futures):
        lat, lon = futures[future]
        #done += 1
        try:
            rows.append(future.result())
            print(f"Request {done}/{total} OK")
        except Exception as e:
            print(f"ERROR {lat:.4f} {lon:.4f} — {e}")







df = pd.DataFrame(rows)
df.to_csv(filename, index=False)
print("saved:", filename)
print(df.head())


