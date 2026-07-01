import xml.etree.ElementTree as ET
import pandas as pd
import re

# ===================================================
# File
# ===================================================
input_kml = "isobath_batam_rnd.kml"
output_csv = "isobath_batam_rnd.csv"

# ===================================================
# Namespace KML
# ===================================================
ns = {"kml": "http://www.opengis.net/kml/2.2"}

# ===================================================
# Fungsi konversi nama menjadi depth
# ===================================================
def get_depth(name):

    text = str(name).strip().replace(" ", "").lower()

    # Hilangkan huruf m
    text = text.replace("m", "")

    # -------------------------------
    # Pulau / darat
    # contoh:
    # 0--2
    # 2--4
    # 4--6
    # -------------------------------
    if "--" in text:

        nums = re.findall(r"\d+\.?\d*", text)

        if len(nums) >= 2:
            return -(float(nums[0]) + float(nums[1])) / 2

        elif len(nums) == 1:
            return -float(nums[0])

    # -------------------------------
    # Laut
    # contoh:
    # 30-32
    # 32-34
    # -------------------------------
    else:

        nums = re.findall(r"\d+\.?\d*", text)

        if len(nums) >= 2:
            return (float(nums[0]) + float(nums[1])) / 2

        elif len(nums) == 1:
            return float(nums[0])

    return None


# ===================================================
# Baca KML
# ===================================================
tree = ET.parse(input_kml)
root = tree.getroot()

rows = []
component_id = 1

for placemark in root.findall(".//kml:Placemark", ns):

    # -----------------------------------
    # Ambil Name
    # -----------------------------------
    name_element = placemark.find("kml:name", ns)

    if name_element is None or name_element.text is None:
        continue

    depth = get_depth(name_element.text)

    # -----------------------------------
    # Ambil Coordinates
    # -----------------------------------
    coord_element = placemark.find(".//kml:coordinates", ns)

    if coord_element is None or coord_element.text is None:
        continue

    coordinates = coord_element.text.strip().split()

    points = []

    for coord in coordinates:

        values = coord.split(",")

        if len(values) < 2:
            continue

        lon = float(values[0])
        lat = float(values[1])

        points.append((lat, lon))

    # Hilangkan titik terakhir jika sama dengan titik pertama
    if len(points) > 1 and points[0] == points[-1]:
        points.pop()

    # Simpan semua titik
    for lat, lon in points:

        rows.append({
            "ComponentId": component_id,
            "Latitude": lat,
            "Longitude": lon,
            "Depth": depth
        })

    component_id += 1


# ===================================================
# Simpan CSV
# ===================================================
df = pd.DataFrame(rows)

df.to_csv(output_csv, index=False)

print("--------------------------------")
print(df.head())
print("--------------------------------")
print("Jumlah Polygon :", component_id - 1)
print("Jumlah Titik   :", len(df))
print("Output         :", output_csv)