import requests
import numpy as np
import pandas as pd
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
from shapely.geometry import Point, Polygon

from datetime import datetime
from zoneinfo import ZoneInfo


# ===================== ZONE =====================

zone_lat = [
    1.164710,
    1.145767,
    1.135914,
    1.148309
]

zone_lon = [
    103.893515,
    103.924360,
    103.919063,
    103.895587
]

n_points = 30


# ===================== GENERATE POINTS =====================

def generate_points_in_zone(
    zone_lat,
    zone_lon,
    n_points
):

    polygon = Polygon(

        zip(
            zone_lon,
            zone_lat
        )
    )

    lat_min = min(zone_lat)
    lat_max = max(zone_lat)

    lon_min = min(zone_lon)
    lon_max = max(zone_lon)

    side = int(

        np.ceil(

            np.sqrt(
                n_points * 3
            )
        )
    )

    lat_grid = np.linspace(
        lat_min,
        lat_max,
        side
    )

    lon_grid = np.linspace(
        lon_min,
        lon_max,
        side
    )

    inside = []

    for lat in lat_grid:

        for lon in lon_grid:

            if polygon.contains(

                Point(
                    lon,
                    lat
                )
            ):

                inside.append(

                    (
                        lat,
                        lon
                    )
                )

    if len(inside) > n_points:

        idx = np.round(

            np.linspace(

                0,
                len(inside)-1,
                n_points

            )

        ).astype(int)

        inside = [

            inside[i]

            for i in idx
        ]

    print(

        f"Zone filled: "

        f"{len(inside)} points"

    )

    return inside


# ===================== PREPARE =====================

coords = generate_points_in_zone(

    zone_lat,
    zone_lon,
    n_points
)

total = len(coords)

filename = "sea_current_now.csv"

if os.path.exists(filename):

    os.remove(filename)

    print(
        "csv lama dihapus"
    )

else:

    print(
        "csv belum ada"
    )


# ===================== FETCH =====================

def fetch(lat, lon):

    url = (

        f"https://marine-api.open-meteo.com/v1/marine?"

        f"latitude={lat}"

        f"&longitude={lon}"

        f"&hourly="

        f"ocean_current_velocity,"

        f"ocean_current_direction"

        f"&forecast_days=1"

        f"&timezone=Asia/Jakarta"
    )

    try:

        r = requests.get(

            url,

            timeout=10
        )

        data = r.json()

        hourly = data["hourly"]

        times = hourly["time"]

        # paksa WIB
        current_time = datetime.now(

            ZoneInfo(
                "Asia/Jakarta"
            )

        ).replace(

            minute=0,

            second=0,

            microsecond=0
        )

        api_times = []

        for t in times:

            api_times.append(

                datetime.strptime(

                    t,

                    "%Y-%m-%dT%H:%M"

                ).replace(

                    tzinfo=

                    ZoneInfo(

                        "Asia/Jakarta"
                    )
                )
            )

        idx = min(

            range(

                len(api_times)
            ),

            key=lambda i:

            abs(

                api_times[i]

                -

                current_time
            )
        )

        print(

            f"{lat:.4f},"

            f"{lon:.4f}"

            f" -> "

            f"{times[idx]}"
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

    except Exception as e:

        print(

            f"ERROR "

            f"{lat:.4f} "

            f"{lon:.4f}"

            f" {e}"
        )

        return {

            "latitude": lat,

            "longitude": lon,

            "time": None,

            "sea_current_speed": None,

            "direction": None
        }


# ===================== MULTITHREAD =====================

rows = []

done = 0

with ThreadPoolExecutor(

    max_workers=20

) as executor:

    futures = {

        executor.submit(

            fetch,

            lat,

            lon

        ):

        (

            lat,

            lon

        )

        for lat, lon in coords
    }

    for future in as_completed(

        futures
    ):

        done += 1

        try:

            rows.append(

                future.result()
            )

            print(

                f"Request "

                f"{done}"

                f"/"

                f"{total}"

                f" OK"
            )

        except Exception as e:

            print(e)


# ===================== SAVE =====================

df = pd.DataFrame(rows)

df.to_csv(

    filename,

    index=False
)

print(

    "saved:",

    filename
)

print(

    df.head()
)